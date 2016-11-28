#!/usr/bin/env python3

import sys
if sys.version_info.minor < 5:
    raise Exception('Must use Python 3.5 or above!')

import argparse
import asyncio
import shlex
import traceback
from typing import Tuple, Mapping

from fileserver import HttpFileServer


def parse_config(file) -> Tuple[Tuple[str, str],
                                Mapping[str, str],
                                Mapping[str, str]]:
    host = None
    media = {}
    params = {}
    for n, line in enumerate(file, 1):
        if not line.strip():
            continue
        data = shlex.split(line, True)
        if len(data) != 3:
            raise Exception('Line %d: Bad line in configuration' % n)
        group, val1, val2 = data
        if group.lower() == 'host':
            if host is not None:
                raise Exception('Line %d: Host already defined' % n)
            host = (val1, val2)
        elif group.lower() == 'media':
            if val1.lower() in media:
                raise Exception(
                    'Line %d: Media extension %s already defined' % (n, val1))
            media[val1.lower()] = val2
        elif group.lower() == 'parameter':
            if val1.lower() in params:
                raise Exception(
                    'Line %d: Parameter %s already defined' % (n, val1))
            params[val1.lower()] = val2
        else:
            raise Exception('Line %d: Unknown group name %s' % (n, group))
    if host is None:
        host = ('default', 'web')
    return host, media, params


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='web.conf',
                        help='The configuration file to use')
    parser.add_argument('-p', '--port', metavar='port', default=8080, type=int,
                        help='The port to run the server on')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Run the server in debug mode')
    args = parser.parse_args()
    if args.debug:
        asyncio.get_event_loop().set_debug(True)
    try:
        with open(args.config) as f:
            host, media, params = parse_config(f)
        hostname, root = host
        if hostname == 'default':
            hostname = 'localhost'
        server = HttpFileServer(root)
        timeout = float(params.get('timeout', 10))
        for extension, mime_type in media.items():
            server.add_mime_type(extension, mime_type)
        server.run((hostname, args.port), timeout=timeout)
    except Exception as e:
        traceback.print_exc()


if __name__ == '__main__':
    main()
