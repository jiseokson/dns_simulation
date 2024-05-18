import sys
import re
import threading

from config import extract_company
import cache
import flag
import resolver

if __name__ == '__main__':
    filepath = sys.argv[2]
    rrcache = cache.Cache(filepath=filepath)
    recur_flag = flag.Flag(False)

    worker_thread = threading.Thread( \
        target=resolver.resolver, \
        args=[rrcache, recur_flag, False, extract_company(filepath), int(sys.argv[1])])
    worker_thread.start()

    cache_pattern = re.compile(r'^\s*cache\s*$')
    while True:
        prompt = input('>>> ')
        if match := cache_pattern.match(prompt):
            rrcache.logs()
