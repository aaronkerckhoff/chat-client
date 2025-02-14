import socket
import threading

class Client:
    def __init__(self, ip: str, port: int, on_message_received=None) -> None:
        """
        Initializes the client and starts the listening thread.
        :param ip: Server IP address
        :param port: Server port
        :param on_message_received: Callback function that gets called when a new message is received.
                                    It can be an instance method.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.running = True
        self.on_message_received = on_message_received  # Callback (can be an instance method)
        self.thread = threading.Thread(target=self.__listen_loop, daemon=True)
        self.thread.start()

    def send(self, message: str) -> None:
        """Send a message to the server."""
        try:
            print(f"Sending data... ")
            self.socket.send((message + "\n").encode('utf-8'))
            print("Data sent!")
        except Exception as e:
            print(f"Failed: {e}")
            raise Exception(f"Error: {e}")

    def listen(self):
        """Receives a single message from the server."""
        try:
            data = self.socket.recv(1024)
            if not data:
                return None
            return data.decode('utf-8')
        except Exception as e:
            raise Exception(f"Error: {e}")

    def __listen_loop(self):
        """Continuously listens for incoming messages in a separate thread and triggers an event."""
        while self.running:
            try:
                message = self.listen()
                if message and self.on_message_received:
                    self.on_message_received(self, message)  # Pass self and message
            except Exception as e:
                print(f"Error while listening: {e}")
                break

    def dc(self):
        """Disconnect the client."""
        self.running = False
        self.socket.close()
        print("Disconnected from server.")
