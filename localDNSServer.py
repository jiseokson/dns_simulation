import sys
import re
import socket
import threading

from config import config
import cache
import message

def worker(rrcache: cache.Cache):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(('', config.local.port))
        while True:
            query_bytes, address = udp_socket.recvfrom(4092)
            query = message.decode(query_bytes)
            reply = query.copy()
            # todo: resolve 과정....
            # if rr := rrcache.resolve(query.name, 'A') is not None:
            #     reply.add_answer(rr)
            # elif rr := rrcache.resolve(~~xxx.com~~, 'NS') is not None:
            #     reply.add_answer(rr)
            # else:
            ############    
            reply.add_log(config.local.server)
            udp_socket.sendto(reply.encode(), address)

if __name__ == '__main__':
    rrcache = cache.Cache()
    rrcache.append(cache.RR(config.root.name, config.root.ip, 'A'))
    pattern = re.compile(r'^\s*cache\s*$')
    worker_thread = threading.Thread(target=worker, args=[rrcache])
    worker_thread.start()
    while True:
        prompt = input('>>> ')
        match = pattern.match(prompt)
        if match is None: continue
        rrcache.logs()
