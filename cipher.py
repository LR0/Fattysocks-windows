import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util import Padding
from constants import PACK_PAD

class AESCipher(object):

    def __init__(self, key): 
        self.bs = 32
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, raw):
        raw = Padding.pad(raw, PACK_PAD)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return iv + cipher.encrypt(raw)

    def decrypt(self, enc):
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        raw = cipher.decrypt(enc[AES.block_size:])
        return Padding.unpad(raw, PACK_PAD)


if __name__ == "__main__":
    cipher = AESCipher(b'12345')
    data = b'0123456789012345678901234567890123456789'
    edata = cipher.encrypt(data)
    print(AES.block_size)
    print(len(edata))