import socket
from time import sleep

class Buffer:
    def __init__(self, ip: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def send(self, message: str) -> None:
        try:
            self.socket.send(message.encode("utf-8"))
        except Exception as e:
            print(f"Error: {e}")

    def listen(self) -> (str | None):
        try:
            data = self.socket.recv(1024)
            if not data:
                print("Server closed the connection.")
                return None
            print(f"Received from server: {data.decode('utf-8')}", end="")
            return data.decode('utf-8')
                

        except Exception as e:
            print(f"Error: {e}")


IP = '192.168.176.250'
PORT = 12345

def runBuffer():
    buffer = Buffer(IP, PORT)

    data = None
    while data == None:
        data = buffer.listen()
    
    sleep(5)
    buffer.socket.close()


if __name__ == '__main__':
    runBuffer()