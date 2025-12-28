"""
Class for managing user passwords
"""
import copy
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import uuid
import pyperclip

import src.common.encryption as encryption
from src.common.config import APP_DATA_DIR
from src.common.exceptions import InvalidEntryException
from src.logging.logging import AuditLog, Level

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

@dataclass
class LoginEntry:
    """
    LoginEntry contains information about a specific site / account linked to a user
    """
    id: str
    username: str
    password: str
    address: str
    group: str
    created_at: str
    updated_at: str

class PasswordManager:
    """Class for managing user password entries, with CRUD operations and search functionality"""
    def __init__(self, username: str, master_password: bytes, log: AuditLog, storage_path: Path | str = None):
        self.__logger = log
        self.__username = username
        self.__master_password = master_password
        self.__path = self.__init_dirs(storage_path)
        self.__user_passwords = self.__load_passwords()

    def create_entry(
            self, address: str, username: str,
            password: str, group: str = '') -> LoginEntry:
        """
        Creates a new login entry
        """
        entry = LoginEntry(
            id=str(uuid.uuid4()),
            username=username,
            password=encryption.encrypt(password, self.__master_password),
            address=address,
            group=group,
            created_at=datetime.now().strftime(TIME_FORMAT),
            updated_at=datetime.now().strftime(TIME_FORMAT),
        )

        self.__user_passwords[entry.id] = entry
        self.__save_passwords()

        self.__logger.log_with_user('A new password has been saved', self.__username)
        return entry

    def fetch_entry_by_id(self, entry_id: str) -> LoginEntry | None:
        """
        Fetch entry by id, returns None if the entry does not exist
        """
        if entry_id not in self.__user_passwords:
            self.__logger.log_with_user('An invalid entry has been fetched',
                                        self.__username, Level.ERROR)
            return None

        entry = copy.deepcopy(self.__user_passwords[entry_id])
        entry.password = encryption.decrypt(entry.password, self.__master_password)

        self.__logger.log_with_user(f'Fetched password entry {entry_id}', self.__username)
        return entry

    def edit_entry(self, entry_id: str, entry: LoginEntry) -> None:
        """
        Edit entry by id, the function accepts the new entry and sets it to the existing id
        """
        if entry_id not in self.__user_passwords:
            self.__logger.log_with_user('Invalid input entry on edit', self.__username, Level.ERROR)
            raise InvalidEntryException

        entry.password = encryption.encrypt(entry.password, self.__master_password)
        entry.updated_at = datetime.now().strftime(TIME_FORMAT)

        self.__user_passwords[entry_id] = entry
        self.__save_passwords()

        self.__logger.log_with_user(f'Edited password entry {entry_id}', self.__username)

    def delete_entry(self, entry_id: str) -> LoginEntry | None:
        """
        Delete entry by id, returns None if the entry does not exist
        """
        if entry_id not in self.__user_passwords:
            self.__logger.log_with_user('Invalid input entry on delete',
                                         self.__username, Level.ERROR)
            return None

        entry = self.__user_passwords[entry_id]
        del self.__user_passwords[entry_id]
        self.__save_passwords()

        self.__logger.log_with_user(f'Deleted password entry {entry_id}', self.__username)
        return entry

    def list_passwords(self) -> list[LoginEntry]:
        """
        Returns a list of all passwords
        """
        self.__logger.log_with_user('Listing passwords', self.__username)
        return [entry for entry in self.__user_passwords.values()]

    def search_by_username(self, username_match: str) -> list[LoginEntry]:
        """
        Returns a list of all password entries containing the input username
        """
        self.__logger.log_with_user('Searching passwords by username', self.__username)
        return list(
            filter(
                lambda entry: username_match in entry.username,
                self.__user_passwords.values()
                )
            )

    def search_by_address(self, address_match: str) -> list[LoginEntry]:
        """
        Returns a list of all password entries containing the input address
        """
        self.__logger.log_with_user('Searching passwords by address', self.__username)
        return list(
            filter(
                lambda entry: address_match in entry.address,
                self.__user_passwords.values()
                )
            )

    def search_by_groups(self, *groups_match: str) -> list[LoginEntry]:
        """
        Returns a list of all passwords, where the entry group matches one of the input groups
        """
        self.__logger.log_with_user('Searching passwords by group', self.__username)
        return list(
            filter(
                lambda entry: entry.group in groups_match,
                self.__user_passwords.values()
                )
            )

    def get_username(self) -> str:
        """Returns the username of the current user"""
        return self.__username


    @staticmethod
    def copy_password_to_clipboard(password: str) -> None:
        """Copies the given password to the clipboard"""
        pyperclip.copy(password)

    def __init_dirs(self, storage_path: Path | str | None) -> Path:
        self.__logger.log_with_user('Initializing password manager', self.__username)

        if storage_path is not None:
            base_dir = Path(storage_path) / "user_passwords"
        else:
            base_dir = APP_DATA_DIR / "user_passwords"

        base_dir.mkdir(parents=True, exist_ok=True)

        return base_dir

    def __load_passwords(self) -> dict[str, LoginEntry]:
        # TODO: file exceptions
        user_file = self.__path / f'{self.__username}.json'

        if not user_file.exists():
            user_file.write_text(
                json.dumps({}),
                encoding='utf-8'
            )

        passwords = json.loads(user_file.read_text(encoding='utf-8'))

        self.__logger.log_with_user('Loaded passwords', self.__username)
        return {entry['id']:LoginEntry(**entry) for entry in passwords}

    def __save_passwords(self) -> None:
        user_file = self.__path / f'{self.__username}.json'

        passwords = json.dumps([asdict(ent) for ent in self.__user_passwords.values()])

        user_file.write_text(passwords, encoding='utf-8')

        self.__logger.log_with_user('Saved passwords', self.__username)
