import public_key
import signature
import crypto
class ChatState:
    def __init__(self, symetric_key: bytes, display_name: str, public_key: public_key.PublicKey):
        self.symetric_key = symetric_key
        self.display_name = display_name,
        self.public_key = public_key,

    def decrypt_verify_chat(self, message: bytes, decrypted_hash: bytes) -> str | None:
        decrypted_message = crypto.aes_decrypt(self.symetric_key, message)
        if decrypted_message == None:
            return None
        received_hash = crypto.hash(decrypted_message)
        if received_hash == decrypted_hash:
            return decrypted_message.decode("utf-8")

        
        
class ClientState:

    def __init__(self, pub_key: public_key.PublicKey, priv_key):
        self.chats: dict[public_key.PublicKey, ChatState] = {}
        self.public_key = pub_key
        self.private_key = priv_key
        

    def get_public_key(self) -> public_key.PublicKey:
        """Returns the global public key of this client"""
        return self.public_key
    
    def received_shared_secret(self, sender: public_key.PublicKey, encrypted_shared_secret: bytes, shared_secret_signature: signature.Signature):
        """The client has received a chat-initiating shared secret"""
        sym_key = crypto.rsa_decrypt(self.private_key, encrypted_shared_secret)
        if not shared_secret_signature.valid_for(sender, sym_key):
            return
        self.chats[sender] = sym_key            
        pass
    def received_message(self, sender: public_key.PublicKey, encrypted_message_bytes: bytes, decrypted_hash: bytes):
        """The client has received a message that is still encrypted.
        We need to check whether the decrypted message hash matches the decrypted hash, the other client might
        have been hacked otherwise :O
        
        Todo: We don't check yet whether the message has actually come from the pretended sender, enabeling people to send fake packets making this client think the other party has been hacked."""
        if not sender in self.chats:
            return #We dont know them, maybe log it?
        self.chats[sender].decrypt_verify_chat(encrypted_message_bytes, decrypted_hash)
    def received_healing(self, sender: public_key.PublicKey, encrypted_new_key: bytes, signature: signature.Signature):
        """The client received a healing message from the sender. 
        The encrypted_new_key has been asymetrically encrypted with the most current public key within the dm message context.
        """
        raise NotImplementedError()
        pass
    def other_wants(self, requested: public_key.PublicKey):
        """A client on the network requested that buffer servers send the most recent messages to the requested receiver.
        This function can be ignored by non-buffer clients"""
        pass
    def other_wants_name(self, name_query: str):
        """A client on the network requested that buffer servers resend broadcast/exists messages of every user that matches a certain name query
        This function can be ignored by non-buffer clients"""
        pass
    def discovered_client(self, public_key: public_key.PublicKey, name: str, signature: signature.Signature):
        """Received a broadcast message where a connected client announces themselves. 
        Their name has been signed with the signature."""
        pass
    