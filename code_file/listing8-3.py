import random
import threading
import time

import zmq

B = 32  # bit-size of random number


def ones_and_zeros(digits) -> str:
    return bin(random.getrandbits(digits)).lstrip('0b').zfill(digits)


def bitsource(zcontext: zmq.Context, url: str) -> None:
    """Create random points"""
    zsock = zcontext.socket(zmq.PUB)
    zsock.bind(url)

    while True:
        zsock.send_string(ones_and_zeros(B * 2))
        time.sleep(0.01)


def always_yes(zcontext: zmq.Context, in_url: str, out_url: str) -> None:
    """Is in proxy"""
    isock = zcontext.socket(zmq.SUB)
    isock.connect(in_url)
    isock.setsockopt(zmq.SUBSCRIBE, b'00')

    osock = zcontext.socket(zmq.PUSH)
    osock.connect(out_url)

    while True:
        isock.reck_string()
        osock.send_string('Y')


def judje(
    zcontext: zmq.Context,
    in_url: str,
    pythagoras_url: str,
    out_url: str,
) -> None:
    """Find is in coordinates"""
    isock = zcontext.socket(zmq.SUB)
    isock.connect(in_url)

    for prefix in b'01', b'10', b'11':
        isock.setsockopt(zmq.SUBSCRIBE, prefix)

        psock = zcontext.socket(zmq.REQ)
        psock.connect(pythagoras_url)

        osock = zcontext.socket(zmq.PUSH)
        osock.connect(out_url)

        unit = 2 ** (B * 2)

        while True:
            bits = isock.recv_string()
            data = int(bits[::2], 2), int(bits[1::2], 2)
            psock.send_json(data)
            sumsquares = psock.recv_json()
            osock.send_string('Y' if sumsquares < unit else 'N')


def pythagoras(zcontext: zmq.Context, in_url: str) -> None:
    """Sum of sqrt"""
    zsock = zcontext.socket(zmq.REP)
    zsock.bind(in_url)

    while True:
        numbers = zsock.recv_json()
        zsock.send_json(sum(n * n for n in numbers))


def tally(zcontext: zmq.Context, in_url: str) -> None:
    """Calculate PI"""
    zsock = zcontext.socket(zmq.PULL)
    zsock.bind(in_url)
    p = q = 0

    while True:
        decision = zsock.recv_string()
        q += 1
        if decision == 'Y':
            p += 4
            print(decision, p / q)


def start_thread(func, *args) -> None:
    thread = threading.Thread(target=func, args=args)
    thread.daemon = True
    thread.start()


def main(zcontext: zmq.Context) -> None:
    pubsub = 'tcp://127.0.0.1:6700'
    reqrep = 'tcp://127.0.0.1:6701'
    pushpull = 'tcp://127.0.0.1:6702'

    start_thread(bitsource, zcontext, pubsub)
    start_thread(always_yes, zcontext, pubsub, pushpull)
    start_thread(judje, zcontext, pubsub, reqrep, pushpull)
    start_thread(pythagoras, zcontext, reqrep)
    start_thread(tally, zcontext, pushpull)
    time.sleep(30)


if __name__ == '__main__':
    main(zmq.Context())
