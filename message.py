import copy
import pickle

class Message:
    def __init__(self, name=None, recur_desire=True):
        # todo: 생성자 인자, message 필드...
        self.message = {
            'query': name,
            'recur_desire': recur_desire,
            # 'recur_avaliable' ,
            'answer': [],
            'logs': [], # reply를 보낼 때 마다 config statement의 server를 추가
        }

    def copy(self):
        message = Message()
        message.message = copy.deepcopy(self.message)
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
    
    @recur_available.setter
    def recur_available(self, value):
        if isinstance(value, bool): self.message['recur_available'] = value

    def add_answer(self, rr):
        self.message['answer'].append(rr)
    
    def __str__(self):
        try:
            resolved_ip = next(rr.ip for rr in self.message.get('answer') \
                               if rr.type == 'A')
        except StopIteration:
            resolved_ip = None
        return \
            f'{self.message.get("query")} : {resolved_ip}' + '\n' + \
            f'(via: {" -> ".join(self.message.get("logs"))})'

def query(name, recur_desire):
    return Message(name, recur_desire)

def decode(bytes) -> Message:
    message = Message()
    message.message = pickle.loads(bytes)
    return message
