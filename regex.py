import re

config_statement = re.compile(r'^([a-zA-Z0-9][a-zA-Z0-9\-]*)_dns_server=\[([a-zA-Z0-9][a-zA-Z0-9\-\.]*),(\d+\.\d+\.\d+\.\d+)\](\d+)$')
cache_statement = re.compile(r'^([a-zA-Z0-9][a-zA-Z0-9\-\.]*),(\d+\.\d+\.\d+\.\d+|[a-zA-Z0-9][a-zA-Z0-9\-\.]*),(A|NS|CNAME)$')

domain_name = re.compile(r'([^\.]*\.com)$')
tld_name = re.compile(r'([^\.]*)$')
company = re.compile(r'^(.*)\.txt$')

ipaddr_command = re.compile(r'^\s*ipaddr\s+([a-zA-Z0-9][a-zA-Z0-9\-\.]*)\s*$')
cache_command = re.compile(r'^\s*cache\s*$')
recur_flag_command = re.compile(r'^\s*recursiveFlag\s+(on|off)\s*$')
