import sys
import re
import socket
import threading

from config import config
import cache
import message

import flag

def worker(rrcache: cache.Cache, recur_flag: flag.Flag, server: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(('', port))
        while True:
            recevied_query_bytes, address = udp_socket.recvfrom(4092)
            recevied_query = message.decode(recevied_query_bytes)
            reply = recevied_query.copy()

            while True:
                rrs, is_resolved = rrcache.resolve(recevied_query.name)
                if is_resolved or not (recur_flag.value or config.root.ip == address[1]):
                    reply.add_answer(*rrs)
                    break

                query = reply.to_query()
                query.recur_desire = recur_flag.value
                ns_ip, is_ns_resolved = cache.resolve_ip(rrs, recevied_query.name, 'NS')
                if not is_ns_resolved:
                    break

                query.add_log(server)
                udp_socket.sendto(query.encode(), ('', config.resolve_port(ns_ip)))
                reply_bytes, _ = udp_socket.recvfrom(4092)
                reply = message.decode(reply_bytes)
                rrcache.append(*reply.answer)
                    
            reply.add_log(config.local.server)
            udp_socket.sendto(reply.encode(), address)

if __name__ == '__main__':
    rrcache = cache.Cache()
    rrcache.append(cache.RR(config.root.name, config.root.ip, 'A'))
    recur_flag = flag.Flag(True)
    pattern = re.compile(r'^\s*cache\s*$')
    worker_thread = threading.Thread(target=worker, args=[rrcache, recur_flag, config.local.server, config.local.port])
    worker_thread.start()
    while True:
        prompt = input('>>> ')
        match = pattern.match(prompt)
        if match is None: continue
        rrcache.logs()
