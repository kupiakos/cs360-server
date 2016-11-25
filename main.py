import asyncio
import socket

from .asyncsocket import AsyncSocket
from .socketmanager import SocketManager


async def echo_server(manager):
    server = AsyncSocket(manager)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    server.bind(('localhost', 9005))
    server.listen(5)
    print('Starting echo server...')
    while True:
        client, address = await server.accept()
        print('Connected:', address)
        asyncio.get_event_loop().create_task(
            echo_client(client))


async def echo_client(client):
    print('Starting echo client', client.fileno())
    while True:
        data = await client.recv(2048)
        print('Client', client.fileno(), 'received', repr(data))
        if not data:
            break
        client.send(data)


def main():
    manager = SocketManager()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        manager.poll(), echo_server(manager)))


if __name__ == '__main__':
    main()
