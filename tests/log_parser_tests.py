import unittest
from log_parser import LogParser

class LogParserTest(unittest.TestCase):
    def test_nginx_log_parsing(self):
        log_format = '$remote_addr - $remote_user [$time_local]  "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" "$request_body"'
        log_type = 'nginx'
        parser = LogParser(log_format, log_type)
        record = '127.0.0.1 - - [08/Jul/2016:08:45:58 -0400]  "POST /place HTTP/1.1" 404 233 "-" "curl/7.38.0" "way"'
        parsed = parser.parse(record)
        self.assertEqual(parsed, {'request.first_line': 'POST /place HTTP/1.1',
                 'request.headers.referer': '-',
                 'request.headers.user-agent': 'curl/7.38.0',
                 'request.method': 'POST',
                 'request.protocol': 'HTTP/1.1',
                 'request.src_ip': '127.0.0.1',
                 'request.time': '08/Jul/2016:08:45:58 -0400',
                 'request.uri': '/place',
                 'request.user': '-',
                 'request.body': 'way',
                 'response.body_size': '233',
                 'response.status': '404'})
    
    def test_apache_log_parsing(self):
        log_format = '%h %l %u %t "%r" %>s %O "%{Referer}i" "%{User-Agent}i"' 
        log_type = 'apache'
        parser = LogParser(log_format, log_type)
        record = '127.0.0.1 - - [12/Jul/2016:14:00:22 +0300] "GET /test HTTP/1.1" 200 10956 "-" "curl/7.47.0"'
        parsed = parser.parse(record)
        self.assertEqual(parsed, {'request.client_id': '-',
             'request.first_line': 'GET /test HTTP/1.1',
             'request.headers.referer': '-',
             'request.headers.user-agent': 'curl/7.47.0',
             'request.method': 'GET',
             'request.protocol': 'HTTP/1.1',
             'request.src_ip': '127.0.0.1',
             'request.time': '[12/Jul/2016:14:00:22 +0300]',
             'request.uri': '/test',
             'request.user': '-',
             'response.size': '10956',
             'response.status': '200'})
