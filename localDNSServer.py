import re
import threading

from config import config
import cache
import flag
import resolver

if __name__ == '__main__':
    rrcache = cache.Cache()
    rrcache.add_rr(cache.RR(config.root.name, config.root.ip, 'A'))
    recur_flag = flag.Flag(True)

    worker_thread = threading.Thread( \
        target=resolver.resolver, \
        args=[rrcache, recur_flag, True, config.local.server, config.local.port])
    worker_thread.start()

    pattern = re.compile(r'^\s*cache\s*$')
    while True:
        prompt = input('>>> ')
        if match := pattern.match(prompt):
            rrcache.logs()
