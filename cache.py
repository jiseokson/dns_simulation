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

def find_a_ip(rrs: list[RR], name: str) -> tuple[str, bool]:
    try:
        cname = next(rr.value for rr in rrs if rr.name == name and rr.type == 'CNAME')
    except StopIteration:
        cname = None
    if cname is not None: name = cname
    try:
        ip = next(rr.value for rr in rrs if rr.name == name and rr.type == 'A')
    except StopIteration:
        return None, False
    return ip, True

def find_ns_ip(rrs: list[RR], name: str) -> tuple[str, bool]:
    # resolve authoritative dns
    domain_name = re.search(r'([a-zA-Z0-9\-]*\.com)', name).string
    try:
        ns_ip = next(rr.value for rr in rrs \
                     if re.match(rf'[a-zA-Z0-9\-]*\.{domain_name}$', rr.name) and rr.type == 'NS')
    except StopIteration:
        ns_ip = None
    if ns_ip: return ns_ip, True

    # resolve comtld dns
    try:
        ns_ip = next(rr.value for rr in rrs \
                     if rr.name == config.comtld.name)
    except StopIteration:
        ns_ip = None
    if ns_ip: return ns_ip, True

    # resolve root dns
    try:
        ns_ip = next(rr.value for rr in rrs \
                     if rr.name == config.root.name)
    except StopIteration:
        return None, False
    
    return ns_ip, True

def all_company_dns() -> list[RR]:
        rrs = []
        for stmt in config.company_servers:
            rrs.append(RR(extract_domain_name(stmt.name), stmt.name, 'NS'))
            rrs.append(RR(stmt.name, stmt.ip, 'A'))
        return rrs