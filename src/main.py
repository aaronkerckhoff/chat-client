from client_state import ClientState, new_client
import packet_parser

client = new_client("Hello World, Im leah")
client.broadcast_self()


def update(client: ClientState):
    while True:
        message = client.client_socket.receive_message()
        if not message:
            break
        packet_parser.parse_packet(message, client)