import asyncio
import io
import select
from selectors import BaseSelector, SelectorKey
from typing import Union


class AsyncEpollSelector(BaseSelector):
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._poller = select.epoll()
        self._options = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
        self._futures = {}
        self._registered = set()
        self.timeout = 1
        self.closed = False
        self._

    # def _get_fut(self, fd):
    #     """Get the waiting future for a file descriptor or create one."""
    #     return self._futures.setdefault(
    #         fd, asyncio.Future(loop=self.loop))
    #
    # def register(self, sock):
    #     self._registered.add(sock.fileno())
    #     self._poller.register(sock, self._options)
    #
    # @coroutine
    # def poll_one(self):
    #     yield
    #     events = self._poller.poll(timeout=self.timeout)
    #     for fd, event in events:
    #         if fd not in self._futures:
    #             continue
    #         fut = self._futures[fd]
    #         if event & (select.POLLHUP | select.POLLERR):
    #             fut.set_exception(IOError('Socket hangup or error'))
    #         else:
    #             # Data is ready
    #             fut.set_result(True)
    #         del self._futures[fd]
    #         # Cooperative multitasking
    #         yield
    #
    # @coroutine
    # def poll(self):
    #     while True:
    #         yield from self.poll_one()
    #
    # def wait(self, sock):
    #     if sock.fileno() not in self._registered:
    #         raise IOError('Cannot wait on non-registered socket')
    #     return self._get_fut(sock.fileno())

    def close(self):
        self._poller.close()

    def get_map(self):
        pass

    def register(self, fileobj: Union[int, io.IOBase], events: int, data=None):
        if self.closed:
            raise IOError('Cannot register into closed selector!')
        if hasattr(fileobj, 'fileno'):
            fd = fileobj.fileno()
        else:
            fd = fileobj
            fileobj = None
        key = SelectorKey(fileobj, fd, [], data)
        self._poller.register(fd, events)

    def select(self, timeout=None):
        if self.closed:
            raise IOError('Cannot select from closed selector!')
        events = self._poller.poll(timeout)
        

    async def select_loop(self, loop: asyncio.AbstractEventLoop = None):
        pass

    def unregister(self, fileobj):
        pass
