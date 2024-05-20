import sys
import threading

from config import config
from config import extract_company
import cache
import flag
import resolver

from regex import cache_command

if __name__ == '__main__':
    filepath = sys.argv[2]
    rrcache = cache.Cache(filepath=filepath)
    recur_flag = flag.Flag(False)

    server = extract_company(filepath)
    worker_thread = threading.Thread( \
        target=resolver.resolver, \
        args=[rrcache, recur_flag, False, server, config.find_by_server(server).port])
    worker_thread.start()

    while True:
        prompt = input('>>> ')
        if match := cache_command.match(prompt):
            rrcache.logs()
