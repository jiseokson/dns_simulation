import threading

class Flag:
    def __init__(self, init=False):
        self.lock = threading.Lock()
        self.__value = init

    @property
    def value(self):
        with self.lock:
            return self.__value
        
    @value.setter
    def value(self, obj):
        if isinstance(obj, bool):
            with self.lock:
                self.__value = obj
