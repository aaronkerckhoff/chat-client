import public_key
import crypto
import base64
class Signature:
    def __init__(self, sig_bytes):
        self.sig_bytes = sig_bytes

    def valid_for(self, pub_key: public_key.PublicKey, data: bytes) -> bool:
        return crypto.verify_signature(pub_key.inner, data, self.sig_bytes)
    def to_base64(self) -> str:
        return base64.b64encode(self.sig_bytes).decode("utf-8")

def sign_with(private_key, data: bytes) -> Signature:
    sig_bytes = crypto.sign_message(private_key, data)
    return Signature(sig_bytes)

def from_base64_string(str: str) -> Signature:
    return Signature(base64.b64decode(str))