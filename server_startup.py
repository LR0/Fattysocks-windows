import asyncore

from server.tcptunnel import TCPServer
from server.udptunnel import UDPServer
from utils import load_tokens

if __name__ == '__main__':
    tokens = load_tokens()
    tcp_server = TCPServer('0.0.0.0', 6666, tokens)
    #udp_server = UDPServer('0.0.0.0', 7778)
    asyncore.loop()
