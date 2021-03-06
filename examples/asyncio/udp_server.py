# Based on: UDP server example from:
# https://www.pythonsheets.com/notes/python-asyncio.html 
import asyncio
import socket
import struct
from intuition import parse_datagram

MCAST_ADDR = '224.192.32.19'
MCAST_PORT = 22600

###############################################################################
# Python 3.4 provisionally introduced an asyncio, providing infrastructure for
# futures, tasks, protocols, transports and pluggable event loops in the Python
# Standard Library.

# Python 3.5 introduced the async and await keywords abstracting away the
# underlying coroutine mechanism on which asyncio is constructed, providing
# syntactic sugar for this new style of programming. Python 3.6 provides further
# language support for asynchronous programming with async comprehensions and
# async generators.

# See Video: https://www.youtube.com/watch?time_continue=136&v=M-UcUs7IMIM
# In this session we explore what asyncio is, and demonstrate how to use it to
# to best effect to solve concurrency problems in Python, including advice on
# how to best approach testing of asynchronous Python code.
###############################################################################

loop = asyncio.get_event_loop()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))
sock.setblocking(False)
mreq = struct.pack("4sl", socket.inet_aton(MCAST_ADDR), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# host = 'localhost'
# port = 3553

# sock.bind((host, port))

def recvfrom(loop, sock, n_bytes, fut=None, registed=False):
    fd = sock.fileno()
    if fut is None:
        fut = loop.create_future()
    if registed:
        loop.remove_reader(fd)

    try:
        data, addr = sock.recvfrom(n_bytes)
    except (BlockingIOError, InterruptedError):
        loop.add_reader(fd, recvfrom, loop, sock, n_bytes, fut, True)
    else:
        fut.set_result((data, addr))
    return fut
#  ** NOTE ** async and await keywords maybe new in Python 3.5
async def udp_server(loop, sock):
    while True:
        data, addr = await recvfrom(loop, sock, 1024)
        print(parse_datagram(data))

try:
    loop.run_until_complete(udp_server(loop, sock))
finally:
    loop.close()
