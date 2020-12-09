import socket
import threading
import random


class Bob(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.alice_socket  = None
        self.cert_socket = None

    def callback(self,conn,addr):
        print(str(addr) + " is now connected to Bob")
        return

    def open_connection(self):
        HOST = '127.0.0.1'
        PORT = 8000
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print("Bob is now accepting connections at port 8000")
            while(True):
                conn, addr = s.accept()
                x = threading.Thread(target=self.callback, args=(conn,addr))
                x.start()

    def connect_to_alice(self,port):
        alice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        alice_socket.connect(('127.0.0.1', port))
        print("Bob is now connected to Alice")

    def connect_to_cert(self):
        cert_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cert_socket.connect(('127.0.0.1', 9000))
        print("Bob is now connected to Cert Authority")
        
    def run(self):
        return self.open_connection()