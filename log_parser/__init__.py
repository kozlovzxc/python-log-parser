import re
from formats import Translators

class LogParser(object):
    def __init__(self, log_format, log_type='default'):
        translator = Translators[log_type]()

        var = re.compile(translator.get_variable_template())
        translation = translator.get_translation()
         
        process_part = lambda part: r'(?P<{0}>{1})'.format(*translation(part)) if var.match(part) else re.escape(part)
        self.log_format = re.compile('^'+''.join(process_part(part) for part in var.split(log_format))+'$')

    def parse_record(self, record):
        match = self.log_format.match(record)
        return match.groupdict()

log_format = '''$remote_addr - $remote_user [$time_local]  "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"'''

record = '''83.149.25.67 - - [04/Jul/2016:13:46:15 -0400]  "GET / HTTP/1.1" 200 107 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36"'''

parser = LogParser(log_format, log_type='nginx')

from pprint import pprint
pprint(parser.parse_record(record))

'''
 {'request_first_line': 'GET / HTTP/1.1',
 'request_headers_referer': '-',
 'request_headers_user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36',
 'request_src_ip': '83.149.25.67',
 'request_time': '04/Jul/2016:13:46:15 -0400',
 'request_user': '-',
 'response_body_size': '107',
 'response_status': '200'}
'''
