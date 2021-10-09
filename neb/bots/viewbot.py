import json
import os
import socket
import ssl
import sys
import threading

from argparse import ArgumentParser
from urllib.parse import urlencode as std_urlencode
from datetime import date

# constants
PROXY_LIST = os.path.join(os.path.dirname(__file__), 'proxies.json') # each proxy must be assigned a ticket
VERSION = '1.0'

HOST = '52.6.241.44'
PORT = 443

NEB_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ENDPOINT = '/api/account/GetPlayerProfile'

# ensure the proxy list is no more than 1 week fresh.
def is_fresh_enough():
    date_file = date.fromtimestamp(os.path.getmtime(PROXY_LIST))
    date_now = date.today()

    return (date_now - date_file).days <= 7

def main(args):
    if not os.path.isfile(PROXY_LIST):
        print("[ - ] No proxy list found in the project directory!", file = sys.stderr)

        try:
            open(PROXY_LIST, 'w').close()
        except OSError as e:
            print("[ ! ] Unable to create %s!" % PROXY_LIST, file = sys.stderr)
            print("[ ! ] Your OS said: %s" % e, file = sys.stderr)

            exit(1)

        print("[ + ] Created %s. Please populate this file with proxies and tickets." % PROXY_LIST,
            file = sys.stderr)
        print("[ + ] See https://github.com/neosophaux/viewbot-nebulous for more info.",
            file = sys.stderr)

        exit(1)

    NEB_SOCK = ssl.wrap_socket(NEB_SOCK, ssl_version = ssl.PROTOCOL_TLSv1_2,
        ciphers = 'ECDHE-RSA-AES256-GCM-SHA384')

    NEB_SOCK.settimeout(10)

    try:
        NEB_SOCK.connect((HOST, PORT))
    except socket.timeout:
        print("[ - ] Timed out while attempting to connect.", file = sys.stderr)
        print("[ - ] If this continues, update the script by visiting" + 
              "https://github.com/neosophaux/viewbot-nebulous", file = sys.stderr)

        exit(1)

    if not is_fresh_enough():
        print("[ - ] Your proxy list isn't fresh enough. Please update it and try again.",
            file = sys.stderr)

        exit(1)

    proxies_fobj = open(PROXY_LIST, 'r')
    proxies_data = json.loads(proxies_fobj.read())
    proxies_thrd = []

    proxies_fobj.close()

    req_headers = [
        'POST /api/account/GetAlerts HTTP/1.1',
        'Host: ' + socket.gethostbyaddr(HOST),
        'User-Agent: viewbot-nebulous/' + VERSION,
        'Content-Length: %d', # tbd.
        'Accept: */*',
        'Content-Type: application/x-www-form-urlencoded'
    ]

    for idx, proxy in enumerate(proxies_data):
        if len(proxy['address']) == 0 or len(proxy['ticket']) == 0:
            print("[ ! ] Warning: Skipping proxy #%d due to invalid configuration." % idx,
                file = sys.stderr)

            proxies_data.pop(idx)

            continue

        req_content = std_urlencode({
            'Game': 'Nebulous',
            'Version': 1087,
            'Ticket': proxy['ticket']
        })

        req_headers[3] = req_headers[3] % len(req_content)
        req_full = '\r\n'.join(req_headers) + '\r\n\r\n' + req_content

        NEB_SOCK.send(req_full.encode('utf-8'))

        resp = NEB_SOCK.recv().decode('utf-8').split('\r\n')

        if '404' in resp.split(' '):
            print("[ - ] Warning: Proxy #%d has an invalid ticket." % idx, file = sys.stderr)

            proxies_data.pop(idx)
        
        # if it didn't 404 then it returned JSON data
        resp_content = json.loads(resp[-1])

        if resp_content['Error'] is not None:
            print("[ - ] Warning: Proxy #%d has an invalid ticket." % idx, file = sys.stderr)
            print("[ - ] Nebulous said: %s" % resp_content['Error'])

        pass

def parse_args(parser):
    parser.add_argument(
        'account_id',
        help = 'The account ID to deliver the views to.',
        type = int,
        metavar = 'ID'
    )

    parser.add_argument(
        '-V', '--views',
        help = 'The amount of views to work towards.',
        type = int,
        default = 100,
        metavar = 'VIEWS'
    )

    parser.add_argument(
        '-b', '--bots',
        help = 'The number of view bots to spawn.',
        type = int,
        default = 8,
        metavar = 'COUNT'
    )

    return parser.parse_args()

main(parse_args(ArgumentParser(
    prog = 'python3 viewbot.py',
    description = 'Become a celebrity on Nebulous.io.',
    epilog = 'https://github.com/neosophaux/viewbot-nebulous'
)))