import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from dotenv import load_dotenv, set_key
import base64
from src.logger_utils import setup_logger

logger = setup_logger("cryptography", "cryptography.log")


def generate_symmetric_key(shared_secret, key_length=32):
    """
    Generates a symmetric key using an initial shared secret and a key length
    """
    derived_key = HKDF(
        algorithm=hashes.SHA256(), length=key_length, salt=None, info=b"handshake data"
    ).derive(shared_secret)

    return derived_key


# Load environment variables from .env file
load_dotenv()


def save_key_to_env(key, key_name):
    """
    Saves the key with the key_name into the .env file (Base64 Encoded).
    """
    key_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    key_b64 = base64.b64encode(key_bytes).decode("utf-8")  # Encode in Base64
    set_key("src/.env", key_name, key_b64)  # Store in .env


def save_public_key_to_env(key, key_name):
    """
    Saves the public key in Base64 format to avoid newline issues.
    """
    key_bytes = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    key_b64 = base64.b64encode(key_bytes).decode("utf-8")  # Encode in Base64
    set_key("src/.env", key_name, key_b64)  # Store in .env


def load_key_from_env(key_name):
    """
    Loads the key with the key_name from the .env file (Base64 Decoded).
    """
    key_b64 = os.getenv(key_name)
    if key_b64:
        key_bytes = base64.b64decode(key_b64)  # Decode from Base64
        return serialization.load_pem_private_key(key_bytes, password=None)
    return None


def load_public_key_from_env(key_name):
    """
    Loads the public key from the .env file (Base64 Decoded).
    """
    key_b64 = os.getenv(key_name)
    if key_b64:
        key_bytes = base64.b64decode(key_b64)  # Decode from Base64
        return serialization.load_pem_public_key(key_bytes)
    return None


def get_new_asym_keys():
    """
    Returns the keys from the .env file if existing,
    else generating and returning a new sk and pk
    """
    secret_key = load_key_from_env("SECRET_KEY")
    public_key = load_public_key_from_env("PUBLIC_KEY")
    if secret_key is None or public_key is None:
        secret_key = ec.generate_private_key(ec.SECP256R1())
        public_key = secret_key.public_key()
        save_key_to_env(secret_key, "SECRET_KEY")
        save_public_key_to_env(public_key, "PUBLIC_KEY")
    return secret_key, public_key


def aes_encrypt(key, plaintext, associated_data=None):
    """
    Encrypt plaintext using AES-256-GCM.
    """
    if len(key) != 32:
        logger.error("Key must be 32 bytes for AES-256")
        return

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)

    return {
        "nonce": nonce,
        "ciphertext": ciphertext,
        "associated_data": associated_data,
    }


def aes_decrypt(key, encrypted_data):
    """
    Decrypt ciphertext using AES-256-GCM.
    """
    if len(key) != 32:
        logger.error("Key must be 32 bytes for AES-128")
        return
    nonce = encrypted_data["nonce"]
    ciphertext = encrypted_data["ciphertext"]
    associated_data = encrypted_data.get("associated_data", None)

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)

    return plaintext


def ecc_key_derivation(sk, peer_pk):
    """
    Generates a new shared secret and returns it
    """
    shared_secret = sk.exchange(ec.ECDH(), peer_pk)
    return shared_secret


def get_asym_sig(sk, message):
    """
    Generates a unique signature, based on sk and message
    """
    message = message.encode("utf-8")
    signature = sk.sign(message, ec.ECDSA(hashes.SHA256()))
    return signature


def verify_asym_sig(pk, message, signature):
    """
    Verifies whether a signature is correct for a specific message and pk
    """
    message = message.encode("utf-8")
    try:
        pk.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        print("The signature is valid!")
        return True
    except Exception as e:
        print("The signature is invalid:", e)
        return False


def key_derivation(pk):
    """
    Creates 2 new keys from the public key
    """
    salt = os.urandom(16)
    key_length = 32  # Example key length
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=2 * key_length,  # Derive twice the length of a single key
        salt=salt,
        info=b"handshake data",
    )
    pk_bytes = pk.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
        encryption_algorithm=serialization.NoEncryption(),
    )
    derived_key_material = hkdf.derive(pk_bytes)
    key1 = derived_key_material[:key_length]
    key2 = derived_key_material[key_length:]
    return key1, key2


# Generate or load keys
# sk, pk = get_new_asym_keys()
# peer_sk, peer_pk = get_new_asym_keys()
"""
print(sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8"),peer_sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8"))

own_secret = ecc_key_derivation(sk,peer_pk)
peer_secret = ecc_key_derivation(peer_sk, pk)
print(f"own_secret{own_secret}")
print(f"peer_secret{peer_secret}")
print("length", len(own_secret))
own_sym_key= generate_symmetric_key(own_secret)
peer_sym_key = generate_symmetric_key(peer_secret)
print(own_sym_key)
print(peer_sym_key)
message = b"wir sind die besten"
encr = aes_encrypt(own_sym_key, message)
print(f"encrypted message: {encr}")
decr = aes_decrypt(peer_sym_key, encr)
print(f"decrypted:{decr}")
"""
