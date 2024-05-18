import re
import threading

from config import config
from config import append_all

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
            ### for test mocking data ###
            if len(self.rrs) == 1:
                return [RR('dns.rootDSNService.com', '57.32.9.101', 'A')], False
            else:
                return self.rrs[1:], True
            #############################

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