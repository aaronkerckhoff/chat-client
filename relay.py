import src.client_socket
import src.packet_parser
import src.packet_creator
import src.client_state
import src.public_key
import time
import io
import json


def query_directed(key, message_queue: list) -> list:
    res = []
    for message in message_queue:
        if message["type"] == "DIRECTED" and message["receiver"] == key:
            res.append(message)
    return res

def query_name(name: str, message_queue: list) -> list:
    res = []
    for message in message_queue:
        if message["type"] == "BROADCAST" and message["inner"]["type"] == "EXISTS" and name in message["inner"]["display_name"]:
            res.append(message)
    return res

def resend(messages: list, socket: src.client_socket.ClientSocket):
    for message in messages:
        message["from_buf"] = True
        packet = src.packet_creator.as_bytes(message)
        socket.send(packet)



def try_execute_message(message, message_queue, socket) -> bool:
    if message["type"] == "BROADCAST":
        inner = message["inner"]
        match inner["type"]:
            case "WANTS":
                found = query_directed(inner["public_key"], message_queue)
                resend(found, socket)
                return True
            case "WANTSNAME":
                found = query_name(inner["name"], message_queue)
                resend(found)
                return True
    return False



socket = src.client_socket.ClientSocket(src.client_state.IP, src.client_state.PORT)
message_queue = []
while True:
    message = socket.receive_message()
    if not message:
        time.sleep(1)
        continue
    message = io.BytesIO(message)
    if not src.packet_parser.valid_head(message):
        print("Received message with invalid head.")
        continue
    body = json.loads(message.read())
    if body["from_buf"] == True:
        continue

    if not try_execute_message(body, message_queue, socket):
        message_queue.append(body)


