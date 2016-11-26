from asyncsocket import AsyncSocket
from server import AsyncServer


class EchoServer(AsyncServer):
    async def handle_client(self, client: AsyncSocket):
        print('Starting echo client', client.fileno())
        while True:
            data = await client.recv(2048)
            print('Client', client.fileno(), 'received', repr(data))
            if not data:
                break
            client.send(data)


def main():
    server = EchoServer()
    server.run(('localhost', 8085))


if __name__ == '__main__':
    main()
