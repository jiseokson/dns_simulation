import copy
import pickle

import cache

class Message:
    def __init__(self, name=None, recur_desire=True):
        self.message = {
            'query': name,
            'recur_desire': recur_desire,
            'answer': [],
            'logs': [],
        }

    def copy(self):
        message = Message()
        message.message = copy.deepcopy(self.message)
        return message
    
    def to_query(self):
        message = self.copy()
        message.message['answer'] = []
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
    def recur_available(self):
        return self.message.get('recur_available')
    
    @property
    def answer(self):
        return self.message.get('answer')
    
    @recur_available.setter
    def recur_available(self, value):
        if isinstance(value, bool): self.message['recur_available'] = value

    def add_answer(self, *rrs):
        for rr in rrs: self.message.get('answer').append(rr)
    
    def __str__(self):
        resolved_ip, _ = cache.find_a_ip(self.message.get('answer'), self.message.get('query')) 
        return \
            f'{self.message.get("query")} : {resolved_ip}' + '\n' + \
            f'(via: {" -> ".join(self.message.get("logs"))})'

def query(name, recur_desire):
    return Message(name, recur_desire)

def decode(bytes) -> Message:
    message = Message()
    message.message = pickle.loads(bytes)
    return message
