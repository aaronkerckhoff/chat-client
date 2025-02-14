from src.crypto import verify_asym_sig


class Signature:
    def __init__(self, sig: str):
        if len(sig) != 72:
            return
        self.signature = sig

    def verify(self, pk, message) -> bool:
        return verify_asym_sig(pk, message, self.signature)


def from_base64_string(str: str) -> Signature:
    return Signature(str)
