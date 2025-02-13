import socket


class Client:
    def __innit__(self):
        ...

    def send(ip, port, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))

        client_socket.send(message.encode())

        client_socket.close()


IP = '192.168.176.250'
PORT = 12345

def start():
    client = Client()

    client.send(IP, PORT, 'test')

if __name__ == '__main__':
    start()