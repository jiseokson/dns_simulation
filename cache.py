import re
import threading

from config import append_all

class RR:
    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type

    def __str__(self):
        return f'{self.name} : {self.value} ({self.type})'

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

    def append(self, rr):
        with self.lock:
            self.rrs.append(rr)

    def logs(self):
        with self.lock:
            print('\n'.join(str(rr) for rr in self.rrs))

    def resolve(self, name, type):
        with self.lock:
            pass
