import asyncio
from inspect import isawaitable
from typing import Tuple

from asyncselectors import AsyncEpollSelector
from asyncsocket import AsyncSocket


class AsyncServer:
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()
        self.selector = AsyncEpollSelector(loop=self.loop)

    async def _handle_client(self, client: AsyncSocket):
        with client:
            if isawaitable(self.handle_client):
                await self.handle_client(client)
            else:
                self.handle_client(client)

    async def server_loop(self, address: Tuple[str, int]):
        with AsyncSocket(self.selector) as server:
            server.bind(address)
            server.listen()
            print('Listening on {}:{}'.format(*address))
            while True:
                client, address = await server.accept()
                print('New client', client.fileno(), 'from', address)
                self.loop.create_task(self._handle_client(client))

    async def handle_client(self, client: AsyncSocket):
        raise NotImplementedError

    def run(self, address: Tuple[str, int], timeout=None):
        tasks = [
            self.selector.poll(),
            self.server_loop(address),
        ]
        self.loop.run_until_complete(asyncio.gather(*tasks))
