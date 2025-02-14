import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib

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
    Encrypt data using recipient's RSA public key.
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


def rsa_decrypt(private_key, ciphertext: bytes) -> bytes:
    """
    Decrypt data using RSA private key.
    """
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return plaintext


def sign_message(private_key, message: bytes) -> bytes:
    """
    Sign a message using RSA-PSS.
    """
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return signature


def verify_signature(public_key, message: bytes, signature: bytes) -> bool:
    """
    Verify the RSA-PSS signature.
    """
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


# AES functions
def generate_aes_key() -> bytes:
    """
    Generates a random 256-bit AES key.
    """
    return os.urandom(32)


def aes_encrypt(key: bytes, plaintext: bytes, associated_data: bytes) -> dict:
    """
    Encrypts plaintext using AES-GCM.
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return {"nonce": nonce, "ciphertext": ciphertext}


def aes_decrypt(
    key: bytes, nonce: bytes, ciphertext: bytes, associated_data: bytes
) -> bytes:
    """
    Decrypt ciphertext using AES-GCM.
    """
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
    return plaintext


def get_sha256_hash(message: bytes) -> bytes:
    m = hashlib.sha256()
    m.update(message)
    return m.digest()
