import asyncore

from server.tcptunnel import TCPServer
from server.udptunnel import UDPServer

if __name__ == '__main__':
    tcp_server = TCPServer('0.0.0.0', 6666, b'thisIsAKey')
    udp_server = UDPServer('0.0.0.0', 7778)
    asyncore.loop()
