import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from src.logger_utils import setup_logger

logger = setup_logger("rsa_encryption", "rsa_encryption.log")

KEY_DIR = "keys"
PRIVATE_KEY_FILE = os.path.join(KEY_DIR, "private_key.pem")
PUBLIC_KEY_FILE = os.path.join(KEY_DIR, "public_key.pem")


# Key creation and loading helper functions
def generate_rsa_key_pair():
    """
    Generates an RSA key pair and stores them as PEM files.
    """
    if not os.path.exists(KEY_DIR):
        os.makedirs(KEY_DIR)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with open(PRIVATE_KEY_FILE, "wb") as file:
        file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    public_key = private_key.public_key()
    with open(PUBLIC_KEY_FILE, "wb") as file:
        file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    logger.info("RSA key pair generated and saved.")


def load_private_key():
    with open(PRIVATE_KEY_FILE, "rb") as file:
        private_key = serialization.load_pem_private_key(file.read(), password=None)
    return private_key


def load_public_key():
    with open(PUBLIC_KEY_FILE, "rb") as file:
        public_key = serialization.load_pem_public_key(file.read())
    return public_key


# RSA functions
def rsa_encrypt(public_key, data: bytes) -> bytes:
    """
    Encrypt data using recipient's RSA public key
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext
