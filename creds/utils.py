import os
import binascii


def create_token(size=40):
    return binascii.hexlify(os.urandom(int(size/2))).decode('ascii')
