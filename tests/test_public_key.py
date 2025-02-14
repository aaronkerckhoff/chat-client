import pytest
from src.public_key import PublicKey, from_base64_string


def test_public_key_valid():
    # A valid public key string with exactly 32 characters.
    valid_str = "A" * 32
    pk = PublicKey(valid_str)
    # The object should have the 'value' attribute set to the input string.
    assert hasattr(pk, "value")
    assert pk.value == valid_str


def test_public_key_invalid():
    # An invalid public key string (not 32 characters)
    invalid_str = "A" * 30
    pk = PublicKey(invalid_str)
    # Since the length is invalid, the 'value' attribute should not be set.
    assert not hasattr(pk, "value")


def test_from_base64_string_valid():
    valid_str = "B" * 32
    pk = from_base64_string(valid_str)
    # The returned PublicKey object should have a 'value' attribute set to the valid string.
    assert hasattr(pk, "value")
    assert pk.value == valid_str


def test_from_base64_string_invalid():
    invalid_str = "B" * 31
    pk = from_base64_string(invalid_str)
    # For an invalid input string, no 'value' attribute should be set.
    assert not hasattr(pk, "value")
