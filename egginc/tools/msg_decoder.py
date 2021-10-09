import atexit
import common_pb2
import ei_pb2 as egg
import endpoints
import json
import re

from base64 import b64decode, b64encode
from google.protobuf import json_format
from google.protobuf.message import DecodeError
from http import HTTPStatus

EGGINC_APPSPOT_HOST = "afx-2-dot-auxbrainhome.appspot.com"

output_data = []
output_file = open('decoded.json', 'w')

def sanitize(data):
    for k, v in data.items():
        if isinstance(v, dict):
            data[k] = sanitize(v)

        if isinstance(v, bytes):
            data[k] = v.hex()

    return data

def on_exit():
    for idx, item in enumerate(output_data):
        output_data[idx] = sanitize(item)

    output_file.write(json.dumps(output_data, indent = 4))
    output_file.close()

atexit.register(on_exit)
endpoints.register_endpoints()

def hexdump_data(data, width):
    d, m = divmod(len(data), width)
    chunks = []

    for i in range(d):
        chunks.append(data[i * width : (i + 1) * width].hex())

    if m:
        chunks.append(data[d * width:].hex())

    for idx, chunk in enumerate(chunks):
        c_row = chunks[idx]
        n_row = ''

        for i in range(0, len(c_row), 2):
            n_row += ' ' + c_row[i : i + 2]

        chunks[idx] = n_row.strip()

    return chunks

# https://stackoverflow.com/a/45928164
def is_b64(data):
    try:
        return b64encode(b64decode(data)) == data
    except:
        return False

def process_req(transaction, request):
    if request['_body'] == '0':
        return {'msg': 'empty body'}

    req_content = re.sub('^data=', '', request['body']['__cdata'], count = 1)

    if not is_b64(req_content.encode('utf-8')):
        return {'msg': req_content}

    decoded_data = bytearray(b64decode(req_content))
    decoded_req = {'raw_data': hexdump_data(decoded_data, 8)}

    endpoint = endpoints.from_path(transaction['_path'])
    req = endpoint['req']
    msg = req['msg']()

    if req['authenticated']:
        msg = egg.AuthenticatedMessage()
    
    try:
        msg.ParseFromString(bytes(decoded_data))

        if req['authenticated']:
            decoded_req['auth_code'] = msg.code

            encoded_data = msg.message
            msg = req['msg']()

            msg.ParseFromString(encoded_data)
    except DecodeError as err:
        return {'raw_data': decoded_req['raw_data'], 'msg': 'failed to parse decoded data: %s' % str(err)}

    decoded_req['decoded'] = json_format.MessageToDict(msg)

    return decoded_req

def process_rsp(transaction, response):
    if int(response['_status']) >= HTTPStatus.BAD_REQUEST:
        return {'msg': 'server returned error. response: %s' % response['body']['__cdata']}

    if response['_body'] == '0':
        return {'msg': 'empty body'}

    rsp_content = response['body']['__cdata']

    if not is_b64(rsp_content.encode('utf-8')):
        return {'msg': rsp_content}

    decoded_data = bytearray(b64decode(rsp_content))
    decoded_rsp = {'raw_data': hexdump_data(decoded_data, 8)}

    endpoint = endpoints.from_path(transaction['_path'])
    rsp = endpoint['rsp']
    msg = rsp['msg']()

    if rsp['authenticated']:
        msg = egg.AuthenticatedMessage()
    
    try:
        msg.ParseFromString(bytes(decoded_data))

        if rsp['authenticated']:
            decoded_rsp['auth_code'] = msg.code

            encoded_data = msg.message
            msg = rsp['msg']()

            msg.ParseFromString(encoded_data)
    except DecodeError as err:
        return {'raw_data': decoded_rsp['raw_data'], 'msg': 'failed to parse decoded data: %s' % str(err)}

    decoded_rsp['decoded'] = json_format.MessageToDict(msg)

    return decoded_rsp

def main():
    session_json = None
    tcount = 0

    with open('egg.json', 'r') as session:
        session_json = json.loads(session.read())['charles-session']

    for transaction in session_json['transaction']:
        if transaction['_host'] != EGGINC_APPSPOT_HOST:
            continue

        if not endpoints.check_endpoint(transaction['_path']):
            print("[ - ] Unknown endpoint encountered.")
            print("[ - ] Endpoint: %s" % transaction['_path'])

            continue

        print("[ + ] %s" % transaction['_path'])

        output_data.append(
            {
                'location': transaction['_path'],
                'request': process_req(transaction, transaction['request']),
                'response': process_rsp(transaction, transaction['response'])
            }
        )

        tcount += 1

    print("[ + ] Wrote %d decoded transactions to ./decoded.json" % tcount)

main()