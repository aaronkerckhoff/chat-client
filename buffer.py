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

def formatData(data):
    binary = int(data[:1], 2).to_bytes(len(1))
    sdata = json.loads(data[1:])

    return binary[:8], binary[8:16], binary[16:32], sdata

def runBuffer():
    buffer = Buffer(IP, PORT)

    for _ in range(time):
        data = buffer.listen()
        version, protokoll, cversion, sdata = formatData(data, 69)


#            sdata, v, p, cv = formatData(data, 69)
#            if sdata["from_buf"] == False and sdata["inner"]["type"] == "WANTS":
#                if sdata["receiver"] in buffer.q:
#                    while not buffer.q[sdata["receiver"]].empty():
#                        buffer.send('01000101000000000000000000000000' + '{"from_buf": true, "type": "DIRECTED", "receiver": 1234567890, "inner": {"type": "MESSAGE", "data": "' + buffer.q[sdata["receiver"]].get()["inner"]["data"] + '", "hash": "' + buffer.q[sdata["receiver"]].get()["inner"]["hash"] + '", "sender": "987654321"}}' + '\n')
#            elif sdata["from_buf"] == False and sdata["inner"]["type"] == "MESSAGE":
#                if sdata["receiver"] not in buffer.q:
#                    buffer.q[sdata["receiver"]] = Queue()
#                buffer.q[sdata["receiver"]].put(sdata["receiver"], data)
#                print(f"Received and Buffered: {data}", end="")
        sleep(1)

    buffer.socket.close()


if __name__ == '__main__':
    runBuffer()
