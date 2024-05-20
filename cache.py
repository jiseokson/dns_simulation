import re
import threading

from config import extract_domain_name, extract_tld_name
from regex import cache_statement

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
            for line in file.readlines():
                if match := cache_statement.match(re.sub(r'\s+', '', line)):
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

def resolve_ip(name: str, type: str, answer: RR|None, authority: RR|None, additional: RR|None) -> str|None:
    if answer and answer.type == 'A':
        return answer.value
    if additional and \
        (answer and (answer.value, answer.type) == (additional.name, 'CNAME')) or \
        (authority and (authority.value, authority.type) == (additional.name, 'NS')):
        return additional.value
    return None
