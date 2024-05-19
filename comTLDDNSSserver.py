import re
import threading

from config import config
import cache
import flag
import resolver

if __name__ == '__main__':
    rrcache = cache.Cache()
    rrcache.append(*cache.all_company_dns())
    recur_flag = flag.Flag(False)

    worker_thread = threading.Thread( \
        target=resolver.resolver, \
        args=[rrcache, recur_flag, False, config.comtld.server, config.comtld.port])
    worker_thread.start()

    cache_pattern = re.compile(r'^\s*cache\s*$')
    recur_flag_pattern = re.compile(r'^\s*recursiveFlag\s+(on|off)\s*$')
    while True:
        prompt = input('>>> ')
        if match := cache_pattern.match(prompt):
            rrcache.logs()
        elif match := recur_flag_pattern.match(prompt):
            command = match.group(1)
            match command:
                case 'on':
                    recur_flag.set(True)
                case 'off':
                    recur_flag.set(False)
