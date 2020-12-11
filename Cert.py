import random
import socket
import threading
import re 

from datetime import datetime
from dateutil import parser

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from Utils import pad,unpad


class Cert(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.key_pair      = self.__gen_key_pair()
        self.alice_socket  = None
        self.alice_port    = None
        self.bob_socket    = None
        self.alice_pub_key = None
        self.bob_pub_key   = None
        

    def callback(self,conn,addr):
        print("[Auth]"+str(addr) + " is now connected to Cert Authority")
        data = conn.recv(2000)
        data = unpad(data)
        decoded = data.decode("utf-8")
        ## If ALICE
        if(re.match(r'Alice on [0-9]{4,5}',decoded)):

            ## Handshake
            self.alice_port   = int(decoded.split("on")[1])
            self.alice_socket = conn
            self.alice_socket.send(pad(b'send'))
            self.alice_pub_key = RSA.import_key(unpad(self.alice_socket.recv(2000)))
            print("[Auth] got alice key")

            ## Recive Nonce and Timestamp
            time_now = datetime.now()
            self.alice_socket.send(pad(b'nonce,ts'))

            mess = self.alice_socket.recv(2000)
            
            try:
                nonce = mess.decode("utf-8").split(",")[0] 
                timestamp = mess.decode("utf-8").split(",")[1] 
                date_time_obj = parser.parse(timestamp)
                hms = date_time_obj.strftime("%H:%M:%S")
            except:
                print("[Auth] Timeout Expired")
                return    

            ## Send back Encrypted Nonce and Timestamp and my pub_key
            cipher_rsa_c = PKCS1_OAEP.new(self.key_pair)
            cipher_rsa_ac = PKCS1_OAEP.new(self.alice_pub_key)
            cipher_rsa_bc = PKCS1_OAEP.new(self.bob_pub_key)
            if ((date_time_obj - time_now).seconds < 10):
                

                nonce_c     = cipher_rsa_ac.encrypt(bytes(nonce,"utf-8"))
                a_timestamp = cipher_rsa_ac.encrypt(format(hms).encode())
                c_pub_key   = self.key_pair.publickey().export_key()

                hash_object = SHA256.new(data=nonce_c)
                hash_object.update(data=a_timestamp)
                
                self.alice_socket.send(nonce_c)
                self.alice_socket.send(a_timestamp)
                self.alice_socket.send(pad(c_pub_key))
                self.alice_socket.send(hash_object.digest())

                ## Reciva AB key from A
                ab_key_enc = self.alice_socket.recv(256)
                ab_key     = cipher_rsa_c.decrypt(ab_key_enc)
                print("[Auth] recvd key from Alice")

                ## Send AB Key and TS To bob
                self.bob_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.bob_socket.connect(('127.0.0.1', 8000))
                self.bob_socket.send(pad(b'Cert'))
                self.bob_socket.send(cipher_rsa_bc.encrypt(ab_key))
                self.bob_socket.send(cipher_rsa_bc.encrypt(hms.encode()))
                self.bob_socket.send(cipher_rsa_bc.encrypt(str(self.alice_port).encode()))

            else:
                print("[Auth] Timeout Expired")
                return    
            return
        elif(decoded == 'Bob'):
            self.bob_socket = conn
            self.bob_socket.send(pad(b'send'))
            self.bob_pub_key = RSA.import_key(unpad(self.bob_socket.recv(2000)))
            print("[Auth] got bob key")
            return
        else:
            print("[Auth] Not identified! closing connection")
            return
        return

    def open_connection(self):
        HOST = '127.0.0.1'
        PORT = 9000
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print("[Auth] Now accepting connections at port 9000")
            while(True):
                conn, addr = s.accept()
                x = threading.Thread(target=self.callback, args=(conn,addr))
                x.start()

    def __gen_key_pair(self):
        return RSA.generate(2048)

    def run(self):
        assert self.key_pair is not None
        return self.open_connection()
