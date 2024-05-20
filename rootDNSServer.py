import re
import threading

from config import config
import cache
import flag
import resolver

if __name__ == '__main__':
    rrcache = cache.Cache()
    rrcache.add_rr(cache.RR('com', config.comtld.name, 'NS'))
    rrcache.add_rr(cache.RR(config.comtld.name, config.comtld.ip, 'A'))
    recur_flag = flag.Flag(False)

    worker_thread = threading.Thread( \
        target=resolver.resolver, \
        args=[rrcache, recur_flag, False, config.root.server, config.root.port])
    worker_thread.start()

    cache_pattern = re.compile(r'^\s*cache\s*$')
    recur_flag_pattern = re.compile(r'^\s*recursiveFlag\s+(on|off)\s*$')
    while True:
        prompt = input('>>> ')
        if match := cache_pattern.match(prompt):
            rrcache.logs()
        elif match := recur_flag_pattern.match(prompt):
            command = match.group(1)
            if command == 'on':
                recur_flag.set(True)
                print('recursive processing : on')
            elif command == 'off':
                recur_flag.set(False)
                print('recursive processing : off')
