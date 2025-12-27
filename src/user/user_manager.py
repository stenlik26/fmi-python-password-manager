"""
Class for managing users
"""

from dataclasses import dataclass, asdict
import json
from pathlib import Path

from src.common.exceptions import UsernameTakenException, UserInvalidLoginException
import src.common.generators as generators
import src.common.encryption as encryption
from src.logging.logging import AuditLog


@dataclass
class User:
    """
    User dataclass is used for easier management of user's info.
    """
    password_salt: str
    password_hash: str
    username: str
    master_password_salt: str
    groups: list[str]

class UserManager:
    """
    Class used for managing users. Uses a json file as persistent storage of users
    """

    def __init__(self, logger: AuditLog, user_file_path: str = 'users.json'):
        self.__logger = logger
        self.__user_file = Path(user_file_path)

        if not self.__user_file.exists():
            self.__user_file.write_text(json.dumps({}), encoding='utf-8')

        self.__users = self.__load_users()

    def register_user(self, username: str, password: str) -> None:
        """
        Registers a user with a username/password combination.
        Throws an exception if the username is already taken.
        """
        if username in self.__users or username.strip() == '':
            self.__logger.log('A user tried to register with an empty or registered username.')
            raise UsernameTakenException

        password_salt = generators.generate_salt()
        hashed_password = generators.generate_hashed_password(password, password_salt)

        master_salt = generators.generate_salt()
        self.__users[username] = User(
            password_salt,
            hashed_password,
            username,
            master_salt,
            []
        )

        self.__logger.log_with_user('A new user has been registered', username)
        self.__save_users()

    def login_user(self, username: str, password: str) -> bytes:
        """
        Login for a user. Returns the key used for encrypting the passwords, 
        Throws an exception if the user doesn't exist or has entered an invalid password.
        """

        if username not in self.__users:
            self.__logger.log('A user tried to login with an invalid username.')
            raise UserInvalidLoginException

        user = self.__users[username]
        if generators.generate_hashed_password(password, user.password_salt) != user.password_hash:
            self.__logger.log('A user tried to login with an invalid password.')
            raise UserInvalidLoginException

        self.__logger.log_with_user('User logged in', username)
        return encryption.password_to_fernet_key(password, user.master_password_salt.encode())

    def create_group(self, username: str, group_name: str) -> None:
        """Creates a group with the given name for the input user."""
        self.__logger.log_with_user(f'A new group has been registered: {group_name}', username)

        self.__users[username].groups.append(group_name)
        self.__save_users()

    def fetch_groups(self, username: str) -> list[str]:
        """Fetches all groups associated with the user."""
        self.__logger.log_with_user('Request to fetch all groups', username)

        return self.__users[username].groups

    def delete_group(self, username: str, group_name: str) -> None:
        """Deletes a group with the given name for the input user."""
        self.__logger.log_with_user(f'A group has been deleted: {group_name}', username)

        self.__users[username].groups.remove(group_name)

    def __save_users(self) -> None:
        json_users = json.dumps([asdict(v) for v in self.__users.values()])
        self.__user_file.write_text(json_users, encoding='utf-8')

        self.__logger.log('User file has been saved')

    def __load_users(self) -> dict[str, User]:
        self.__logger.log('Loading user file')

        data = json.loads(self.__user_file.read_text(encoding='utf-8'))
        return {d['username']: User(**d) for d in data}
