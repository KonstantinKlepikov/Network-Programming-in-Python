import math
import operator
from functools import reduce
from xmlrpc.server import SimpleXMLRPCServer


def main():
    server = SimpleXMLRPCServer(('127.0.0.1', 7001))
    server.register_introspection_functions()
    server.register_multicall_functions()
    server.register_function(addtogether)
    server.register_function(quadratic)
    server.register_function(remote_repr)
    print('Server ready')
    server.serve_forever()


def addtogether(*things):
    """Add together everything in the list `things`."""
    return reduce(operator.add, things)


def quadratic(a, b, c):
    """Determine `x` values satisfying: `a` * x*x + `b` * x + c == 0"""
    b24ac = math.sqrt(b * b - 4.0 * a * c)
    return list(set([(-b - b24ac) / 2.0 * a, (-b + b24ac) / 2.0 * a]))


def remote_repr(arg):
    """Return the `repr()` rendering of the supplied `arg`."""
    return arg


if __name__ == '__main__':
    main()
