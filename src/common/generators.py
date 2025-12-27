"""
Contains generator functions for salts used in encryption
"""

import random
from hashlib import sha256

ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def generate_salt() -> str:
    """ Generates a random salt string of length 8 """
    chars = []
    for _ in range(8):
        chars.append(random.choice(ALPHABET))

    return "".join(chars)

def generate_hashed_password(password: str, salt: str) -> str:
    """ Hashes password using sha256 with the given salt """
    return sha256((password + salt).encode('utf-8')).hexdigest()

def generate_password(length: int, use_caps: bool, use_symbols: bool, use_number: bool) -> str:
    """ Generates a random password of given length with options for caps, symbols and numbers """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    caps = alphabet.upper()
    symbols = '!@#$%^&*()'
    numbers = '0123456789'
    all_symbols = alphabet

    password = [random.choice(alphabet)]
    offset = 1

    if use_caps:
        all_symbols += caps
        password.append(random.choice(caps))
        offset += 1
    if use_symbols:
        all_symbols += symbols
        password.append(random.choice(symbols))
        offset += 1
    if use_number:
        all_symbols += numbers
        password.append(random.choice(numbers))
        offset += 1

    for _ in range(length - offset):
        password.append(random.choice(all_symbols))

    return ''.join(password)[:length]
