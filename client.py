import socket

class Client:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def send(self, message):
        self.socket.send(message.encode("utf-8"))

    def listen(self):
        try:
            while True:
                data = self.socket.recv(1024)
                if not data:
                    print("Server closed the connection.")
                    break
                print(f"Received from server: {data.decode('utf-8')}")

        except Exception as e:
            print(f"Error: {e}")


IP = '192.168.176.250'
PORT = 12345

def runClient():
    client = Client(IP, PORT)

    client.send('test\n')

    client.listen()

    client.socket.close()

if __name__ == '__main__':
    runClient()