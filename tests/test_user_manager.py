import pytest
import json
from unittest.mock import patch

from src.user.user_manager import UserManager, User
from src.logging.logging import Level
from src.common.exceptions import UsernameTakenException, UserInvalidLoginException

import src.user.user_manager as user_manager

class AuditLog:
    def __init__(self, path: str) -> None:
        pass

    def log(self, msg: str, lvl: Level = Level.INFO) -> None:
        pass

    def log_with_user(self, msg: str,  usr: str, lvl: Level = Level.INFO) -> None:
        pass


@pytest.fixture
def mock_generators():
    with patch.object(user_manager, "generators") as mock_gen:
        mock_gen.generate_salt.return_value = "mock_salt"
        mock_gen.generate_hashed_password.return_value = "mock_hashed_password"
        yield mock_gen

@pytest.fixture
def mock_encryption():
    with patch.object(user_manager, "encryption") as mock_enc:
        mock_enc.password_to_fernet_key.return_value = b"mock_fernet_key"
        yield mock_enc


@pytest.fixture
def manager(tmp_path, mock_generators):
    temp_file = tmp_path / "test_users.json"
    fake_logger = AuditLog("")
    return UserManager(logger=fake_logger, user_file_path=str(temp_file))

def test_init_creates_empty_file(tmp_path):
    temp_file = tmp_path / "new_users.json"
    assert not temp_file.exists()

    logger = AuditLog("")
    UserManager(logger=logger, user_file_path=str(temp_file))

    assert temp_file.exists()
    assert temp_file.read_text(encoding="utf-8") == "{}"


def test_register_user_success(tmp_path, manager,  mock_generators):
    manager.register_user("alice", "secret123")

    assert "alice" in manager._UserManager__users
    user = manager._UserManager__users["alice"]
    assert user.username == "alice"
    assert user.password_hash == "mock_hashed_password"

    mock_generators.generate_salt.assert_called()
    mock_generators.generate_hashed_password.assert_called_with("secret123", "mock_salt")


def test_register_user_saves_to_file(manager, tmp_path):
    manager.register_user("bob", "password")

    file_content = json.loads(manager._UserManager__user_file.read_text())

    assert len(file_content) == 1
    assert file_content[0]["username"] == "bob"


def test_register_duplicate_username_fails(manager):
    manager.register_user("alice", "pass")

    with pytest.raises(UsernameTakenException):
        manager.register_user("alice", "pass2")


def test_register_empty_username_fails(manager):
    with pytest.raises(UsernameTakenException):
        manager.register_user("", "pass")

    with pytest.raises(UsernameTakenException):
        manager.register_user("   ", "pass")


def test_login_success(manager, mock_encryption, mock_generators):
    manager.register_user("alice", "my_password")

    mock_generators.generate_hashed_password.return_value = "mock_hashed_password"

    key = manager.login_user("alice", "my_password")

    assert key == b"mock_fernet_key"
    mock_encryption.password_to_fernet_key.assert_called()


def test_login_invalid_username(manager):
    with pytest.raises(UserInvalidLoginException):
        manager.login_user("ghost", "pass")


def test_login_wrong_password(manager, mock_generators):
    manager.register_user("alice", "correct_pass")

    mock_generators.generate_hashed_password.side_effect = ["hash_A", "hash_B"]

    with pytest.raises(UserInvalidLoginException):
        manager.login_user("alice", "wrong_pass")

def test_group_management(manager):
    username = "alice"
    manager.register_user(username, "pass")

    manager.create_group(username, "admins")
    manager.create_group(username, "editors")
    groups = manager.fetch_groups(username)

    assert "admins" in groups
    assert "editors" in groups

    manager.delete_group(username, "admins")
    groups = manager.fetch_groups(username)
    assert "admins" not in groups
    assert "editors" in groups


def test_load_existing_users(tmp_path):
    f = tmp_path / "existing.json"
    pre_existing_data = [
        {
            "username": "dave",
            "password_salt": "s1",
            "password_hash": "h1",
            "master_password_salt": "ms1",
            "groups": ["groupA"]
        }
    ]
    f.write_text(json.dumps(pre_existing_data), encoding="utf-8")

    fake_logger = AuditLog("")
    manager = UserManager(logger=fake_logger, user_file_path=str(f))

    assert "dave" in manager._UserManager__users
    assert manager.fetch_groups("dave") == ["groupA"]