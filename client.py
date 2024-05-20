import sys
import socket

from config import config
import message

from regex import ipaddr_command

if __name__ == '__main__':
    port = int(sys.argv[1])
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(('', port))
        while True:
            prompt = input('>>> ')
            if match := ipaddr_command.match(prompt):
                name = match.group(1)
                query = message.query(name, recur_desire=True)
                udp_socket.sendto(query.encode(), ('', config.local.port))
                reply_bytes, _ = udp_socket.recvfrom(4092)
                reply = message.decode(reply_bytes)
                print(reply)
