import socket

class Buffer:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def send(self, message):
        self.socket.send(message.encode("utf-8"))


IP = '192.168.176.250'
PORT = 12345

def runBuffer():
    buffer = Buffer(IP, PORT)

    buffer.send("test\n")

    buffer.socket.close()


if __name__ == '__main__':
    runBuffer()