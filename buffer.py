import socket

class Buffer:
    def __innit__(self):
        self.ip

    def send(ip, port, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))

        client_socket.send(message.encode())

        client_socket.close()


IP = '192.168.176.250'
PORT = 12345

if __name__ == '__main__':
    Buffer.send(IP, PORT, 'test')