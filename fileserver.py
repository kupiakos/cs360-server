import os
import re
from email.utils import formatdate
from urllib.request import url2pathname

import aiofiles

from httpresponse import HttpResponse
from httpserver import BaseHttpServer

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser


class HttpFileServer(BaseHttpServer):
    def __init__(self, root_dir: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_dir = root_dir
        self.mime_types = {}

    def add_mime_type(self, extension: str, mime_type: str):
        self.mime_types[extension.lower()] = mime_type

    async def handle_url(self, request: HttpParser) -> HttpResponse:
        method = request.get_method().upper()
        if method not in ('GET', 'HEAD'):
            return HttpResponse(405)
        path = request.get_path()
        if path.endswith('/'):
            path += 'index.html'
        relative = os.path.relpath(url2pathname(path), '/')
        filename = os.path.join(self.root_dir, relative)
        try:
            byte_range = None
            if 'Range' in request.get_headers():
                # Not RFC 7233 compliant
                range_match = re.match(r'bytes=(\d+)-(\d+)', request.get_headers()['Range'])
                if not range_match:
                    return HttpResponse(400, 'Invalid Range header')
                start, end = map(int, range_match.groups())
                # Python range is exclusive, HTTP Range is inclusive
                byte_range = range(start, end + 1)
            length = 0
            async with aiofiles.open(filename, 'rb') as f:
                if method == 'GET':
                    if byte_range is not None:
                        await f.seek(byte_range.start)
                        data = await f.read(len(byte_range))
                        byte_range = range(byte_range.start, byte_range.start + len(data))
                        await f.seek(0, os.SEEK_END)
                        length = await f.tell()
                        response = HttpResponse(206, data)
                    else:
                        data = await f.read()
                        response = HttpResponse(200, data)
                else:
                    # Used instead of os.stat to ensure the file can be accessed
                    response = HttpResponse(200)
                    await f.seek(0, os.SEEK_END)
                    length = await f.tell()
                    if byte_range is not None:
                        byte_range = range(byte_range.start, min(length, byte_range.stop))
                    response.headers['Content-Length'] = length
            if byte_range is not None:
                response.headers['Content-Range'] = 'bytes %d-%d/%d' % (
                    byte_range.start, byte_range.stop - 1, length)

        except FileNotFoundError:
            return HttpResponse(
                404, 'This is not the file you are looking for')
        except PermissionError:
            return HttpResponse(403)
        _, extension = os.path.splitext(filename)
        extension = extension[1:]
        if extension.lower() in self.mime_types:
            response.headers['Content-Type'] = self.mime_types[extension.lower()]
        response.headers['Last-Modified'] = formatdate(
            os.stat(filename).st_mtime,
            False, True
        )
        return response
