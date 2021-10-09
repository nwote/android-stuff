import sys

from pyshark import LiveCapture

WIRELESS_ITF = 'ap0'

stream = LiveCapture(
        interface = WIRELESS_ITF,
        display_filter = 'tcp')
output_file = sys.argv[1]

# pulled from my personal private stream library :P
def hexdump(data, formatted: bool = True, col_len: int = 1, row_len: int = 16, sep: str = ' '):
    """Returns a hexdump of the underlying buffer."""

    if not formatted:
        return data.hex()

    if row_len % col_len:
        raise Exception("hexdump: col_len must be a multiple of row_len.")

    stream_data = data
    dump = ''

    last_line_len = 0

    d, m = divmod(len(stream_data), row_len)
    chunks = []

    for i in range(d):
        chunks.append(stream_data[i * row_len : (i + 1) * row_len])

    if m:
        chunks.append(stream_data[d * row_len :])

    for i in range(len(chunks)):
        row = ''

        for j, b in enumerate(chunks[i]):
            if j != 0 and j % col_len == 0:
                row += sep

            row += '%02x' % b

        if len(row) < last_line_len:
            row += ' ' * (last_line_len - len(row))

        dump += row + '    '

        last_line_len = len(row)

        for b in chunks[i]:
            if b < 0x7f and b >= 0x20:
                dump += chr(b)
            else:
                dump += '.'

        dump += '\n'

    return dump.strip()

def process_payload(load):
    bindata = bytes.fromhex(load.replace(':', ''))
    dump = "%d bytes\n" % len(bindata)

    dump += hexdump(bindata)

    return dump

def tcp_flags_of(tcp_layer):
    flags = []

    for field in tcp_layer.field_names:
        if field[:5] == 'flags':
            tcp_flag = tcp_layer.get(field)

            if tcp_flag == '1':
                flags.append(field[6:].upper())

    return ', '.join(flags)

def is_local_ip(src):
    return src[:7] == '192.168'

def create_dump_header(packet):
    dump_layers = [
        'tcp',
        'ip'
    ]

    header = ''

    if dump_layers in packet:
        layer_ip = packet.ip
        layer_tcp = packet.tcp

        # add tcp stream info
        header += 'TCP Stream #%s (seq %s -->> %s nxtseq) ' % (
            layer_tcp.stream.main_field.show,
            layer_tcp.seq.main_field.show,
            layer_tcp.nxtseq.main_field.show)
        header += '[ %s ] ' % tcp_flags_of(layer_tcp)
        header += '\n'

        # add packet direction
        if is_local_ip(layer_ip.src):
            header += '<< '
        else:
            header += '>> '

        # add packet source
        header += layer_ip.src
        header += ':'
        header += layer_tcp.srcport

        # add packet destination
        header += ' -> '
        header += layer_ip.dst
        header += ':'
        header += layer_tcp.dstport
    else:
        print("[ - ] No TCP data found!")

    return header

def main():
    with open(output_file, 'w') as output:
        for packet in stream.sniff_continuously():
            data_str = packet.transport_layer

            data_str += ' || '
            data_str += create_dump_header(packet)
            
            if packet.tcp.get('payload'):
                data_str += '\nPayload hexdump: '
                data_str += process_payload(packet.tcp.payload)

            data_str += '\n'

            print(data_str)

            data_str += '\n'

            output.write(data_str)

main()

print("\n[ + ] Shutting down...")
stream.close()
print("[ + ] Saved stream dump to '%s'." % output_file)