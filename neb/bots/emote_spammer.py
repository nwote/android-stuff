import socket
import sys
import struct
import random
import time
import re

from threading import Thread, Event

def usage():
    print("Usage: python3 emote_spammer.py <public id> <request id> <port> [-w]", file = sys.stderr)
    print("\n\t-w\tNumber of worker threads to use.")

    exit(1)

worker_threads = 2

try:
    pub_id = int(sys.argv[1], 16)
    req_id = int(sys.argv[2], 16)
    port = int(sys.argv[3])

    if len(sys.argv) > 4:
        if sys.argv[4][:3] == '-w ' and len(sys.argv[4]) > 3:
            try:
                worker_threads = int(sys.argv[4][3:])
            except ValueError:
                usage()
        else:
            usage()
except (IndexError, ValueError):
    usage()

neb_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = "45.56.113.95" # US EAST game server
emote_id = 0
hardcoded = False

neb_sock.connect((host, port))
neb_sock.shutdown(socket.SHUT_RD) # disable receiving.

def spammer(killer, w_id):
    global hardcoded
    global emote_id

    while not killer.is_set():
        emote_packet = bytearray(b'\x61')
        emote = random.randint(1, 85) if not hardcoded else emote_id

        emote_packet.extend(struct.pack('>I', pub_id))
        emote_packet.extend(struct.pack('b', emote))
        emote_packet.extend(struct.pack('>I', req_id))

        neb_sock.send(bytes(emote_packet))

    print("[ + ] Worker #%d shutting down" % w_id)

if __name__ == '__main__':
    ev = Event()
    w_threads = []

    for w in range(worker_threads):
        wt = Thread(target = spammer, args = [ev, w])

        wt.daemon = True
        wt.name = "Worker #%d" % w

        print("[ + ] Worker #%d starting..." % w)

        w_threads.append(wt)

        wt.start()

    try:
        while True:
            emote_id_bak = emote_id

            try:
                emote_id = int(re.sub('[^0-9]', '', input("[ + ] Input emote id: ")))
                hardcoded = True
            except ValueError:
                print("[ - ] Invalid ID.")

                emote_id = emote_id_bak

                continue

            if emote_id not in range(0, 85):
                print("[ - ] Invalid ID.")

                emote_id = emote_id_bak

                continue

            if emote_id == 0:
                hardcoded = False

                continue

    except KeyboardInterrupt:
        print()

        ev.set()

        for t in w_threads:
            t.join()

        neb_sock.close()

    print("[ + ] Successfully shut down.")