import random
import socket
import threading
import time

from datetime import datetime
from dateutil import parser

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Util import Padding
from Crypto.PublicKey import RSA

from Utils import pad,unpad



class Bob(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.c_pub_key     = None
        self.alice_socket  = None
        self.cert_socket   = None
        self.ab_key        = None
        self.a_timestamp   = None
        self.key_pair      = self.__gen_key_pair()

    def callback(self,conn,addr):
        print("[Bob]"+str(addr) + " is now connected to Bob")
        cipher_rsa     = PKCS1_OAEP.new(self.key_pair)
        # Bob wants only to talk with Alice or Cert
        who = unpad(conn.recv(2000))
        if(who == b'Cert'):
            try:
                ## Recive AB Key and check everything
                self.ab_key     = cipher_rsa.decrypt(conn.recv(256))
                self.a_timestamp  = parser.parse(cipher_rsa.decrypt(conn.recv(256)).decode())
                alice_port = int(cipher_rsa.decrypt(conn.recv(256)).decode())
                # One minute tollerance
                assert(datetime.now().strftime("%H:%M")==self.a_timestamp.strftime("%H:%M"))
                print("[Bob] Got AB_key ")
                print("[Bob] Got Alice port")
                ## To Alice
                self.connect_to_alice(alice_port)
            except:
                print("[Bob] Never saw you around")
        elif(who == b'Alice'):
            print("[Bob] wait for me Alice")
        else:
            print("[Bob] i dont know u, see ya")
            return
        return

    def open_connection(self):
        HOST = '127.0.0.1'
        PORT = 8000
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print("[Bob] Now accepting connections at port 8000")
            while(True):
                conn, addr = s.accept()
                x = threading.Thread(target=self.callback, args=(conn,addr))
                x.start()

    def connect_to_alice(self,port):
        alice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        alice_socket.connect(('127.0.0.1', port))
        alice_socket.send(pad(b'Bob'))
        cipher       = AES.new(self.ab_key, AES.MODE_ECB)
        timestamp_to_a = cipher.encrypt(Padding.pad(self.a_timestamp.strftime("%H:%M:%S").encode(),AES.block_size))
        alice_socket.send(timestamp_to_a)
        time.sleep(0.1)
        print("[Bob] Now connected to Alice")

    def connect_to_cert(self):
        cert_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cert_socket.connect(('127.0.0.1', 9000))
        print("[Bob] Now connected to Cert Authority")
        cert_socket.send(pad(b'Bob'))
        mess = cert_socket.recv(2000)
        mess = unpad(mess)
        if(mess == b'send'):
            cert_socket.send(pad(self.key_pair.publickey().export_key()))
        return
        
    def __gen_key_pair(self):
        return RSA.generate(2048)

    def run(self):
        assert self.key_pair is not None
        return self.open_connection()