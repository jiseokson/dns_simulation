import re
import threading

from config import config
from config import append_all
from config import extract_domain_name

def find_first(lst, cond):
    return next((item for item in lst if cond(item)), None)

class RR:
    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type

    def __str__(self):
        return f'{self.name} : {self.value} ({self.type})'
    
    def __eq__(self, obj) -> bool:
        return isinstance(obj, RR) and \
            (self.name, self.value, self.type) == (obj.name, obj.value, obj.type)

class Cache:
    def __init__(self, filepath=None):
        self.lock = threading.Lock()
        self.rrs = []
        if filepath is None: return
        append_all(
            filepath,
            r'([a-zA-Z0-9][a-zA-Z0-9\-\.]*),(\d+\.\d+\.\d+\.\d+|[a-zA-Z0-9][a-zA-Z0-9\-\.]*),(A|NS|CNAME)',
            RR,
            self.rrs
            )

    def append(self, *rrs):
        with self.lock:
            for rr in rrs:
                if rr not in self.rrs: self.rrs.append(rr)

    def logs(self):
        with self.lock:
            print('\n'.join(str(rr) for rr in self.rrs))

    def resolve(self, name) -> tuple[list[RR], bool]:
        with self.lock:
            rrs = []

            # A type RR
            cname = name
            cname_rr: RR|None = find_first(self.rrs, lambda rr: rr.name == name and rr.type == 'CNAME')
            if cname_rr:
                rrs.append(cname_rr)
                cname = cname_rr.value
            a_rr: RR|None = find_first(self.rrs, lambda rr: rr.name == cname and rr.type == 'A')
            if a_rr:
                rrs.append(a_rr)
                return rrs, True

            # authoritative dns
            domain_name = re.search(r'([a-zA-Z0-9\-]*\.com)', name).string
            ns_rr: RR|None = find_first(self.rrs, lambda rr: re.match(rf'[a-zA-Z0-9\-]*\.{domain_name}$', rr.name) and rr.type == 'NS') # regex 앞부분 지워도 되지 않나?????? 어차피 (a.com, dns.a.com, NS), (dns.a.com, 1.1.1.1, A) 이런식이니까???
            if ns_rr:
                rrs.append(ns_rr)
                a_rr: RR|None = find_first(self.rrs, lambda rr: rr.name == ns_rr.value and rr.type == 'A')
                if a_rr: rrs.append(a_rr)
                return rrs, False

            # comtld dns
            ns_rr = find_first(self.rrs, lambda rr: rr.name == config.comtld.name)
            if ns_rr:
                rrs.append(ns_rr)
                return rrs, False

            # root dns
            ns_rr = find_first(self.rrs, lambda rr: rr.name == config.root.name)
            if ns_rr:
                rrs.append(ns_rr)
                return rrs, False
            
            return None, False

def all_company_dns() -> list[RR]:
        rrs = []
        for stmt in config.company_servers:
            rrs.append(RR(extract_domain_name(stmt.name), stmt.name, 'NS'))
            rrs.append(RR(stmt.name, stmt.ip, 'A'))
        return rrs

def resolve_ip(rrs: list[RR], name: str, type: str) -> tuple[str, bool]:
    if type == 'A':
        cur_rr: RR = find_first(rrs, lambda rr: rr.name == name and rr.type == 'CNAME')
        if not cur_rr:
            cur_rr: RR = find_first(rrs, lambda rr: rr.name == name and rr.type == 'A')
    elif type == 'NS':
        cur_rr: RR = find_first(rrs, lambda rr: rr.name == extract_domain_name(name) and rr.type == 'NS')

    result = []
    while cur_rr:
        result.append(cur_rr)
        cur_rr = find_first(rrs, lambda rr: rr.name == cur_rr.value)

    if type == 'NS' and len(result) == 0:
        if cur_rr := find_first(rrs, lambda rr: rr.name == config.comtld.name) or \
            find_first(rrs, lambda rr: rr.name == config.root.name):
            result.append(cur_rr)

    if len(result) == 0 or result[-1].type != 'A':
        return None, False
    return result[-1].value, True