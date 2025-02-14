import os
import shutil
import pytest

from src import crypto


# Fixture to generate RSA keys before tests and clean up the keys directory afterwards
@pytest.fixture(scope="module", autouse=True)
def rsa_keys():
    # Remove the keys directory if it already exists to start fresh
    if os.path.exists(crypto.KEY_DIR):
        shutil.rmtree(crypto.KEY_DIR)
    crypto.generate_rsa_key_pair()
    yield
    # Cleanup after tests
    if os.path.exists(crypto.KEY_DIR):
        shutil.rmtree(crypto.KEY_DIR)


def test_rsa_key_loading():
    """Test that RSA keys can be loaded from the generated files."""
    private_key = crypto.load_private_key()
    public_key = crypto.load_public_key()
    # Check that the loaded keys have the expected attributes.
    # For instance, the public key should have an 'encrypt' method.
    assert hasattr(public_key, "encrypt")
    assert hasattr(private_key, "decrypt")


def test_rsa_encryption_decryption():
    """Test RSA encryption and decryption of a sample message."""
    private_key = crypto.load_private_key()
    public_key = crypto.load_public_key()

    message = b"Test RSA encryption and decryption"
    ciphertext = crypto.rsa_encrypt(public_key, message)
    # Ensure that the ciphertext is different from the original message
    assert ciphertext != message

    decrypted_message = crypto.rsa_decrypt(private_key, ciphertext)
    assert decrypted_message == message


def test_rsa_sign_verify():
    """Test signing a message and verifying the signature."""
    private_key = crypto.load_private_key()
    public_key = crypto.load_public_key()

    message = b"Test RSA signing"
    signature = crypto.sign_message(private_key, message)

    # Valid signature should verify correctly
    assert crypto.verify_signature(public_key, message, signature) is True

    # If we change the message, the signature verification should fail
    tampered_message = b"Tampered RSA signing"
    assert crypto.verify_signature(public_key, tampered_message, signature) is False


def test_generate_aes_key():
    """Test that generate_aes_key returns a 16-byte key."""
    key = crypto.generate_aes_key()
    assert isinstance(key, bytes)
    assert len(key) == 16


def test_aes_encryption_decryption():
    """Test AES-GCM encryption and decryption."""
    key = crypto.generate_aes_key()
    plaintext = b"Test AES-GCM encryption"
    associated_data = b"header"

    # Encrypt the plaintext
    result = crypto.aes_encrypt(key, plaintext, associated_data)
    assert "nonce" in result
    assert "ciphertext" in result

    nonce = result["nonce"]
    ciphertext = result["ciphertext"]

    # Ensure ciphertext is not equal to plaintext
    assert ciphertext != plaintext

    # Decrypt the ciphertext
    decrypted_text = crypto.aes_decrypt(key, nonce, ciphertext, associated_data)
    assert decrypted_text == plaintext


def test_aes_decryption_with_invalid_associated_data():
    """Test that using incorrect associated data causes decryption to fail."""
    key = crypto.generate_aes_key()
    plaintext = b"Another test for AES"
    associated_data = b"valid header"
    wrong_associated_data = b"invalid header"

    result = crypto.aes_encrypt(key, plaintext, associated_data)
    nonce = result["nonce"]
    ciphertext = result["ciphertext"]

    # Attempt decryption with wrong associated data should raise an exception
    with pytest.raises(Exception):
        crypto.aes_decrypt(key, nonce, ciphertext, wrong_associated_data)
