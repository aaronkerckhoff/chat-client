class Signature:
    def valid_for(self, pub_key, data: bytes) -> bool:
        pass
    def to_base64(self) -> str:
        pass   

def sign_with(private_key, data: bytes) -> Signature:
    pass

def from_base64_string(str: str) -> Signature:
    pass