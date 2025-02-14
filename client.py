import socket
from time import sleep

class Client:
    def __init__(self, ip: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def send(self, message: str) -> None:
        try:
            self.socket.send(message.encode("utf-8"))
        except Exception as e:
            raise Exception(f"Error: {e}")

    def listen(self):
        try:
            data = self.socket.recv(1024)
            if not data:
                return None
            return data.decode('utf-8')

        except Exception as e:
            raise Exception(f"Error: {e}")


IP = '192.168.176.250'
PORT = 12345

def runClient():
    client = Client(IP, PORT)

    client.send('test\n')

    print(client.listen())

    sleep(1)

    client.socket.close()

if __name__ == '__main__':
    runClient()