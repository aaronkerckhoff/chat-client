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


#IP = '192.168.176.250'
IP = '192.168.176.160'
PORT = 12345

magicNumber = 69

time = 60

def formatData(data, magicNumber: int):
    version = int(data[2:10], 2)

    if not version == magicNumber:
        raise Exception(f"Wrong Version: {version}")
    
    protocol = int(data[10:18], 2)

    if not protocol == 0:
        raise Exception(f"Wrong Protocol Version: {version}")
    
    cversion = int(data[19:31], 2)

    if not cversion == 0:
        raise Exception(f"Wrong Client-spesific Version: {version}")
    
    return json.loads(data[32:]), version, protocol, cversion


def runBuffer():
    buffer = Buffer(IP, PORT)

    data = buffer.listen()

    sdata, v, p, cv = formatData(data, 69)

    buffer.enqueue(sdata["receiver"], data)

    print(f"Received from server: {data}", end="")


    sleep(1)

    buffer.socket.close()


if __name__ == '__main__':
    runBuffer()