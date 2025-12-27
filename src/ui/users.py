"""Textual UI User registration and login screens"""

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Input, Button, Label
from textual.containers import Vertical
from textual.screen import Screen

from src.logging.logging import AuditLog
from src.manager.password_manager import PasswordManager
from src.ui.vault import VaultScreen
from src.common.exceptions import UserInvalidLoginException, UsernameTakenException
from src.user.user_manager import UserManager

class RegisterScreen(Screen):
    """
    Textual screen for registering a new user
    """
    def __init__(self, user_manager: UserManager, log: AuditLog):
        super().__init__()
        self.user_manager = user_manager
        self.__logger = log

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id='register'):
            yield Label('Registration:')
            yield Input(placeholder='Username: ', id='username')
            yield Input(placeholder='Password: ', id='password', password=True)
            yield Button("Register", id="register-btn")
            yield Button('Go to login', id="login-btn")
        yield Footer()

    def on_button_pressed(self, btn: Button.Pressed) -> None:
        if btn.button.id == 'login-btn':
            self.app.push_screen(LoginScreen(self.user_manager, self.__logger))
            return

        user = self.query_one('#username', Input).value
        pwd = self.query_one('#password', Input).value

        try:
            self.user_manager.register_user(user, pwd)
        except UsernameTakenException:
            self.app.notify('This username is already taken!', severity='error')
            return

        self.app.notify('Registration successful!', severity="information")
        self.app.push_screen(LoginScreen(self.user_manager, self.__logger))

        self.query_one('#username', Input).clear()
        self.query_one('#password', Input).clear()

class LoginScreen(Screen):
    """
    Textual screen for logging a user in
    """
    def __init__(self, user_manager: UserManager, log: AuditLog):
        super().__init__()
        self.user_manager = user_manager
        self.__logger = log

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id='login'):
            yield Label('Login:')
            yield Input(placeholder='Username: ', id='username')
            yield Input(placeholder='Password: ', id='password', password=True)
            yield Button("Login", id="unlock")
            yield Button('Go to registration', id="register")
        yield Footer()

    def on_button_pressed(self, btn: Button.Pressed) -> None:
        if btn.button.id == 'register':
            self.app.push_screen(RegisterScreen(self.user_manager, self.__logger))
            return

        user = self.query_one('#username', Input).value
        pwd = self.query_one('#password', Input).value

        try:
            master_key = self.user_manager.login_user(user, pwd)
        except UserInvalidLoginException:
            self.app.notify('Invalid username or password', severity='error')
            return

        pwd_manager = PasswordManager(user, master_key, self.__logger)
        self.app.push_screen(VaultScreen(pwd_manager, self.user_manager))
        self.app.notify('Login successful!', severity="information")

        self.query_one('#username', Input).clear()
        self.query_one('#password', Input).clear()
