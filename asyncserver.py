from asyncsocket import AsyncSocket
from server import AsyncServer


class EchoServer(AsyncServer):
    async def handle_client(self, client: AsyncSocket):
        print('Starting echo client', client.fileno())
        while True:
            data = await client.recv(2048)
            if not data:
                break
            print('Client', client.fileno(), 'received', repr(data))
            if not data:
                break
            client.send(data)
        print('Finished client', client.fileno())
