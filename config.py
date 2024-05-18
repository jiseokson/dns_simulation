import re

CONFIG_FILEPATH = './config.txt'

class Statement:
    def __init__(self, server, name, ip, port):
        self.server = server
        self.name = name
        self.ip = ip
        self.port = int(port)

    def __str__(self):
        return f'{self.server} = [{self.name}, {self.ip}] #{self.port}'

class Config:
    def __init__(self):
        self.statements = []
        self.company_servers = []
        self.__local = None
        self.__root = None
        self.__comtld = None

    def append(self, statement):
        self.statements.append(statement)

    def append_company(self, server):
        self.company_servers.append(server)

    @property
    def local(self):
        if self.__local is None:
            self.__local = next(stmt for stmt in self.statements \
                                    if stmt.server == 'local')
        return self.__local

    @property
    def root(self):
        if self.__root is None:
            self.__root = next(stmt for stmt in self.statements \
                                    if stmt.server == 'root')
        return self.__root

    @property
    def comtld(self):
        if self.__comtld is None:
            self.__comtld = next(stmt for stmt in self.statements \
                                     if stmt.server == 'comTLD')
        return self.__comtld
    
    def find_by_server(self, server) -> Statement:
        try:
            stmt = next(stmt for stmt in self.statements \
                        if stmt.server == server)
        except StopIteration:
            stmt = None
        return stmt
    
    def resolve_port(self, ip):
        try:
            stmt = next(stmt for stmt in self.statements \
                        if stmt.ip == ip)
        except StopIteration:
            return None
        return stmt.port
    
def append_all(filepath, pattern, cls, obj):
    pattern = re.compile(pattern)
    with open(filepath, 'r') as file:
        with open(CONFIG_FILEPATH, 'r') as file:
            for line in file.readlines():
                match = pattern.match(re.sub(r'\s+', '', line))
                el = cls(*match.groups())
                obj.append(el)

def extract_domain_name(name):
    if match := re.search(r'([a-zA-Z0-9\-]*\.com)', name):
        return match.string
    return None

config = Config()
append_all(
    CONFIG_FILEPATH,
    r'^([a-zA-Z0-9][a-zA-Z0-9\-]*)_dns_server=\[([a-zA-Z0-9][a-zA-Z0-9\-\.]*),(\d+\.\d+\.\d+\.\d+)\](\d+)$',
    Statement,
    config
    )
