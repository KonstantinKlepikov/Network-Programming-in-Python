import socket
import struct
from argparse import ArgumentParser

header_struct = struct.Struct('!I')  # messages up to 2**32 - 1 in length


def recvall(sock: socket.socket, length: int) -> bytes:
    blocks = []
    while length:
        block = sock.recv(length)
        if not block:
            raise EOFError(
                'socket closed with {} bytes left'
                ' in this block'.format(length)
            )
        length -= len(block)
        blocks.append(block)
    return b''.join(blocks)


def get_block(sock: socket.socket) -> bytes:
    data = recvall(sock, header_struct.size)
    (block_length,) = header_struct.unpack(data)
    return recvall(sock, block_length)


def put_block(sock: socket.socket, message: bytes) -> None:
    block_length = len(message)
    sock.send(header_struct.pack(block_length))
    sock.send(message)


def server(address) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(1)
    print('Run this script in another window with "-c" to connect')
    print('Listening at', sock.getsockname())
    sc, sockname = sock.accept()
    print('Accepted connection from', sockname)
    sc.shutdown(socket.SHUT_WR)
    while True:
        block = get_block(sc)
        if not block:
            break
        print('Block says:', repr(block))
    sc.close()
    sock.close()


def client(address) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    sock.shutdown(socket.SHUT_RD)
    put_block(sock, b'Beautiful is better than ugly.')
    put_block(sock, b'Explicit is better than implicit.')
    put_block(sock, b'Simple is better than complex.')
    put_block(sock, b'')
    sock.close()


if __name__ == '__main__':
    parser = ArgumentParser(description='Transmit & receive blocks over TCP')
    parser.add_argument(
        'hostname',
        nargs='?',
        default='127.0.0.1',
        help='IP address or hostname (default: %(default)s)',
    )
    parser.add_argument('-c', action='store_true', help='run as the client')
    parser.add_argument(
        '-p',
        type=int,
        metavar='port',
        default=1060,
        help='TCP port number (default: %(default)s)',
    )
    args = parser.parse_args()
    function = client if args.c else server
    function((args.hostname, args.p))
