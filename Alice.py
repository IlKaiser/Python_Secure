import random
import socket
import threading
import pickle

from datetime import datetime
from dateutil import parser

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Util import Padding
from Crypto.Random import get_random_bytes

from Utils import pad,unpad


class Alice(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.bob_socket  = None
        self.cert_socket = None
        self.timestamp   = None
        self.HOST = '127.0.0.1'
        self.PORT = random.randrange(1024,65536)
        self.key_pair    = self.__gen_key_pair()
        self.b_ticket    = []
        self.c_pub_key   = None
        self.ab_key      = get_random_bytes(16)

    def callback(self,conn,addr):
        print("[Alice]"+str(addr) + " is now connected to Alice")
        data = unpad(conn.recv(2000))
        if(data == b'Bob'):
            cipher     = AES.new(self.ab_key, AES.MODE_ECB)
            timestamp_c = conn.recv(16)
            timestamp_d = parser.parse(Padding.unpad(cipher.decrypt(timestamp_c),AES.block_size).decode())
            assert(timestamp_d.strftime("%H:%M:%S")==self.timestamp.strftime("%H:%M:%S"))
            print("[Alice] You are Bob 100% sure")
        return

    def open_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.HOST, self.PORT))
            s.listen()
            print("[Alice] Now accepting connections at port "+str(self.PORT))
            while(True):
                conn, addr = s.accept()
                x = threading.Thread(target=self.callback, args=(conn,addr))
                x.start()

    def connect_to_cert(self):
        cert_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cert_socket.connect(('127.0.0.1', 9000))
        print("[Alice] Now connected to Cert Authority")
        cert_socket.send(pad(b'Alice on '+bytes(str(self.PORT),"utf-8")))
        b = cert_socket.recv(2000)
        b = unpad(b)
        if(b == b'send'):
            cert_socket.send(pad(self.key_pair.publickey().export_key()))
            b=unpad(cert_socket.recv(2000))
        if(b == b'nonce,ts'):
            nonce = random.randint(1,20000)
            timestamp = datetime.now()
            self.timestamp = timestamp
            cert_socket.send(pad(bytes(str(nonce)+","+format(timestamp),"utf-8")))
        try:
            cipher_rsa = PKCS1_OAEP.new(self.key_pair)
        
            ## my nonce
            nonce_c        = cert_socket.recv(256)
            ## my timestamp
            timestamp_c    = cert_socket.recv(256)
            ## c pub key
            self.c_pub_key = RSA.import_key(unpad(cert_socket.recv(2000)))
            ## checksum
            checksum       = cert_socket.recv(256)
            
            # check integrity
            nonce_d        = cipher_rsa.decrypt(nonce_c)
            timestamp_d    = parser.parse(cipher_rsa.decrypt(timestamp_c).decode())
            hash_object    = SHA256.new(data=nonce_c)
            hash_object.update(data=timestamp_c)
            
            assert(int(nonce_d)==nonce)
            assert(hash_object.digest() == checksum)
            assert(timestamp_d.strftime("%H:%M:%S")==timestamp.strftime("%H:%M:%S"))

            ## Send Symmetric-Key to C and wait for Bob
            cipher_rsa_c = PKCS1_OAEP.new(self.c_pub_key)
            cert_socket.send(cipher_rsa_c.encrypt(self.ab_key))
        except:
            print("[Alice] See Ya")
            return
        print("[Alice] wait for Bob")
        return

    
    def __gen_key_pair(self):
        return RSA.generate(2048)

    def run(self):
        assert self.key_pair is not None
        return self.open_connection()