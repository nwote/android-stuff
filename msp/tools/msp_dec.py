import base64
import sys
import struct

from Crypto.Cipher import AES
from io import BytesIO, BufferedReader

aes_key = base64.b64decode("ypOiwAB4vKEF5EYDvTC8Yw==")
enc_obj = AES.new(aes_key, AES.MODE_CTR)

class MSPEncryption(object):
    def __init__(self, stream):
        self._buf = BufferedReader(BytesIO(stream.read()))
        self._output_buf = bytearray()

        self.f144e = None
        self.f146g = 0
        self.f147h = b''

    def get_output(self):
        return bytes(self._output_buf)

    def decrypt(self):
        self.f146g = struct.unpack(">I", self._buf.read(4))[0]
        self.f147h = struct.unpack("B", self._buf.read(1))[0]
        self.f144e = bytearray()

        if self.f147h == 1:
            self.f144e.extend(
                struct.unpack("%dB" % self.f146g, self._buf.read(self.f146g))
            )

            self.f144e = bytearray(
                enc_obj.decrypt(self.f144e)
            )
        else:
            self.f144e.extend(
                struct.unpack("%dB" % self.f146g, self._buf.read(self.f146g))
            )

            self._buf.read(4)

        self._output_buf.extend(self.f144e)

        if len(self._buf.peek()) > 0:
            self.decrypt()

def main():
    with open(sys.argv[1], 'rb') as msp_file:
        msp = MSPEncryption(msp_file)

        msp.decrypt()

        sys.stdout.buffer.write(msp.get_output())

main()