import threading

class Flag:
    def __init__(self, init=False):
        self.lock = threading.Lock()
        self.__value = init

    def set(self, value):
        with self.lock:
            self.__value = value

    @property
    def value(self):
        with self.lock:
            return self.__value
