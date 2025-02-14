import public_key
import signature

class ClientState:
    def get_public_key(self) -> public_key.PublicKey:
        """Returns the global public key of this client"""
        pass
    def received_message(self, sender: public_key.PublicKey, encrypted_message_bytes: bytes, decrypted_hash: bytes):
        """The client has received a message that is still encrypted.
        We need to check whether the decrypted message hash matches the decrypted hash, the other client might
        have been hacked otherwise :O
        
        Todo: We don't check yet whether the message has actually come from the pretended sender, enabeling people to send fake packets making this client think the other party has been hacked."""
        pass
    def received_healing(self, sender: public_key.PublicKey, encrypted_new_key: bytes, signature: signature.Signature):
        """The client received a healing message from the sender. 
        The encrypted_new_key has been asymetrically encrypted with the most current public key within the dm message context.
        """
        pass
    def other_wants(self, requested: public_key.PublicKey):
        """A client on the network requested that buffer servers send the most recent messages to the requested receiver.
        This function can be ignored by non-buffer clients"""
        pass
    def discovered_client(self, public_key: public_key.PublicKey, name: str, signature: signature.Signature):
        """Received a broadcast message where a connected client announces themselves. 
        Their name has been signed with the signature."""
        pass
    def fqg():
        pass
    