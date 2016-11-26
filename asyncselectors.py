import asyncio
import io
import select
from asyncio.futures import Future
from selectors import BaseSelector, SelectorKey
from typing import Union, Mapping, List, Tuple


class AsyncEpollSelector(BaseSelector):
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()
        self._poller = select.epoll()
        self._futures = {}
        self.closed = False
        self._keys = {}

    def close(self):
        self._poller.close()
        self.closed = True
        self._keys = {}

    def get_map(self) -> Mapping[int, SelectorKey]:
        return self._keys

    def register(self, fileobj: Union[int, io.IOBase], events: int, data=None):
        if self.closed:
            raise IOError('Cannot register into closed selector!')
        fd = fileobj.fileno() if hasattr(fileobj, 'fileno') else fileobj
        value = SelectorKey(fileobj, fd, 0, data)
        self._poller.register(fd, events)
        self._keys[fd] = value

    def select(self, timeout=None) -> List[Tuple[SelectorKey, int]]:
        if self.closed:
            raise IOError('Cannot select from closed selector!')
        result = []
        try:
            events = self._poller.poll(timeout)
        except InterruptedError:
            return result
        for fd, event in events:
            if fd not in self._keys:
                raise IOError('No registration for received event {}, {}'.format(fd, event))
            key = self._keys[fd]
            key = SelectorKey(
                key.fileobj,
                key.fd,
                key.events | event,
                key.data,
            )
            self._keys[fd] = key
            result.append((key, event))
        return result

    @asyncio.coroutine
    def poll(self, rate=None):
        """Loop through the results of select, setting and clearing futures as needed"""
        rate = rate or 0.3
        while True:
            # Cooperative multitasking
            yield
            events = self.select(rate)
            for key, event in events:
                fd = key.fd
                if fd not in self._futures:
                    continue
                fut = self._futures[fd]
                if event & (select.POLLHUP | select.POLLERR):
                    fut.set_exception(IOError('Socket hangup or error'))
                else:
                    # Data is ready
                    fut.set_result(True)
                del self._futures[fd]

    def unregister(self, fileobj: Union[int, io.IOBase]):
        fd = fileobj.fileno() if hasattr(fileobj, 'fileno') else fileobj
        self._poller.unregister(fd)
        del self._keys[fileobj]
        if fd in self._futures:
            self._futures[fd].cancel()

    def wait(self, fileobj: Union[int, io.IOBase]) -> Future:
        """Return a future which will be set when an event is detected in the event loop"""
        fd = fileobj.fileno() if hasattr(fileobj, 'fileno') else fileobj
        if fd not in self._keys:
            raise IOError('Cannot wait on non-registered socket')
        return self._futures.setdefault(
            fd, self.loop.create_future())
