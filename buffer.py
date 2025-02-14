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
    format = True

    try:
        version = int(data[2:10], 2)
        if not version == magicNumber:
            raise Exception(f"Wrong Version: {version}")
    except:
        print("Wrong Format")
        format = False
    
    try:
        protocol = int(data[10:18], 2)

        if not protocol == 0:
            raise Exception(f"Wrong Protocol Version: {version}")
    except:
        print("Wrong Format")
        format = False

    try:
        cversion = int(data[19:31], 2)

        if not cversion == 0:
            raise Exception(f"Wrong Client-spesific Version: {version}")
    except:
        print("Wrong Format")
        format = False

    if not format == False:
        return json.loads(data[32:]), version, protocol, cversion


def runBuffer():
    buffer = Buffer(IP, PORT)

    for _ in range(time):
        data = buffer.listen()
        sdata, v, p, cv = formatData(data, 69)
        if sdata["inner"]["type"] == "WANTS":
            sleep(1)
            if "receiver" in buffer.q:
                while not buffer.q.empty():
                    buffer.send('0b' +format(69, '08b') + format(0, '07b') + format(0, '015b') + '{"from_buf": true, "type": "DIRECTED", "receiver": 1234567890, "inner": {"type": "MESSAGE", "data": "' + buffer.q.get()["inner"]["data"] + '", "hash": "' + buffer.q.get()["inner"]["hash"] + '", "sender": "987654321"}}' + '\n')
        elif sdata['from_buf'] == False:
            buffer.enqueue(sdata["receiver"], data)
            print(f"Received: {data}", end="")
        sleep(1)

    buffer.socket.close()


if __name__ == '__main__':
    runBuffer()