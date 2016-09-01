#!/usr/bin/env python

from log_parser import LogParser

import argparse
import tailer
import yaml, json

def main():
    parser = argparse.ArgumentParser(description='Convert logs to custom fileformat(now supports json and yaml fileformats)', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_file', help='file with input logs', type=argparse.FileType('r'))
    parser.add_argument('output_file', help='file with parsed data', type=argparse.FileType('w'))
    # default nginx log_format: '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"' 
    # Note: spaces in log_format is important!
    parser.add_argument('log_format', help='''logs format. Supports: nginx log_format and apache CustomLog, also you may use custom format''')
    parser.add_argument('--log_type', help='type of log file.', choices=['nginx', 'apache', 'custom'], default='nginx')
    parser.add_argument('--result_type', help='type of parsed file', choices=['yaml', 'json'], default='json')
    parser.add_argument('-f', '--follow',  action='store_true', default=False,  help='process appended data as the file grows')
    args = parser.parse_args()
    
    parser = LogParser(args.log_format, args.log_type)
    parsed_logs = []
    try:
        for record in (tailer.follow(args.input_file) if args.follow else args.input_file):
            parsed_logs.append(parser.parse(record))
    except KeyboardInterrupt:
        print('interrupt received, stopping.')
    finally:
        if args.result_type == 'yaml':
            yaml.dump(parsed_logs, args.output_file, default_flow_style=False)
        elif args.result_type == 'json':
            json.dump(parsed_logs, args.output_file)

if __name__=='__main__':
    main()
