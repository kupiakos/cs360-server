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


class HttpServer(AsyncServer):
    async def handle_client(self, client: AsyncSocket):
        data = b'Hello world!'
        response = (
            b'HTTP/1.1 200 OK\r\n' +
            b'Content-Length: %d\r\n' % len(data) +
            b'Content-Type: text/html\r\n'
            b'\r\n' + data
        )
        await client.recv(4096)
        client.sendall(response)


def main():
    # import asyncio
    # asyncio.get_event_loop().set_debug(True)
    server = HttpServer()
    server.run(('localhost', 8085), timeout=2)


if __name__ == '__main__':
    main()
