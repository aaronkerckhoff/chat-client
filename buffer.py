import socket
from queue import Queue
from time import sleep

class Buffer:
    def __init__(self, ip: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

        self.q = {}

    def send(self, message: str) -> None:
        try:
            self.socket.send(message.encode("utf-8"))
        except Exception as e:
            raise Exception(f"Error: {e}")

    def listen(self) -> (str | None):
        try:
            data = self.socket.recv(1024)
            if not data:
                return None
            return data.decode('utf-8')
                
        except Exception as e:
            raise Exception(f"Error: {e}")
        
    def enqueue(self, r, data):
        if r not in self.q:
            self.q[r] = Queue() 
        self.q[r].put(data)

    def checkVersion(self, data):
        if not(data[:10] == str(bin(69))):
            raise Exception("Wrong Version ({data[:8]})")


IP = '192.168.176.250'
PORT = 12345

time = 60*5

def runBuffer():
    buffer = Buffer(IP, PORT)

    for i in range(time):
        data = buffer.listen()
        print(f"Received from server: {data}", end="")
        buffer.enqueue('t', data)
        sleep(1)

    buffer.socket.close()


if __name__ == '__main__':
    runBuffer()