import io
import json
import signature
import public_key
import base64
from client_state import ClientState
from protocol_ver import current_protocol_version
class PubKey:
    def __init__(self, b64_str: str):
        pass

class InnerMessage:
    def __init__(self, type):
        self.type = type

class BaseMessage:
    def __init__(self, from_buf: bool, type, receiver: None | PubKey, inner):
        self.from_buf = from_buf
        if type != "BROADCAST" or type != "DIRECTED":
            raise Exception("Invalid type: " + type)
        self.type = type
        if receiver != None:
            self.receiver = receiver

def execute_message(dic: dict, client: ClientState):
    """Executes a json object on the client """
    from_buf = dic["from_buf"]
    type = dic["type"]
    inner = dic["inner"]
    receiver = None
    if type == "DIRECTED":
        receiver = public_key.from_base64_string(dic["receiver"])
        if receiver != client.get_public_key():
            return



def execute_broadcast_message(dic: dict, client: ClientState):
    type = dic["type"]
    match type:
        case "EXISTS":
            sender_public_key = public_key.from_base64_string(dic["public_key"])
            signed_name = signature.from_base64_string(dic["public_key"])
            display_name =  dic["display_name"]
            client.discovered_client(sender_public_key, display_name, signed_name)
        case "WANTS":
            requested = public_key.from_base64_string(dic["public_key"])
            client.other_wants(requested)
        case "WANTSNAME":
            requested = public_key.from_base64_string(dic["name"])
            client.other_wants(requested)

def execute_directed_message(dic: dict, client: ClientState):
    type = dic["type"]
    match type:
        case "HEAL":
            if current_protocol_version < 1:
                print("Client doesn't support version 1 protocol")
                return None
            sender = public_key.from_base64_string(dic["sender"])
            new_key = base64.b64decode(dic["new_key"])
            sig = signature.from_base64_string(dic["sig"])
            client.received_healing(sender, new_key, sig)
        case "EXCHANGE":
            sym_key = base64.b64decode(dic["sym_key"])
            sender = public_key.from_base64_string(dic["sender"])
            sig = signature.from_base64_string(dic["sig"])
            client.received_shared_secret(sender, sym_key, sig)
        case "MESSAGE":
            sender = public_key.from_base64_string(dic["sender"])
            data = base64.b64decode(dic["data"])
            hash = base64.b64decode(dic["hash"])
            client.received_message(sender, data, hash)





            


def valid_head(io_stream: io.BytesIO) -> bool:
    """
    Reads the head of the iostream, and returns whether or not it matches with the supported version
    """
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

def parse_packet(io_stream: io.BytesIO, client: ClientState) -> None | BaseMessage:
    """Parses a packet from an io_stream. This includes head and body, and then calls the client interface with the appropriate package."""
    if not valid_head(io_stream):
        return None
    body = io_stream.read()#.decode(str="utf-8")
    body_object = json.loads(body)
    execute_message(body_object, client)
    
