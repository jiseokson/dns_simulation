import re
import threading

from config import config
from config import append_all
from config import extract_domain_name

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
            pass

def find_first(lst, cond):
    return next((item for item in lst if cond(item)), None)

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