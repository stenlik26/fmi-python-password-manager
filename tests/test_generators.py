import src.common.generators as generators

def test_generate_salt():
    salt = generators.generate_salt()
    assert len(salt) == 8 and " " not in salt

def test_hash_password():
    pwd = "iNeedToBeHashed123"
    salt = "1234"

    hashed = generators.generate_hashed_password(pwd, salt)

    assert hashed != pwd and len(hashed) == 64

def test_generate_password():
    pwd = generators.generate_password(16, True, False, True)

    alphabet = "abcdefghijklmnopqrstuvwxyz"
    alphabet += alphabet.upper()
    alphabet += "0123456789"

    alphabet_set = set(alphabet)
    pwd_set = set(pwd)

    assert len(pwd) == 16 and pwd_set.issubset(alphabet_set)

def test_generate_password2():
    pwd = generators.generate_password(8, False, True, False)

    alphabet = "abcdefghijklmnopqrstuvwxyz!@#$%^&*()"

    alphabet_set = set(alphabet)
    pwd_set = set(pwd)

    assert len(pwd) == 8 and pwd_set.issubset(alphabet_set)