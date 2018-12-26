import socket

print('start test tcp')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 7777))
s.send(b'\x01\x0e\xd7\xb1\x26\x00\x50')
s.send(b'GET / HTTP/1.0\r\n\r\n')
data = s.recv(100)
print(data)
input()

print('start test udp')
ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ss.sendto(b'\x01\x08\x08\x08\x08\x00\x35Q+\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03ss1\x05baidu\x03com\x00\x00\x01\x00\x01',
         ('localhost', 7778))
data = ss.recvfrom(65536)
print(data)
input()