import re
import threading

from config import config
import cache
import flag
import resolver

def all_company_dns() -> list[cache.RR]:
    rrs = []
    for server in config.company_servers:
        stmt = cache.find_first(config.statements, lambda stmt: stmt.server == server)
        rrs.append(cache.RR(cache.extract_domain_name(stmt.name), stmt.name, 'NS'))
        rrs.append(cache.RR(stmt.name, stmt.ip, 'A'))
    return rrs

if __name__ == '__main__':
    rrcache = cache.Cache()
    rrcache.append(*all_company_dns())
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
