import asyncore
import socket

from utils import LOGGER
from constants import UDP_SIZE


class UDPServer(asyncore.dispatcher):

    sess_list = []

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind((host, port))

    def handle_read(self):
        data, addr = self.socket.recvfrom(UDP_SIZE)
        LOGGER.info('udp local recv(%s): %s', repr(addr), data)
        remote = RemoteSession(addr, data, self.socket)
        remote.local = self
        self.sess_list.append(remote)


class RemoteSession(asyncore.dispatcher):
    client_addr = None
    target_addr = None
    target_port = None
    send_data = None
    local = None

    def __init__(self, addr, data, ss):
        asyncore.dispatcher.__init__(self)
        self.client_addr = addr
        atyp = data[0]

        if atyp == 1:
            self.target_addr = '.'.join([str(data[1]), str(data[2]), str(data[3]), str(data[4])])
            self.target_port = data[5] * 256 + data[6]
            self.send_data = data[7:]
            self.header = data[:7]
        # TODO: atyp == 3,4
        else:
            LOGGER.info("%s udp remote target addr: error!!! %d", id(self), atyp)
            return
        LOGGER.info("%s udp remote target addr: %s:%d", id(self), self.target_addr, self.target_port)
        self.ss = ss
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)

    def writeble(self):
        return self.send_data is not None

    def handle_write(self):
        if self.send_data:
            print("client handle write: ", self.send_data)
            self.socket.sendto(self.send_data, (self.target_addr, self.target_port))
            self.send_data = None

    def handle_close(self):
        self.close()
        if self.local and self in self.local.sess_list:
            self.local.sess_list.remove(self)

    def handle_read(self):
        data, addr = self.socket.recvfrom(UDP_SIZE)
        print("%s udp remote recv: %s", id(self), data)
        self.ss.sendto(self.header + data, self.client_addr)
        print("%s udp remote return to addr: %s", id(self), self.client_addr)
        self.handle_close()
