import sys
import re
import socket
import threading

from config import config
import cache
import message
import flag

def worker(rrcache: cache.Cache, recur_flag: flag.Flag, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(('', port))
        while True:
            recevied_query_bytes, address = udp_socket.recvfrom(4092)
            recevied_query = message.decode(recevied_query_bytes)
            reply = recevied_query.copy()

            #############################

            reply.add_log(config.root.server)
            udp_socket.sendto(reply.encode(), address)

if __name__ == '__main__':
    rrcache = cache.Cache()
    rrcache.append(*config.all_company_dns())
    recur_flag = flag.Flag(False)
    cache_pattern = re.compile(r'^\s*cache\s*$')
    recur_flag_pattern = re.compile(r'^\s*recursiveFlag\s+(on|off)\s*$')
    worker_thread = threading.Thread(target=worker, args=[rrcache, recur_flag, config.comtld.port])
    worker_thread.start()
    while True:
        prompt = input('>>> ')
        if match := cache_pattern.match(prompt):
            rrcache.logs()
        elif match := recur_flag_pattern.match(prompt):
            command = match.group(1)
            match command:
                case 'on':
                    recur_flag.set(False)
                case 'off':
                    recur_flag.set(True)
