import asyncore

from client.tcplocal import TCPLocal

if __name__ == '__main__':
    #tcp_server = TCPLocal('localhost', 1081, 'localhost', 7777, '18551828004', b'thisIsAKey')
    tcp_server = TCPLocal('localhost', 1081, 'www.nxyexiong.xyz', 6666, '18551828004', b'thisIsAKey')
    asyncore.loop()
