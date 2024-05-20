import re
import threading

from config import config
from config import extract_domain_name, extract_tld_name

class RR:
    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type

    def __str__(self):
        return f'{self.name}. : {self.value} ({self.type})'
    
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
                if match := pattern.match(re.sub(r'\s+', '', line)):
                    self.rrs.append(RR(*match.groups()))

    def add_rr(self, *rrs):
        with self.lock:
            for rr in rrs:
                if rr and rr not in self.rrs: self.rrs.append(rr)

    def logs(self):
        with self.lock:
            print('\n'.join(str(rr) for rr in self.rrs))

    def resolve(self, name) -> tuple[RR|None, RR|None, RR|None]:
        with self.lock:
            return resolve(name, self.rrs)

def find(lst, condition):
    return next((item for item in lst if condition(item)), None)

def resolve(name: str, rrs: list[RR]) -> tuple[RR|None, RR|None, RR|None]:
    # Answer section
    answer: RR|None = \
        find(rrs, lambda rr: rr.name == name and rr.type == 'CNAME') or \
        find(rrs, lambda rr: rr.name == name and rr.type == 'A') or \
        None
    
    # Authority section
    authority: RR|None = \
        find(rrs, lambda rr: rr.name == extract_domain_name(name) and rr.type == 'NS') or \
        find(rrs, lambda rr: rr.name == extract_tld_name(name) and rr.type == 'NS') or \
        find(rrs, lambda rr: rr.name == '' and rr.type == 'NS') or \
        None
    
    # Additional section
    additional: RR|None = None
    if answer:
        additional = find(rrs, lambda rr: answer.value == rr.name)
    elif authority:
        additional = find(rrs, lambda rr: authority.value == rr.name)
    
    return answer, authority, additional

# todo: return type => ip|None
def resolve_ip(name: str, type: str, answer: RR|None, authority: RR|None, additional: RR|None) -> tuple[str, bool]:
    ### for mocking
    rrs = []
    if answer: rrs.append(answer)
    if authority: rrs.append(authority)
    if additional: rrs.append(additional)
    ####

    if type == 'A':
        cur_rr: RR = \
            find(rrs, lambda rr: rr.name == name and rr.type == 'CNAME') or \
            find(rrs, lambda rr: rr.name == name and rr.type == 'A')
    elif type == 'NS':
        cur_rr: RR = find(rrs, lambda rr: rr.name == extract_domain_name(name) and rr.type == 'NS')

    rrchaine = []
    while cur_rr:
        rrchaine.append(cur_rr)
        cur_rr = find(rrs, lambda rr: rr.name == cur_rr.value)

    if type == 'NS' and len(rrchaine) == 0:
        if cur_rr := find(rrs, lambda rr: rr.name == config.comtld.name) or \
            find(rrs, lambda rr: rr.name == config.root.name):
            rrchaine.append(cur_rr)

    if len(rrchaine) == 0 or rrchaine[-1].type != 'A':
        return None, False
    return rrchaine[-1].value, True
