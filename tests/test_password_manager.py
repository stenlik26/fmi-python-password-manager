import pytest
import json
from unittest.mock import patch
from datetime import datetime

from src.manager.password_manager import PasswordManager, LoginEntry
from src.common.exceptions import InvalidEntryException
from src.logging.logging import Level

import src.manager.password_manager as pwd_manager

class AuditLog:
    def __init__(self, _: str) -> None:
        pass

    def log(self, msg: str, lvl: Level = Level.INFO) -> None:
        pass

    def log_with_user(self, msg: str, usr: str, lvl: Level = Level.INFO) -> None:
        pass


@pytest.fixture
def mock_encryption():
    with patch.object(pwd_manager, "encryption") as mock_enc:
        mock_enc.encrypt.side_effect = lambda data,k : f"enc_{data}"
        mock_enc.decrypt.side_effect = lambda data,k : data.replace(f"enc_", "")

        yield mock_enc


@pytest.fixture
def mock_uuid():
    with patch.object(pwd_manager, "uuid") as mock_id:
        mock_id.uuid4.return_value = "fixed-uuid-1234"
        yield mock_id


@pytest.fixture
def mock_datetime():
    with patch.object(pwd_manager, "datetime") as mock_dt:
        fixed_time = datetime(2025, 1, 1, 12, 0, 0)
        mock_dt.now.return_value = fixed_time
        mock_dt.strftime.return_value = "2025-01-01 12:00:00"
        yield mock_dt


@pytest.fixture
def mock_pyperclip():
    with patch.object(pwd_manager, "pyperclip") as mock_clip:
        yield mock_clip


@pytest.fixture
def manager(tmp_path):
    fake_logger = AuditLog("")

    return PasswordManager(
        username="alice",
        master_password=b"master_key",
        log=fake_logger,
        storage_path=tmp_path
    )

def test_init_creates_directory_and_file(manager, tmp_path):
    expected_dir = tmp_path / "user_passwords"
    expected_file = expected_dir / "alice.json"

    assert expected_dir.exists()
    assert expected_file.exists()
    assert expected_file.read_text(encoding="utf-8") == "{}"


def test_create_entry(manager, mock_encryption, mock_uuid, mock_datetime):
    entry = manager.create_entry(
        address="example.com",
        username="user1",
        password="my_password",
        group="social"
    )

    assert entry.id == "fixed-uuid-1234"
    assert entry.password == "enc_my_password"
    assert entry.created_at == "2025-01-01 12:00:00"

    mock_encryption.encrypt.assert_called_with("my_password", b"master_key")

    saved_entry = manager._PasswordManager__user_passwords["fixed-uuid-1234"]
    assert saved_entry.username == "user1"


def test_fetch_entry_decrypts_password(manager, mock_encryption, mock_uuid):
    manager.create_entry("site.com", "user", "secret_pass")

    fetched = manager.fetch_entry_by_id("fixed-uuid-1234")

    assert fetched is not None
    assert fetched.password == "secret_pass"
    mock_encryption.decrypt.assert_called_with("enc_secret_pass", b"master_key")


def test_fetch_entry_invalid_returns_none(manager):
    result = manager.fetch_entry_by_id("non-existent-id")
    assert result is None


def test_edit_entry_success(manager, mock_encryption, mock_uuid, mock_datetime):
    manager.create_entry("site.com", "user", "old_pass")

    entry_to_update = manager.fetch_entry_by_id("fixed-uuid-1234")
    entry_to_update.password = "new_pass"
    entry_to_update.username = "new_user"

    manager.edit_entry("fixed-uuid-1234", entry_to_update)

    saved_entry = manager._PasswordManager__user_passwords["fixed-uuid-1234"]
    assert saved_entry.username == "new_user"
    assert saved_entry.password == "enc_new_pass"
    assert saved_entry.updated_at is not None


def test_edit_entry_invalid_id_raises_exception(manager):
    fake_entry = LoginEntry("id", "u", "p", "a", "g", "c", "u")

    with pytest.raises(InvalidEntryException):
        manager.edit_entry("bad-id", fake_entry)


def test_delete_entry(manager, mock_encryption, mock_uuid):
    manager.create_entry("site.com", "user", "pass")

    deleted = manager.delete_entry("fixed-uuid-1234")

    assert deleted is not None
    assert "fixed-uuid-1234" not in manager._PasswordManager__user_passwords

    user_file = manager._PasswordManager__path / "alice.json"
    data = json.loads(user_file.read_text())
    assert data == []


def test_search_by_username(manager, mock_encryption):
    manager.create_entry("site1", "alice_work", "p1")
    manager.create_entry("site2", "bob_home", "p2")

    results = manager.search_by_username("alice")

    assert len(results) == 1
    assert results[0].address == "site1"


def test_search_by_groups(manager, mock_encryption):
    manager.create_entry("site1", "u1", "p1", group="work")
    manager.create_entry("site2", "u2", "p2", group="personal")
    manager.create_entry("site3", "u3", "p3", group="work")

    results = manager.search_by_groups("work")

    assert len(results) == 2

    results_multi = manager.search_by_groups("work", "personal")
    assert len(results_multi) == 3


def test_copy_password_to_clipboard(manager, mock_pyperclip):
    manager.copy_password_to_clipboard("secret123")
    mock_pyperclip.copy.assert_called_with("secret123")


def test_get_username(manager):
    assert manager.get_username() == "alice"