import asyncio
import socket
from typing import Tuple

from asyncselectors import AsyncEpollSelector
from asyncsocket import AsyncSocket
from utils import call_maybe_async


class AsyncServer:
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()
        self.selector = AsyncEpollSelector(loop=self.loop)

    async def _handle_client(self, client: AsyncSocket):
        try:
            await call_maybe_async(self.handle_client, client)
        except Exception as e:
            print('Error with client:', e)
        finally:
            client.close()

    async def server_loop(self, server: AsyncSocket):
        try:
            while True:
                client, address = await server.accept()
                print('New client', client.fileno(), 'from', address)
                self.loop.create_task(self._handle_client(client))
        except Exception as e:
            print('Error with server:', e)
        finally:
            server.close()

    async def handle_client(self, client: AsyncSocket):
        raise NotImplementedError

    def run(self, address: Tuple[str, int], timeout=None):
        server = AsyncSocket(self.selector, timeout=False)
        try:
            server.bind(address)
            server.listen()
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print('Listening on {}:{}'.format(*address))
        except OSError as e:
            print('Could not bind socket!', e)
            server.close()
            return

        tasks = [
            self.selector.poll(),
            self.server_loop(server),
        ]
        if timeout:
            tasks.append(self.selector.timeout_loop(timeout))
        self.loop.run_until_complete(asyncio.gather(*tasks))
