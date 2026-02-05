import pytest
from cryptography.fernet import InvalidToken

import src.common.encryption as encryption

def test_encryption():
    pwd = "password"
    salt = b"1234"

    text = "I need to be encrypted and decrypted properly :)"

    key = encryption.password_to_fernet_key(pwd, salt)

    assert text == encryption.decrypt(encryption.encrypt(text, key), key)

def test_encryption_diff_key():
    pwd = "password"
    salt = b"1234"

    text = "I need to be encrypted and decrypted properly :)"

    key = encryption.password_to_fernet_key(pwd, salt)
    key2 = encryption.password_to_fernet_key("abc", salt)

    with pytest.raises(InvalidToken):
        encryption.decrypt(encryption.encrypt(text, key), key2)