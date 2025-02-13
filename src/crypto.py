import os
from cryptography.hazmat.bindings._rust.openssl.aead import AESCCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


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

    aesgcm = AESCCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)

    return plaintext


def asym_encrypt(pk, message):
    encrypted_message = pk.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return encrypted_message


def asym_decryption(sk, message):
    decrypted_message = sk.decrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return decrypted_message


def get_new_asym_keys():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key


def get_asym_sig(sk, message):
    signature = sk.sign(message, ec.ECDSA(hashes.SHA256()))
    return signature


def verify_asym_sig(pk, message, signature):
    try:
        pk.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        print("The signature is valid!")
        return True
    except Exception as e:
        print("The signature is invalid:", e)
        return False


def key_derivation(pk):
    salt = os.urandom(16)
    key_length = 256  # Length of a single key
    kdf = Argon2id(
        salt=salt,
        length=2 * key_length,  # Derive twice the length of a single key
        iterations=10,
        lanes=4,
        memory_cost=64 * 1024,
    )
    # Serialize the private key to bytes
    pk_bytes = pk.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    derived_key_material = kdf.derive(pk_bytes)
    key1 = derived_key_material[:key_length]
    key2 = derived_key_material[key_length:]
    return key1, key2