import time
from email.utils import formatdate
from typing import Union

from http_parser.util import IOrderedDict, status_reasons


def to_bytes(obj) -> bytes:
    if isinstance(obj, bytes):
        return obj
    if isinstance(obj, int):
        return str(obj).encode()
    if isinstance(obj, str):
        return obj.encode()
    return bytes(obj)


class HttpResponse:
    def __init__(self, code: int, content: Union[bytes, str] = b''):
        self.content = to_bytes(content)
        self.response_code = code
        self.headers = IOrderedDict()
        self._standard_headers()

    def _standard_headers(self):
        if 'Content-Length' not in self.headers:
            self.headers['Content-Length'] = len(self.content)
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = b'text/html'
        if 'Date' not in self.headers:
            self.headers['Date'] = formatdate(time.time(), False, True)

    def __bytes__(self):
        self._standard_headers()
        reason = status_reasons.get(self.response_code, 'Unknown').encode()
        response = (
            b'HTTP/1.1 %03d %s\r\n' % (self.response_code, reason) +
            b''.join(
                b'%s: %s\r\n' % (to_bytes(name), to_bytes(val))
                for name, val in self.headers.items()
            ) +
            b'\r\n' +
            to_bytes(self.content)
        )
        return response
