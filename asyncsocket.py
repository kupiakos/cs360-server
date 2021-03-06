import select
import socket

from asyncselectors import AsyncEpollSelector


class AsyncSocket:
    def __init__(self, selector: AsyncEpollSelector, sock=None, timeout=True):
        self.selector = selector
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        self.socket = sock
        self.selector.register(self.fileno(), select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR, timeout=timeout)

    def __await__(self):
        return self.selector.wait(self.socket.fileno()).__await__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()
        return exc_type is not None

    async def accept(self):
        await self
        client, address = self.socket.accept()
        return AsyncSocket(self.selector, sock=client), address

    def bind(self, address):
        self.socket.bind(address)

    def close(self):
        self.socket.close()

    def listen(self, *args):
        self.socket.listen(*args)

    def fileno(self):
        return self.socket.fileno()

    async def recv(self, size):
        await self
        return self.socket.recv(size)

    async def recv_into(self, buffer, *args):
        await self
        return self.socket.recv_into(buffer, *args)

    def send(self, data):
        return self.socket.send(data)

    def sendall(self, data):
        return self.socket.sendall(data)

    def setsockopt(self, *args):
        self.socket.setsockopt(*args)
