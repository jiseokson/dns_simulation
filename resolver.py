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

            querying = True
            qname = recevied_query.name
            is_query_from_root = (config.root.port == address[1])

            # Cache resolve
            answer, authority, additional = rrcache.resolve(qname)
            if answer or \
                not recevied_query.recur_desire or \
                not (recur_flag.value or is_query_from_root):
                reply.sections = answer, authority, additional
                querying = False

            # Querying
            while querying:
                ns_ip = cache.resolve_ip(qname, 'NS', answer, authority, additional)
                if not ns_ip:
                    break

                query = reply.copy_to_query()
                query.recur_desire = True
                query.add_log(server)

                udp_socket.sendto(query.encode(), ('', config.resolve_port(ns_ip)))
                reply_bytes, _ = udp_socket.recvfrom(4092)
                reply = message.decode(reply_bytes)
                answer, authority, additional = reply.sections

                if is_caching:
                    rrcache.add_rr(answer, authority, additional)

                if answer:
                    break

            reply.add_log(server)
            udp_socket.sendto(reply.encode(), address)
