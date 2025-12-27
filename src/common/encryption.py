""" Helper file for encryption related tasks"""
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

def password_to_fernet_key(password: str, salt: bytes) -> bytes:
    """ Derives a Fernet key from a password and salt using Scrypt KDF """
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)

def encrypt(subject: str, key: bytes) -> str:
    """ Encrypts a string using the provided Fernet key """
    fernet = Fernet(key)

    return fernet.encrypt(subject.encode()).decode()

def decrypt(subject: str, key: bytes) -> str:
    """ Decrypts a string using the provided Fernet key """
    fernet = Fernet(key)

    return fernet.decrypt(subject.encode()).decode()
