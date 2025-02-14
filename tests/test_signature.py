import pytest
from src import signature


# A dummy replacement for verify_asym_sig that simply returns True.
def dummy_verify_asym_sig(pk, message, signature):
    return True


def test_valid_signature_verify(monkeypatch):
    # Create a valid signature string of 72 characters.
    valid_sig_str = "a" * 72
    # Patch the verify_asym_sig used inside the Signature class.
    monkeypatch.setattr(signature, "verify_asym_sig", dummy_verify_asym_sig)

    sig_obj = signature.Signature(valid_sig_str)
    # When verify is called, it should use our dummy and return True.
    result = sig_obj.verify("dummy_pk", "dummy_message")
    assert result is True


def test_invalid_signature_length():
    # Create a signature string with an invalid length (not 72 characters).
    invalid_sig_str = "a" * 70
    sig_obj = signature.Signature(invalid_sig_str)
    # Since the __init__ returns early, the signature attribute should not be set.
    assert not hasattr(sig_obj, "signature")
    # Calling verify() should now raise an AttributeError because 'signature' is missing.
    with pytest.raises(AttributeError):
        sig_obj.verify("dummy_pk", "dummy_message")


def test_from_base64_string_valid(monkeypatch):
    valid_sig_str = "b" * 72
    monkeypatch.setattr(signature, "verify_asym_sig", dummy_verify_asym_sig)

    sig_obj = signature.from_base64_string(valid_sig_str)
    # The returned Signature object should have the valid signature stored.
    assert hasattr(sig_obj, "signature")
    assert sig_obj.signature == valid_sig_str


def test_from_base64_string_invalid():
    invalid_sig_str = "b" * 70
    sig_obj = signature.from_base64_string(invalid_sig_str)
    # For an invalid signature string, no signature attribute should be set.
    assert not hasattr(sig_obj, "signature")
