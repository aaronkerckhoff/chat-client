import io
import json
import socket
from queue import Queue
from time import sleep
import json
import io

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

def formatData(data):
    io_stream = io.BytesIO(data[0].encode("utf-8"))
    magic_number = io_stream.read(1)[0]
    print(type(data[1:-1]))

    sdata = json.loads(data[1:-1])
    return magic_number, sdata

def runBuffer():
    buffer = Buffer(IP, PORT)

    for _ in range(time):
        data = None
        data = buffer.listen()
        print(f"Received from server: {data}", end="")
        mn, sd = formatData(data)
        print(mn, sd)
        sleep(1)


    buffer.socket.close()


if __name__ == '__main__':
    runBuffer()
