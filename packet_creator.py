
import io
import json
import packet_parser

def create_head() -> io.BytesIO:
    stream = io.BytesIO()
    magic_number = 69
    stream.write(magic_number.to_bytes(1))
    stream.write(packet_parser.current_protocol_version.to_bytes(1))
    client_specifics = 0
    stream.write(client_specifics.to_bytes(2, byteorder="little"))
    return stream


def as_bytes(body) -> bytes:
    stream = create_head()
    encoded_body = json.dumps(body).encode(encoding="utf-8")
    stream.write(encoded_body)
    return stream.read()

def create_body(message_type):
    body = {
        "from_buf" : False,
        "type" : message_type
    }
    return body

def create_broadcast_message():
    body = create_body("BROADCAST")

def create_exists_message(public_key: str, display_name: str, signature: str):
    body = create_broadcast_message()
    body["inner"] = {
        "type": "EXISTS",
        "public_key": public_key,
        "display_name": display_name,
        "sig": signature
    }
    return as_bytes(body)

def create_wants_message(request_public_key: str):
    body = create_broadcast_message()
    body["inner"] = {
        "type": "WANTS",
        "public_key": request_public_key,
    }
    return as_bytes(body)

def create_direct_message(receiver : str):
    body = create_body("DIRECTED")
    body["receiver"] = receiver
    return body
def create_direct_content_message(receiver, message_content):
    body = create_direct_message(receiver)
    body["content"] = message_content
    return body




    

