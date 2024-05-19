import re
import threading

from config import config
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
        with open(filepath, 'r') as file:
            pattern = re.compile(r'([a-zA-Z0-9][a-zA-Z0-9\-\.]*),(\d+\.\d+\.\d+\.\d+|[a-zA-Z0-9][a-zA-Z0-9\-\.]*),(A|NS|CNAME)')
            for line in file.readlines():
                match = pattern.match(re.sub(r'\s+', '', line))
                self.rrs.append(RR(*match.groups()))

    def append(self, *rrs):
        with self.lock:
            for rr in rrs:
                if rr not in self.rrs: self.rrs.append(rr)

    def logs(self):
        with self.lock:
            print('\n'.join(str(rr) for rr in self.rrs))

    def resolve(self, name) -> tuple[list[RR], bool]:
        with self.lock:
            return resolve(self.rrs, name)

def find_first(lst, cond):
    return next((item for item in lst if cond(item)), None)

def resolve(rrs: list[RR], name: str) -> list[RR]:
    # A type RR
    rrchaine = []
    cur_rr = \
        find_first(rrs, lambda rr: rr.name == name and rr.type == 'CNAME') or \
        find_first(rrs, lambda rr: rr.name == name and rr.type == 'A')
    while cur_rr:
        rrchaine.append(cur_rr)
        cur_rr = find_first(rrs, lambda rr: rr.name == cur_rr.value)
    if len(rrchaine) > 0:
        return rrchaine, rrchaine[-1].type == 'A'
    
    # Authoritative DNS
    rrchaine = []
    cur_rr = find_first(rrs, lambda rr: rr.name == extract_domain_name(name) and rr.type == 'NS')
    while cur_rr:
        rrchaine.append(cur_rr)
        cur_rr = find_first(rrs, lambda rr: rr.name == cur_rr.value)
    if len(rrchaine) > 0:
        return rrchaine, False
    
    # com TLD DNS
    if comtld_rr := find_first(rrs, lambda rr: rr.name == config.comtld.name):
        return [comtld_rr], False
    
    # Root DNS
    if root_rr := find_first(rrs, lambda rr: rr.name == config.root.name):
        return [root_rr], False
    
    return None, False

def resolve_ip(rrs: list[RR], name: str, type: str) -> tuple[str, bool]:
    if type == 'A':
        cur_rr: RR = \
            find_first(rrs, lambda rr: rr.name == name and rr.type == 'CNAME') or \
            find_first(rrs, lambda rr: rr.name == name and rr.type == 'A')
    elif type == 'NS':
        cur_rr: RR = find_first(rrs, lambda rr: rr.name == extract_domain_name(name) and rr.type == 'NS')

    rrchaine = []
    while cur_rr:
        rrchaine.append(cur_rr)
        cur_rr = find_first(rrs, lambda rr: rr.name == cur_rr.value)

    if type == 'NS' and len(rrchaine) == 0:
        if cur_rr := find_first(rrs, lambda rr: rr.name == config.comtld.name) or \
            find_first(rrs, lambda rr: rr.name == config.root.name):
            rrchaine.append(cur_rr)

    if len(rrchaine) == 0 or rrchaine[-1].type != 'A':
        return None, False
    return rrchaine[-1].value, True
