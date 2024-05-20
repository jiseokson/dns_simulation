import copy
import pickle

import cache

class Message:
    def __init__(self, name=None, recur_desire=True):
        self.message = {
            'query': name,
            'recur_desire': recur_desire,
            'answer': None,
            'authority': None,
            'additional': None,
            'logs': [],
        }

    def __str__(self):
        ip, _ = cache.resolve_ip(self.message.get('answer'), self.message.get('query'), 'A')
        return \
            f'{self.message.get("query")} : {ip}' + '\n' + \
            f'(via: {" -> ".join(pretty_server_name(server) \
                                 for server in self.message.get("logs"))})'

    def copy(self):
        message = Message()
        message.message = copy.deepcopy(self.message)
        return message
    
    def copy_to_query(self):
        message = self.copy()
        message.message['answer'] = None
        message.message['authority'] = None
        message.message['additional'] = None
        return message

    def encode(self):
        return pickle.dumps(self.message)
    
    def add_log(self, server):
        self.message['logs'].append(server)

    @property
    def name(self):
        return self.message.get('query')
    
    @property
    def recur_desire(self):
        return self.message.get('recur_desire')
    
    @recur_desire.setter
    def recur_desire(self, value):
        if isinstance(value, bool): self.message['recur_desire'] = value
    
    @property
    def answer(self):
        return self.message.get('answer')
    
    @answer.setter
    def answer(self, rr):
        if isinstance(rr, cache.RR): self.message['answer'] = rr
    
    @property
    def authority(self):
        return self.message.get('authority')
    
    @authority.setter
    def authority(self, rr):
        if isinstance(rr, cache.RR): self.message['authority'] = rr

    @property
    def additional(self):
        return self.message.get('additional')

    @additional.setter
    def additional(self, rr):
        if isinstance(rr, cache.RR): self.message['additional'] = rr

def query(name, recur_desire):
    return Message(name, recur_desire)

def decode(bytes) -> Message:
    message = Message()
    message.message = pickle.loads(bytes)
    return message

def pretty_server_name(server):
    if server in ['local', 'root']:
        return server + ' DNS server'
    if server == 'comTLD':
        return '.com TLD DNS server'
    return server + '.com DNS server'