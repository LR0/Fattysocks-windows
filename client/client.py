import asyncore
import threading
from client.tcplocal import TCPLocal

class Client:
    def __init__(self, lport, addr, port, user):
        self.addr = addr
        self.port = port
        self.lport = lport
        self.user = user

    def run(self):
        self.thread = threading.Thread(target=self.process_client)
        self.thread.start()

    def stop(self):
        try:
            self.tcp_server.stop()
        except asyncore.ExitNow:
            asyncore.close_all()

    def process_client(self):
        self.tcp_server = TCPLocal('localhost', self.lport, self.addr, self.port, self.user, b'thisIsAKey')
        try:
            asyncore.loop()
        except asyncore.ExitNow:
            asyncore.close_all()
        