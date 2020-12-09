import socket
import threading
import random

class Alice(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.bob_socket  = None
        self.cert_socket = None

    def callback(self,conn,addr):
        print(str(addr) + " is now connected to Alice")
        return

    def open_connection(self):
        HOST = '127.0.0.1'
        PORT = random.randrange(1024,65536)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print("Alice is now accepting connections at port "+str(PORT))
            while(True):
                conn, addr = s.accept()
                x = threading.Thread(target=self.callback, args=(conn,addr))
                x.start()

    def connect_to_bob(self):
        bob_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bob_socket.connect(('127.0.0.1', 8000))
        print("Alice is now connected to Bob")

    def connect_to_cert(self):
        cert_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cert_socket.connect(('127.0.0.1', 9000))
        print("Alice is now connected to Cert Authority")
    def run(self):
        return self.open_connection()


