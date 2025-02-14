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
    try:
        version = int(data[:8], 2)
        protocol = int(data[8:16], 2)
        cversion = int(data[16:32], 2)
        if not version == magicNumber:
            raise Exception(f"Wrong Version: {version}")
        if not protocol == 0:
            raise Exception(f"Wrong Protocol Version: {version}")
        if not cversion == 0:
            raise Exception(f"Wrong Client-spesific Version: {version}")
        return json.loads(data[32:-2]), version, protocol, cversion
    except:
        print("Wrong Format")
        return None


def runBuffer():
    buffer = Buffer(IP, PORT)

    for _ in range(time):
        data = None
        data = buffer.listen()
        try:
            sdata, v, p, cv = formatData(data, 69)
            if sdata["from_buf"] == False and sdata["inner"]["type"] == "WANTS":
                if sdata["receiver"] in buffer.q:
                    while not buffer.q[sdata["receiver"]].empty():
                        buffer.send('01000101000000000000000000000000' + '{"from_buf": true, "type": "DIRECTED", "receiver": 1234567890, "inner": {"type": "MESSAGE", "data": "' + buffer.q[sdata["receiver"]].get()["inner"]["data"] + '", "hash": "' + buffer.q[sdata["receiver"]].get()["inner"]["hash"] + '", "sender": "987654321"}}' + '\n')
            elif sdata["from_buf"] == False and sdata["inner"]["type"] == "MESSAGE":
                if sdata["receiver"] not in buffer.q:
                    buffer.q[sdata["receiver"]] = Queue()
                buffer.q[sdata["receiver"]].put(sdata["receiver"], data)
                print(f"Received and Buffered: {data}", end="")
            sleep(1)

        except:
            print("Wrong Format")

    buffer.socket.close()


if __name__ == '__main__':
    runBuffer()
