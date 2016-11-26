import asyncio
from asyncio.coroutines import iscoroutinefunction
from typing import Tuple

from asyncselectors import AsyncEpollSelector
from asyncsocket import AsyncSocket


class AsyncServer:
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()
        self.selector = AsyncEpollSelector(loop=self.loop)

    async def server_loop(self, address: Tuple[str, int]):
        with AsyncSocket(self.selector) as server:
            server.bind(address)
            server.listen()
            print('Listening on {}:{}'.format(*address))
            while True:
                client, address = await server.accept()
                print('New client', client.fileno(), 'from', address)
                if iscoroutinefunction(self.handle_client):
                    self.loop.create_task(self.handle_client(client))
                else:
                    self.loop.call_soon(self.handle_client, client)

    async def handle_client(self, client: AsyncSocket):
        client.close()

    def run(self, address: Tuple[str, int], timeout=None):
        tasks = [
            self.selector.poll(),
            self.server_loop(address),
        ]
        self.loop.run_until_complete(asyncio.gather(*tasks))
