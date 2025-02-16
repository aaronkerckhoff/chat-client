import socket
import time

class ClientSocket:

    def spam_connect(self, ip, port):
        while True:
            try:
                self.sock.connect((ip, port))
                break
            except:
                print("Connecting to server failed, retrying in 5")
                time.sleep(5)

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.spam_connect(ip, port)
        self.queued_messages = []
        print("connected!")
    def send(self, data: bytes):
        self.sock.sendall(data)



    def receive_message(self):
        if len(self.queued_messages) > 0:
            return self.queued_messages.pop(0)
        buffer = b''
        self.sock.setblocking(False)
        while True:
            try:
                data = self.sock.recv(4096)
            except BlockingIOError:
                break
            if not data:
                # Connection closed
                break
            buffer += data

        if len(buffer) == 0:
            return None
        
        for message in buffer.split(b'\n'):
            self.queued_messages.append(message)

        return self.queued_messages.pop(0)

