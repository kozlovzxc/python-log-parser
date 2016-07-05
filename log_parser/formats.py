class LogFormatTranslator(object):
    def __init__(self):
        self.view_regex = {
                'any': r'.*',
                'ip': r'\d{0,3}.\d{0,3}.\d{0,3}.\d{0,3}',
                'num': r'\d+',
                'alpha': r'[a-zA-Z]+',
                'alphanum': r'[a-zA-Z0-9]+',
                'alphanum_': r'\w+',
                }
        #coming soon...

        self.variable_template = r'(\$\w+)'

    def get_variable_template(self):
        return self.variable_template
    
    def _translation(self, token):
        return token[1:], self.view_regex['any']

    def get_translation(self):
        return self._translation


class NginxLogFormatTranslator(LogFormatTranslator):
    def __init__(self):
        self.variable_template = r'(\$\w+)'
        self.translation = {
                '$remote_addr': ('request_src_ip', 'ip'),
                '$remote_user': ('request_user', 'any'),
                '$time_local': ('request_time', 'any'),
                '$request': ('request_first_line', 'any'),
                '$status': ('response_status', 'num'),
                '$body_bytes_sent': ('response_body_size', 'num'),
                }
        #coming soon...
        super(NginxLogFormatTranslator, self).__init__()

    def _translation(self, token):
        if token in self.translation:
            name, view = self.translation[token] 
            return name, self.view_regex.get(view, view)
        #this will save some space in self.translation
        elif token.startswith('$http_'):
            return 'request_headers_'+token[6:], self.view_regex['any']
        else:
            raise KeyError('Unknown token: {0}'.format(token))

Translators = {
        'default': LogFormatTranslator,
        'nginx': NginxLogFormatTranslator
        }
