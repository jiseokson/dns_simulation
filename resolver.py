import socket

from config import config
import cache
import message

import flag

def resolver(rrcache: cache.Cache, recur_flag: flag.Flag, is_caching: bool, server: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(('', port))
        while True:
            recevied_query_bytes, address = udp_socket.recvfrom(4092)
            recevied_query = message.decode(recevied_query_bytes)
            reply = recevied_query.copy()

            is_query_from_root = (config.root.port == address[1])
            querying = True

            # Cache resolve
            rrs, is_resolved = rrcache.resolve(recevied_query.name)
            if is_resolved or \
                not recevied_query.recur_desire or \
                not (recur_flag.value or is_query_from_root):
                reply.add_answer(*rrs)
                querying = False

            # Querying
            while querying:
                ns_ip, is_ns_resolved = cache.resolve_ip(rrs, recevied_query.name, 'NS')
                if not is_ns_resolved:
                    break

                query = reply.copy_to_query()
                query.recur_desire = recur_flag.value or is_query_from_root
                query.add_log(server)

                udp_socket.sendto(query.encode(), ('', config.resolve_port(ns_ip)))
                reply_bytes, _ = udp_socket.recvfrom(4092)
                reply = message.decode(reply_bytes)
                rrs = reply.answer

                if is_caching:
                    rrcache.append(*rrs)

                rrchaine, is_resolved = cache.resolve(rrs, recevied_query.name)
                if is_resolved:
                    reply.add_answer(*rrchaine)

            reply.add_log(server)
            udp_socket.sendto(reply.encode(), address)
