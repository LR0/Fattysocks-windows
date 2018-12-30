import asyncore
import socket
import hashlib
import os

from utils import LOGGER
from constants import BUF_SIZE, STAGE_HANDSHAKE, STAGE_STREAM, STAGE_INIT, MAGIC_LEN, PACK_PAD_LEN
from cipher import AESCipher


class TCPLocal(asyncore.dispatcher):
    server_addr = None
    server_port = None
    token = None
    conn_list = []

    def __init__(self, localhost, localport, serverhost, serverport, user):
        asyncore.dispatcher.__init__(self)
        self.server_addr = serverhost
        self.server_port = serverport
        self.token = hashlib.sha1(user.encode('utf-8')).digest()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((localhost, localport))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            LOGGER.info('incoming connection from %s', repr(addr))
            handler = LocalConnection(sock)
            handler.server = self
            self.conn_list.append(handler)

    def stop(self):
        for item in self.conn_list:
            if item.remote:
                item.remote.handle_close()
            else:
                item.handle_close()
        self.handle_close()
        raise asyncore.ExitNow('TCPLocal.stop()')


class LocalConnection(asyncore.dispatcher):

    buffer_recv = b''
    buffer_send = b''
    server = None
    remote = None
    stage = STAGE_INIT

    def handle_read(self):
        data = self.recv(BUF_SIZE)
        if not data:
            return
        self.buffer_recv += data
        #LOGGER.debug('%s local recv %s', id(self), data)
        while True:
            if self.stage == STAGE_INIT:
                if len(self.buffer_recv) < 3:
                    return
                ver = self.buffer_recv[0]
                nmethod = self.buffer_recv[1]
                method = self.buffer_recv[2]
                if ver != 5 or nmethod != 1 or method != 0:
                    self.handle_close()
                    LOGGER.error("error init data: ver=%d, nmethod=%d, method=%d", ver, nmethod, method)
                    return
                self.buffer_recv = self.buffer_recv[3:]
                self.buffer_send += b'\x05\x00'
                self.stage = STAGE_HANDSHAKE
                continue
            elif self.stage == STAGE_HANDSHAKE:
                if len(self.buffer_recv) < 4:
                    return
                ver = self.buffer_recv[0]
                cmd = self.buffer_recv[1]
                rsv = self.buffer_recv[2]
                atyp = self.buffer_recv[3]
                if ver != 5 or cmd != 1 or rsv != 0 or (atyp != 1 and atyp != 3):
                    self.handle_close()
                    LOGGER.error("error handshake data: ver=%d, cmd=%d, rsv=%d, atyp=%d", ver, cmd, rsv, atyp)
                    return
                addr = ""
                port = 0
                if atyp == 1:
                    if len(self.buffer_recv) < 7:
                        return
                    addr = str(self.buffer_recv[4]) + '.' + str(self.buffer_recv[5]) + \
                        '.' + str(self.buffer_recv[6]) + '.' + str(self.buffer_recv[7])
                    port = self.buffer_recv[8] * 256 + self.buffer_recv[9]
                    self.buffer_send += b'\x05\x00\x00\x01' + self.buffer_recv[4:10]
                elif atyp == 3:
                    alen = self.buffer_recv[4]
                    if len(self.buffer_recv) < 5 + alen + 2:
                        return
                    addr = self.buffer_recv[5:5 + alen].decode('utf-8')
                    port = self.buffer_recv[5 + alen] * 256 + self.buffer_recv[5 + alen + 1]
                    self.buffer_send += b'\x05\x00\x00\x03' + self.buffer_recv[4:5 + alen + 3]
                LOGGER.info('%s local handshake: %s:%d', id(self), addr, port)
                self.remote = RemoteConnection(self.server.server_addr, self.server.server_port, self.server.token)
                self.remote.local = self
                self.remote.buffer_send_raw += self.buffer_recv[3:]  # include atyp + addr + port
                self.buffer_recv = b''
                self.stage = STAGE_STREAM
                continue
            elif self.stage == STAGE_STREAM:
                self.remote.buffer_send_raw += self.buffer_recv
                self.buffer_recv = b''
            return

    def writable(self):
        return (len(self.buffer_send) > 0)

    def handle_write(self):
        sent = self.send(self.buffer_send)
        #LOGGER.debug('%s local send %s', id(self), self.buffer_send[:sent])
        self.buffer_send = self.buffer_send[sent:]

    def handle_close(self):
        LOGGER.info('%s local close', id(self))
        if self in self.server.conn_list:
            self.server.conn_list.remove(self)
        self.close()


class RemoteConnection(asyncore.dispatcher):

    buffer_send_raw = b''
    buffer_send = b''
    buffer_recv_raw = b''
    buffer_recv = b''
    local = None
    cipher = None

    def __init__(self, host, port, token):
        asyncore.dispatcher.__init__(self)
        self.buffer_send_raw += token
        magic = bytearray(os.urandom(MAGIC_LEN))
        self.buffer_send_raw += magic
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.cipher = AESCipher()

    def handle_connect(self):
        pass

    def handle_close(self):
        LOGGER.info('%s remote close', id(self))
        self.local.handle_close()
        self.close()

    def handle_read(self):
        data = self.recv(BUF_SIZE)
        #LOGGER.debug('%s remote recv: %s', id(self), data)
        self.buffer_recv += data
        ddata, dlen = self.cipher.decrypt_all(self.buffer_recv)
        self.buffer_recv_raw += ddata
        self.buffer_recv = self.buffer_recv[dlen:]
        if len(self.buffer_recv_raw) > 0:
            self.local.buffer_send += self.buffer_recv_raw
            self.buffer_recv_raw = b''

    def writable(self):
        if len(self.buffer_send_raw) > 0:
            self.buffer_send += self.cipher.encrypt_all(self.buffer_send_raw)
            self.buffer_send_raw = b''
        return (len(self.buffer_send) > 0)

    def handle_write(self):
        sent = self.send(self.buffer_send)
        #LOGGER.debug('%s remote send %s', id(self), self.buffer[:sent])
        self.buffer_send = self.buffer_send[sent:]
