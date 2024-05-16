import sys
import re
import socket

from config import config
import message

if __name__ == '__main__':
    port = int(sys.argv[1])
    pattern = re.compile(r'^\s*ipaddr\s+([a-zA-Z0-9][a-zA-Z0-9\-\.]*)\s*$')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(('', port))
        while True:
            prompt = input('>>> ')
            match = pattern.match(prompt)
            if match is None: continue
            name = match.group(1)
            query = message.query(name, recur_desire=True)
            udp_socket.sendto(query.encode(), ('', config.local.port))
            reply_bytes, _ = udp_socket.recvfrom(4092)
            reply = message.decode(reply_bytes)
            print(reply)
