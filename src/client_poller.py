import io
import packet_parser
import client_state

def update(client: client_state.ClientState):
    message = client.client_socket.receive_message()
    message = io.BytesIO(message)
    if not message:
        print("Connection closed")
        return
    packet_parser.parse_packet(message, client)
    