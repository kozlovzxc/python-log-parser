import re

class LogParser(object):
    def __init__(self, format):
        var = re.compile(r'(\$\w+)')
	#possible type check: r'(?P<{0}>{1})'.format(*translate(part[1:]))
	#translate here: format(self.translate(part[1:]))
        process_part = lambda part: r'(?P<{0}>.*)'.format(part[1:]) if var.match(part) else re.escape(part)
        self.format = re.compile('^'+''.join(process_part(part) for part in var.split(format))+'$')

    def parse_record(self, record):
        match = self.format.match(record)
        return match.groupdict()

format = '''$remote_addr - $remote_user [$time_local]  "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"'''

record = '''83.149.25.67 - - [04/Jul/2016:13:46:15 -0400]  "GET / HTTP/1.1" 200 107 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36"'''

parser = LogParser(format)

from pprint import pprint
pprint(parser.parse_record(record))

'''
{'body_bytes_sent': '107',
 'http_referer': '-',
 'http_user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36',
 'remote_addr': '83.149.25.67',
 'remote_user': '-',
 'request': 'GET / HTTP/1.1',
 'status': '200',
 'time_local': '04/Jul/2016:13:46:15 -0400'}
'''
