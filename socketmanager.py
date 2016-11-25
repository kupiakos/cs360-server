import asyncio
import select

from types import coroutine


class SocketManager:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._poller = select.epoll()
        self._options = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
        self._futures = {}
        self._registered = set()
        self.timeout = 1

    def _get_fut(self, fd):
        """Get the waiting future for a file descriptor or create one."""
        return self._futures.setdefault(
            fd, asyncio.Future(loop=self.loop))

    def register(self, sock):
        self._registered.add(sock.fileno())
        self._poller.register(sock, self._options)

    @coroutine
    def poll_one(self):
        yield
        events = self._poller.poll(timeout=self.timeout)
        for fd, event in events:
            if fd not in self._futures:
                continue
            fut = self._futures[fd]
            if event & (select.POLLHUP | select.POLLERR):
                fut.set_exception(IOError('Socket hangup or error'))
            else:
                # Data is ready
                fut.set_result(True)
            del self._futures[fd]
            # Cooperative multitasking
            yield

    @coroutine
    def poll(self):
        while True:
            yield from self.poll_one()

    def wait(self, sock):
        if sock.fileno() not in self._registered:
            raise IOError('Cannot wait on non-registered socket')
        return self._get_fut(sock.fileno())
