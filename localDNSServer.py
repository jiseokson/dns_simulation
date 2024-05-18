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
            recevied_query_bytes, address = udp_socket.recvfrom(4092)
            recevied_query = message.decode(recevied_query_bytes)
            reply = recevied_query.copy()

            rrs, is_resolved = rrcache.resolve(recevied_query.name)
            while True:
                if is_resolved:
                    reply.add_answer(*rrs)
                    break
                
                query = reply.to_query()
                ns_ip, is_ns_resolved = cache.find_ns_ip(rrs, recevied_query.name)
                if not is_ns_resolved:
                    break

                query.add_log(config.local.server)
                udp_socket.sendto(query.encode(), ('', config.resolve_port(ns_ip)))

                reply_bytes, _ = udp_socket.recvfrom(4092)
                reply = message.decode(reply_bytes)

                rrcache.append(*reply.answer)
                rrs, is_resolved = rrcache.resolve(recevied_query.name)
                _, is_resolved = cache.find_a_ip(rrs, query.name)
                    
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
