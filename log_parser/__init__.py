from pyparsing import *
from string import printable, uppercase
from dateutil import parser as dateutil_parser
import yaml

class LogParser(object):
    ACCESS_LOG_VARS = {
            'request.first_line' : Word(uppercase)('request.method')+\
                    Literal(" ")+\
                    SkipTo(" ")('request.uri')+\
                    Literal(" ")+\
                    Combine("HTTP/"+\
                    Word(nums+'.', exact=3))('request.protocol'),
            #'request.time' : Word(alphanums+' /:+-').setParseAction(lambda s,l,t : dateutil_parser.parse(t[0].replace(':', ' ', 1)) )
            }

    def translate_nginx_varname(self, chunk):
        name = chunk['var_name']
        if name in self.NGINX_TO_INTERNAL:
            return self.NGINX_TO_INTERNAL[name]
        elif name.startswith('http_'):
            return 'request.headers.'+name[5:].replace('_', '-')
        elif name.startswith('sent_http_'):
            return 'response.headers.'+name[10:].replace('_', '-')
        elif name.startswith('request_'):
            # body, body_file, id, completion, length, method, uri
            return 'request.'+name[8:]
        elif name.startswith('cookie_'):
            return 'request.headers.cookies.'+name[7:].replace('_', '-')
        elif name.startswith('arg_'):
            return 'request.args.'+name[4:]
        elif name.startswith('tcpinfo_'):
            # rtt, rttvar, snd_cwnd, rcv_space
            return 'tcpinfo.'+name[8:]
        else:
            return name
    
    def translate_apache_varname(self, chunk):
        name = chunk['var_name']
        if 'option' in chunk:
            option = chunk['option']
            if name == 'a':
                if option == 'c':
                    return 'request.proxy.src_ip'
                else:
                    raise KeyError('Unknown Key: {0}'.format(option))
            elif name =='p':
                if option == 'canonical':
                    return '' #???
                elif option == 'local':
                    return 'request.dst_port'
                elif option == 'remote':
                    return 'request.src_port'
            elif name == 'C':
                return 'request.headers.cookies.'+option.lower()
            elif name == 'e':
                return 'server.enviroment.'+option.lower()
            elif name == 'i':
                return 'request.headers.'+option.lower()
            elif name == 'o':
                return 'response.headers.'+option.lower()
            elif name == 'P':
                return 'server.worker.'+option.lower()
            elif name == 't':
                return 'request.{0}_time'.format(option.lower())
            elif name == 'T':
                return 'request.{0}_time_consume'.format(option.lower())
            else:
                return name
        else:
            return self.APACHE_TO_INTERNAL[name]

    def __init__(self, log_format, log_type='nginx'):
        with open('log_parser/nginx_translation.yml','r') as nginx_translation:
            self.NGINX_TO_INTERNAL = yaml.load(nginx_translation)
        with open('log_parser/apache_translation.yml', 'r') as apache_translation:
            self.APACHE_TO_INTERNAL = yaml.load(apache_translation)

        self.default_white_chars =  ParserElement.DEFAULT_WHITE_CHARS
        ParserElement.setDefaultWhitespaceChars('')
        settings = {
                'nginx':{
                    'variable': Group(Suppress('$')+ Word(alphanums+'_')('var_name')),
                    'literal': Word(printable, excludeChars='$'),
                    'translation': self.translate_nginx_varname,
                    },
                'apache':{
                    'variable': Group(Suppress(\
                                '%'+\
                                Optional(\
                                    Literal('!')\
                                )+\
                                Optional(\
                                    Word(nums)+\
                                    ZeroOrMore(\
                                        ','+\
                                        Word(nums)\
                                    )\
                                )+\
                                Optional(\
                                    Word('<>', exact=1)\
                                )\
                            )+\
                            Optional(Suppress('{')+\
                                Word(alphas+'-')('option')+\
                                Suppress('}')\
                            )+\
                            Word(alphas, min=1, max=2)('var_name')),
                    'literal': Word(printable, excludeChars='%'),
                    'translation': self.translate_apache_varname,
                    },
                'default':{
                    'variable': Group('${'+ Word(alphanums+'_')('var_name')+'}'),
                    'literal': Word(printable, excludeChars='${}'),
                    'translation': lambda token: token[2:-1]
                    },
                }
        log_type_settings = settings.get(log_type, 'default') 
        variable = log_type_settings['variable']
        literal = log_type_settings['literal']
        translation = log_type_settings['translation']
        log_format_parser = ZeroOrMore(variable|literal)
        log_format_tokens = log_format_parser.parseString(log_format)
        self.parser = Empty()
        for i in xrange(0, len(log_format_tokens)):
            chunk = log_format_tokens[i]
            if isinstance(chunk, str):
                append = Literal(chunk)
            else:
                var_name = translation(chunk)
                if var_name in self.ACCESS_LOG_VARS:
                    append = self.ACCESS_LOG_VARS[var_name]
                else:
                    if i + 1 < len(log_format_tokens):
                        append = SkipTo(log_format_tokens[i+1])
                    else:
                        append = SkipTo(LineEnd())
                append = append.setResultsName(var_name)

            self.parser += append 
    
        ParserElement.setDefaultWhitespaceChars(self.default_white_chars)

    def _make_dict(self, parsed):
        return {key:(''.join(val._asStringList()) if isinstance(val, ParseResults) else val) for key,val in parsed.items()}

    def parse(self, record):
        return self._make_dict(self.parser.parseString(record))

