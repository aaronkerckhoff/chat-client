import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from dotenv import load_dotenv, set_key


def generate_symmetric_key_128(shared_secret, key_length=32):
    derived_key = HKDF(
        algorithm=hashes.SHA256(), length=key_length, salt=None, info=b"handshake data"
    ).derive(shared_secret)

    return derived_key


# Load environment variables from .env file
load_dotenv()


def save_key_to_env(key, key_name):
    key_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    set_key(".env", key_name, key_bytes)


def save_public_key_to_env(key, key_name):
    key_bytes = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    set_key(".env", key_name, key_bytes)


def load_key_from_env(key_name):
    key_bytes = os.getenv(key_name)
    if key_bytes:
        return serialization.load_pem_private_key(
            key_bytes.encode("utf-8"), password=None
        )
    return None


def load_public_key_from_env(key_name):
    key_bytes = os.getenv(key_name)
    if key_bytes:
        return serialization.load_pem_public_key(key_bytes.encode("utf-8"))
    return None


def get_new_asym_keys():
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
    Encrypt plaintext using AES-128-GCM.
    """
    if len(key) != 16:
        print("Key must be 16 bytes for AES-128")
        return

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)

    return {
        "nonce": nonce,
        "ciphertext": ciphertext,
        "associated_data": associated_data,
    }


def aes128_decrypt(key, encrypted_data):
    """
    Decrypt ciphertext using AES-128-GCM.
    """
    if len(key) != 16:
        print("Key must be 16 bytes for AES-128")
        return

    nonce = encrypted_data["nonce"]
    ciphertext = encrypted_data["ciphertext"]
    associated_data = encrypted_data.get("associated_data", None)

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)

    return plaintext


def eec_key_derivation(sk, peer_pk):
    shared_secret = sk.exchange(ec.ECDH(), peer_pk)
    return shared_secret


def get_asym_sig(sk, message):
    message = message.encode("utf-8")
    signature = sk.sign(message, ec.ECDSA(hashes.SHA256()))
    return signature


def verify_asym_sig(pk, message, signature):
    message = message.encode("utf-8")
    try:
        pk.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        print("The signature is valid!")
        return True
    except Exception as e:
        print("The signature is invalid:", e)
        return False


def key_derivation(pk):
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
sk, pk = get_new_asym_keys()
