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


#IP = '192.168.176.250'
IP = '192.168.176.160'
PORT = 12345

def runClient():
    client = Client(IP, PORT)
    client.send('01000101000000000000000000000000' + '{"from_buf": false, "type": "DIRECTED", "receiver": 1234567890, "inner": {"type": "MESSAGE", "data": "test", "hash": "h", "sender": "1234567890"}}' + '\n')

    client.send('01000101000000000000000000000000' + '{"from_buf": false, "type": "BROADCAST", "receiver": 1234567890, "inner": {"type": "WANTS"}}' + '\n')

    print(client.listen())

    sleep(1)


    print(client.listen())
    print(client.listen())

    sleep(1)

    client.socket.close()

if __name__ == '__main__':
    runClient()