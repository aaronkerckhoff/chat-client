from .protocol_ver import current_protocol_version
import io
import json
import base64
from . import public_key


def create_head() -> io.BytesIO:
    stream = io.BytesIO()
    magic_number = 69
    stream.write(magic_number.to_bytes(1, byteorder="little"))
    stream.write(current_protocol_version.to_bytes(1, byteorder="little"))
    client_specifics = 0
    stream.write(client_specifics.to_bytes(2, byteorder="little"))
    return stream


def as_bytes(body) -> bytes:
    stream = create_head()
    #stream = io.BytesIO()
    json_body = json.dumps(body)
    json_body += '\n'
    encoded_body = json_body.encode(encoding="utf-8")

    stream.write(encoded_body)
    return stream.getvalue()

def create_body(message_type):
    body = {
        "from_buf" : False,
        "type" : message_type
    }
    return body

def create_broadcast_message():
    body = create_body("BROADCAST")
    return body

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

def create_wants_name_message(name: str):
    body = create_broadcast_message()
    body["inner"] = {
        "type": "WANTSNAME",
        "name": name,
    }
    return as_bytes(body)


def create_directed_message(receiver : str):
    body = create_body("DIRECTED")
    body["receiver"] = receiver
    return body


def create_direct_message(receiver, message: bytes, hash: str, sender: str, nonce: str):
    body = create_directed_message(receiver)
    body["inner"] = {
        "type": "MESSAGE",
        "data": base64.b64encode(message).decode("utf-8"),
        "hash": hash,
        "sender": sender,
        "nonce": base64.b64encode(nonce).decode("utf-8")
    }
    return as_bytes(body)


def create_exchange_message(key: str, sender: str, sig: str, receiver: str):
    body = create_directed_message(receiver)
    body["inner"] = {
        "type": "EXCHANGE",
        "sym_key": key,
        "sender": sender,
        "sig": sig
    }
    return as_bytes(body)
