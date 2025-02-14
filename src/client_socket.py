import socket

class ClientSocket:
    def __init__(self, ip: Addr):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(ip)
    def send(self, data: bytes):
        self.sock.sendall(data)

    def receive_message(self):
        buffer = b''
        while True:
            data = self.sock.recv(4096)
            if not data:
                # Connection closed
                break
            buffer += data
            while b'\n' in buffer:
                message, buffer = buffer.split(b'\n', 1)
                return message


