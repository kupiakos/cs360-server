import os
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
            # Should be HTTP 405...
            return HttpResponse(501)
        path = request.get_path()
        if path.endswith('/'):
            path += 'index.html'
        relative = os.path.relpath(url2pathname(path), '/')
        filename = os.path.join(self.root_dir, relative)
        try:
            async with aiofiles.open(filename, 'rb') as f:
                if method == 'GET':
                    data = await f.read()
                    response = HttpResponse(200, data)
                else:
                    # Used instead of os.stat to ensure the file can be accessed
                    response = HttpResponse(200)
                    f.seek(0, os.SEEK_END)
                    response.headers['Content-Length'] = f.tell()
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
