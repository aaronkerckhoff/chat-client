import os
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from src import crypto


def test_aes_encrypt_decrypt():
    # Create a valid 16-byte key for AES-128
    key = os.urandom(16)
    plaintext = b"Secret message"
    associated_data = b"header"
    encrypted_data = crypto.aes_encrypt(key, plaintext, associated_data)
    # Verify the encrypted output has the expected structure
    assert isinstance(encrypted_data, dict)
    assert "nonce" in encrypted_data
    assert "ciphertext" in encrypted_data
    # Decrypt and check that the plaintext is recovered
    decrypted = crypto.aes128_decrypt(key, encrypted_data)
    assert decrypted == plaintext


def test_aes_invalid_key_length(capsys):
    # Use an invalid key length (not 16 bytes)
    invalid_key = os.urandom(10)
    plaintext = b"Test"
    encrypted = crypto.aes_encrypt(invalid_key, plaintext)
    captured = capsys.readouterr().out
    assert "Key must be 16 bytes for AES-128" in captured
    assert encrypted is None

    fake_data = {"nonce": os.urandom(12), "ciphertext": b"fake"}
    decrypted = crypto.aes128_decrypt(invalid_key, fake_data)
    captured = capsys.readouterr().out
    assert "Key must be 16 bytes for AES-128" in captured
    assert decrypted is None


def test_asymmetric_signature(capsys):
    message = "Hello, cryptography!"
    sk = ec.generate_private_key(ec.SECP256R1())
    pk = sk.public_key()
    signature = crypto.get_asym_sig(sk, message)
    # Verify that a correct signature passes verification
    valid = crypto.verify_asym_sig(pk, message, signature)
    assert valid is True

    # Verify that tampering with the message causes a verification failure
    invalid = crypto.verify_asym_sig(pk, message + "tampered", signature)
    captured = capsys.readouterr().out
    assert "The signature is invalid:" in captured
    assert invalid is False


def test_get_new_asym_keys(monkeypatch):
    # Ensure the environment variables are not set so that new keys are generated
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("PUBLIC_KEY", raising=False)
    sk, pk = crypto.get_new_asym_keys()
    assert sk is not None
    assert pk is not None
    # Check that the keys are instances of the appropriate classes
    assert isinstance(sk, ec.EllipticCurvePrivateKey)
    assert isinstance(pk, ec.EllipticCurvePublicKey)


def test_generate_symmetric_key_128():
    shared_secret = os.urandom(32)
    # Generate a symmetric key intended for AES-128 by specifying a 16-byte length
    symmetric_key = crypto.generate_symmetric_key_128(shared_secret, key_length=16)
    assert isinstance(symmetric_key, bytes)
    assert len(symmetric_key) == 16


def test_eec_key_derivation():
    # Generate two key pairs for an ECDH exchange
    sk1 = ec.generate_private_key(ec.SECP256R1())
    pk1 = sk1.public_key()
    sk2 = ec.generate_private_key(ec.SECP256R1())
    pk2 = sk2.public_key()
    secret1 = crypto.eec_key_derivation(sk1, pk2)
    secret2 = crypto.eec_key_derivation(sk2, pk1)
    # Both parties should derive the same shared secret
    assert secret1 == secret2
