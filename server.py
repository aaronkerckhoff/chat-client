#!/usr/bin/env python3
# coding=utf-8
import socket
import threading
from queue import Queue
import time

class ServerThread:
    def __init__(self):
        self.lock = threading.RLock()  # lock for clients list
        self.clients = []
        self.sendQueue :Queue = Queue()  # Thread safe queue
        self.server = None

    def __ownIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(("10.254.254.254", 1))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()

##############################################################################
###### Starting Server #######################################################
##############################################################################
    def start(self):
        while True:
            own = self.__ownIP()
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.bind((IP, PORT))  # Server lauscht auf Port 12345
                self.server.listen(5)
                print(f"Der Server läuft unter {own}")
                break
            except Exception as e:
                print(f"Adresse geblockt. Erneuter Versuch in 5s.")
                time.sleep(5)
        threading.Thread(daemon=True, target=self.__listen).start()
        threading.Thread(daemon=True, target=self.__sendWorker).start()
        
    def terminate(self):
        with self.lock:
            for client in self.clients:
                client.close()
        self.server.close()
        print("Der Server wurde beendet.")


##############################################################################
###### Accepting new Client ##################################################
##############################################################################
    def __listen(self):
        while True:
            try:
                client, addr = self.server.accept()
                with self.lock: self.clients.append(client)
                threading.Thread(daemon=True, target=(self.__listenClient), args=(client, addr)).start()
                print(f"Neuer Client mit {addr}")
            except Exception:
                print("Verbindungsaufbau abgebrochen.")
                time.sleep(1)
                continue


##############################################################################
###### Listening to a Client #################################################
##############################################################################
    def __listenClient(self, client, addr):
        while True:
            data = ''
            while True:
                try:
                    data += client.recv(2048).decode("utf-8")
                except UnicodeDecodeError:
                    print(f"{addr} hat kein Unicode gesendet.")
                    continue
                except Exception as e:
                    with self.lock:
                        self.clients.remove(client)
                    print(f"Verbindung zu {addr} geschlossen.")
                    return
                if "\n" in data:
                    data = data.strip()
                    break
            
            print(f"{addr}: {data}")
            self.sendQueue.put(data)

##############################################################################
###### Thread that sends messages ############################################
##############################################################################
    def __sendWorker(self):
        while True:
            message = self.sendQueue.get()
            with self.lock:
                clientCopies = self.clients.copy()
            for client in clientCopies:
                with self.lock:
                    try:
                        client.send((message + "\n").encode("utf-8"))
                    except Exception as e:
                        self.clients.remove(client)
                        print(f"Client hat sich abgemeldet {e}")  # TODO: add address





##############################################################################
###### Main ##################################################################
##############################################################################

IP = ""  #"localhost"
PORT = 12345

def runServer(seconds: int):
    server = ServerThread()
    server.start()
    time.sleep(seconds)
    server.terminate()
    exit()


if __name__ == "__main__":
    #runServer(60 * 5)
    runServer(24 * 60 * 60)  # one day

