import os
import re

from regex import config_statement, domain_name, tld_name, company

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

    def find_by_server(self, server) -> Statement|None:
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

def extract_domain_name(name):
    if match := domain_name.search(name):
        return match.group(1)
    return None

def extract_tld_name(name):
    if match := tld_name.search(name):
        return match.group(1)
    return None

def extract_company(filepath):
    if match := company.match(os.path.basename(filepath)):
        return match.group(1)
    return None

config = Config()
with open(CONFIG_FILEPATH, 'r') as file:
    for line in file.readlines():
        if match := config_statement.match(re.sub(r'\s+', '', line)):
            config.append(Statement(*match.groups()))
            if (server := match.group(1)) not in ['local', 'root', 'comTLD']:
                config.company_servers.append(server)
