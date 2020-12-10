import socket
import threading
import random
import pickle
from datetime import datetime
from Utils import pad,unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

class Alice(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.bob_socket  = None
        self.cert_socket = None
        self.HOST = '127.0.0.1'
        self.PORT = random.randrange(1024,65536)
        self.key_pair    = self.__gen_key_pair()

    def callback(self,conn,addr):
        print("[Alice]"+str(addr) + " is now connected to Alice")
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

    def connect_to_bob(self):
        bob_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bob_socket.connect(('127.0.0.1', 8000))
        print("[Alice] Now connected to Bob")

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
            cert_socket.send(pad(bytes(str(nonce)+","+format(timestamp),"utf-8")))
        try:
            b_ticket   = cert_socket.recv(256)
            nonce_c    = cert_socket.recv(256)
            print("[Alice] got s**t")
            print("[Alice] nonce_c "+str(nonce_c))
            cipher_rsa = PKCS1_OAEP.new(self.key_pair)
            nonce_d = cipher_rsa.decrypt(nonce_c)
            print(nonce_d)
            print(int(nonce_d)==nonce)
        except AttributeError as err:
            print(format(err))
            print("[Alice] See Ya")
            return
        except ValueError as err:
            print(format(err))
            print("[Alice] See Ya")
            return
        return

    
    def __gen_key_pair(self):
        return RSA.generate(2048)

    def run(self):
        assert self.key_pair is not None
        return self.open_connection()