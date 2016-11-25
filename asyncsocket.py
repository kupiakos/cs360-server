import socket


class AsyncSocket:
    def __init__(self, manager, sock=None):
        self.manager = manager
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        self.socket = sock
        self.manager.register(self)

    def __await__(self):
        return self.manager.wait(self.socket).__await__()

    async def accept(self):
        await self
        client, address = self.socket.accept()
        return AsyncSocket(self.manager, sock=client), address

    def bind(self, address):
        self.socket.bind(address)

    def listen(self, *args):
        self.socket.listen(*args)

    def fileno(self):
        return self.socket.fileno()

    async def recv(self, size):
        await self
        return self.socket.recv(size)

    def send(self, data):
        return self.socket.send(data)

    def setsockopt(self, *args):
        self.socket.setsockopt(*args)
