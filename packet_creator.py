
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

def create_body(message_type):
    body = {
        "from_buf" : False,
        "type" : message_type
    }
    return body
def create_direct_message():
    body = create_body("DIRECTED")
    body["receiver"] = 
    

