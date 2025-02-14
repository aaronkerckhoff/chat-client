from src.crypto import verify_asym_sig


class Signature:
    def __init__(self, sig: str):
        self.signature = sig

    def verify(self, pk, message):
        return verify_asym_sig(pk, message, self.signature)


def from_base64_string(str: str) -> Signature:
    return Signature(str)
