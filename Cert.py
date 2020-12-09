import socket
import threading
import random

class Cert(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.alice_socket  = None
        self.bob_socket = None

    def callback(self,conn,addr):
        print(str(addr) + " is now connected to Cert Authority")
        return

    def open_connection(self):
        HOST = '127.0.0.1'
        PORT = 9000
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print("Cert Authority is now accepting connections at port 9000")
            while(True):
                conn, addr = s.accept()
                x = threading.Thread(target=self.callback, args=(conn,addr))
                x.start()

    def connect_to_alice(self,port):
        cert_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cert_socket.connect(('127.0.0.1', port))
        print("Cert Authority is now connected to Alice ")

    def connect_to_bob(self):
        bob_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bob_socket.connect(('127.0.0.1', 8000))
        print("Cert Authority is now connected to Bob")
    
    def run(self):
        return self.open_connection()
