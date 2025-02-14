import io
import json

current_protocol_version = 0

class PubKey:
    pass

class BaseMessage:
    def __init__(self, from_buf: bool, type, receiver: None | PubKey):
        self.from_buf = from_buf
        if type != "BROADCAST" or type != "DIRECTED":
            raise Exception("Invalid type: " + type)
        self.type = type
        if receiver != None:
            self.receiver = receiver



def valid_head(io_stream: io.BytesIO) -> bool:
    magic_number = io_stream.read(1)[0]
    if magic_number != 69:
        return False
    protocol_version = io_stream.read(1)[0]
    if protocol_version != current_protocol_version:
        return False #Fuck backwards comp.
    client_specifics = int.from_bytes(io_stream.read(2), byteorder= "little") #Since our client has 0 as protocol version, we don't care about byteorder, and neither has the protocol
    if client_specifics != 0:
        return False
    return True

def parse_packet(io_stream: io.BytesIO) -> None | BaseMessage:
    if not valid_head(io_stream):
        return None
    body = io_stream.read().decode(str="utf-8")
    body_object = json.loads(body)
    return body_object #Should follow that schema.
