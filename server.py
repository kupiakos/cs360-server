import asyncio

from .asyncsocket import AsyncSocket
from .socketmanager import SocketManager


class AsyncServer:
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()
        self.manager = SocketManager(loop=self.loop)

    async def server_loop(self):
        server = AsyncSocket(self.manager)

    def run(self):
        self.loop.run_until_complete(asyncio.gather(
            self.manager.poll(),
            self.server_loop(),
        ))
