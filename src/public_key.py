class PublicKey:
    def __init__(self, str: str):
        if len(str) != 32:
            return
        self.value = str

    def as_base64_string(self) -> str:
        pass

def from_base64_string(str: str) -> PublicKey:
    return PublicKey(str)
