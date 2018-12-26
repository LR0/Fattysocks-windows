import asyncore
import socket

from utils import LOGGER
from constants import BUF_SIZE, STAGE_HANDSHAKE, STAGE_STREAM, STAGE_INIT, TOKEN_LEN


class TCPServer(asyncore.dispatcher):

    conn_list = []

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            LOGGER.info('incoming connection from %s', repr(addr))
            handler = LocalConnection(sock)
            handler.server = self
            self.conn_list.append(handler)


class LocalConnection(asyncore.dispatcher):

    buffer = b''
    server = None
    remote = None
    stage = STAGE_INIT

    def handle_read(self):
        data = self.recv(BUF_SIZE)
        if not data:
            return
        self.buffer += data
        #LOGGER.debug('%s local recv %s', id(self), data)
        while True:
            if self.stage == STAGE_INIT:
                if len(self.buffer) < TOKEN_LEN:
                    return
                token = self.buffer[0:TOKEN_LEN]
                LOGGER.info("accept token: %s", token.hex())
                self.buffer = self.buffer[TOKEN_LEN:]
                self.stage = STAGE_HANDSHAKE
                continue
            elif self.stage == STAGE_HANDSHAKE:
                if len(self.buffer) < 1:
                    return
                atyp = self.buffer[0]
                addr = ""
                port = 0
                if atyp == 1:
                    if len(self.buffer) < 7:
                        return
                    addr = str(self.buffer[1]) + '.' + str(self.buffer[2]) + \
                        '.' + str(self.buffer[3]) + '.' + str(self.buffer[4])
                    port = self.buffer[5] * 256 + self.buffer[6]
                    self.buffer = self.buffer[7:]
                elif atyp == 3:
                    if len(self.buffer) < 2:
                        return
                    alen = self.buffer[1]
                    if len(self.buffer) < 2 + alen + 2:
                        return
                    addr = self.buffer[2:2 + alen].decode('utf-8')
                    port = self.buffer[2 + alen] * 256 + self.buffer[2 + alen + 1]
                    self.buffer = self.buffer[2 + alen + 2:]
                LOGGER.info('%s local handshake: %s:%d', id(self), addr, port)
                self.remote = RemoteConnection(addr, port)
                self.remote.local = self
                self.remote.buffer += self.buffer
                self.buffer = b''
                self.stage = STAGE_STREAM
                continue
            elif self.stage == STAGE_STREAM:
                self.remote.buffer += self.buffer
                self.buffer = b''
            return

    def writable(self):
        return (len(self.buffer) > 0 and self.stage == STAGE_STREAM)

    def handle_write(self):
        sent = self.send(self.buffer)
        #LOGGER.debug('%s local send %s', id(self), self.buffer[:sent])
        self.buffer = self.buffer[sent:]

    def handle_close(self):
        LOGGER.info('%s local close', id(self))
        if self in self.server.conn_list:
            self.server.conn_list.remove(self)
        self.close()


class RemoteConnection(asyncore.dispatcher):

    buffer = b''
    local = None

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def handle_connect(self):
        pass

    def handle_close(self):
        LOGGER.info('%s remote close', id(self))
        self.local.handle_close()
        self.close()

    def handle_read(self):
        data = self.recv(BUF_SIZE)
        #LOGGER.debug('%s remote recv: %s', id(self), data)
        self.local.buffer += data

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        sent = self.send(self.buffer)
        #LOGGER.debug('%s remote send %s', id(self), self.buffer[:sent])
        self.buffer = self.buffer[sent:]
