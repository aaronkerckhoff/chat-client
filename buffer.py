import io
import json
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


IP = '192.168.176.250'
PORT = 12345

magicNumber = 69

time = 60*5

def formatData(data, magicNumber: int):
    stream = io.BytesIO(data)

    stream.seek(0)
    version = stream.read(8)

    if not version == magicNumber:
        raise Exception("Wrong Version: {version}")
    
    stream.seek(8)
    protocol = stream.read(10)

    if not protocol == 0:
        raise Exception("Wrong Protocol Version: {version}")
    
    stream.seek(16)
    cversion = stream.read(15)

    if not cversion == 0:
        raise Exception("Wrong Client-spesific Version: {version}")
    
    stream.seek(32)
    sdata = stream.read()


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