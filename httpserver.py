from typing import Tuple, Optional

from httpresponse import HttpResponse
from utils import call_maybe_async

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

from asyncsocket import AsyncSocket
from server import AsyncServer


async def _send_response(client: AsyncSocket, response: HttpResponse):
    client.sendall(bytes(response))
    client.close()


async def _recv_request(client: AsyncSocket, prefix: bytes) -> Tuple[Optional[HttpParser], bytes]:
    p = HttpParser()
    data = prefix
    num_parsed = 0
    if data:
        num_parsed = p.execute(prefix, len(prefix))
    while not p.is_message_complete():
        data = await client.recv(4096)
        if not data:
            return None, b''
        num_parsed = p.execute(data, len(data))
    return p, data[num_parsed:]


class BaseHttpServer(AsyncServer):
    async def handle_client(self, client: AsyncSocket):
        left = b''
        try:
            while True:
                request, left = await _recv_request(client, left)
                if not request:
                    break
                if not (request.get_url() and request.get_method()):
                    print('Invalid response')
                    await _send_response(client, HttpResponse(400))
                '%s %s' % (request.get_method(), request.get_path())
                response = await call_maybe_async(self.handle_url, request)
                response.headers['Server'] = 'kupiakos server'
                client.sendall(bytes(response))
                if not request.should_keep_alive():
                    break
        except Exception as e:
            print(e)
            await _send_response(client, HttpResponse(500, str(e)))

    def handle_url(self, request: HttpParser) -> HttpResponse:
        return HttpResponse(
            501, '%s %s' % (request.get_method(), request.get_path()))
