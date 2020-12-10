import socket
import threading
import random
import re 
from datetime import datetime
from dateutil import parser
from Utils import pad,unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

class Cert(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.alice_socket  = None
        self.alice_port    = None
        self.bob_socket    = None
        self.alice_pub_key = None
        self.sem        = threading.Semaphore(value=0)
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
                print("[Auth]Got ts: "+timestamp)
                date_time_obj = parser.parse(timestamp)
                print("[Auth] diff"+str((date_time_obj - time_now).seconds))
            except:
                return

            ## Send back Ticket to B,Encrypted Nonce and Timestamp
            cipher_rsa_ac = PKCS1_OAEP.new(self.alice_pub_key)
            cipher_rsa_bc = PKCS1_OAEP.new(self.bob_pub_key)
            if ((date_time_obj - time_now).seconds < 10):
                nonce_c     = cipher_rsa_ac.encrypt(bytes(nonce,"utf-8"))
                ab_key      = b'Sixteen byte key'
                b_ticket    = cipher_rsa_bc.encrypt(ab_key)
                self.alice_socket.send(b_ticket)
                self.alice_socket.send(nonce_c)
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
    
    def run(self):
        return self.open_connection()
