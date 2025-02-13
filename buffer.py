import socket

class Buffer:
    def __innit__(self):
        ...

    def connect(self, ip, port):
        buffer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        buffer_socket.connect((ip, port))

        return buffer_socket

    def terminate(self, buffer_socket):
        buffer_socket.close()

    def send(self, buffer_socket, message):
        buffer_socket.send(message.encode("utf-8"))


IP = '192.168.176.250'
PORT = 12345

def runBuffer():
    buffer = Buffer()

    buffer_socket = buffer.connect(IP, PORT)

    buffer.send(buffer_socket, "test\n")

    buffer.terminate(buffer_socket)

if __name__ == '__main__':
    runBuffer()