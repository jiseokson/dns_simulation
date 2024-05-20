import threading

from config import config
import cache
import flag
import resolver

from regex import cache_command

if __name__ == '__main__':
    rrcache = cache.Cache()
    rrcache.add_rr(cache.RR('', config.root.name, 'NS'))
    rrcache.add_rr(cache.RR(config.root.name, config.root.ip, 'A'))
    recur_flag = flag.Flag(True)

    worker_thread = threading.Thread( \
        target=resolver.resolver, \
        args=[rrcache, recur_flag, True, config.local.server, config.local.port])
    worker_thread.start()

    while True:
        prompt = input('>>> ')
        if match := cache_command.match(prompt):
            rrcache.logs()
