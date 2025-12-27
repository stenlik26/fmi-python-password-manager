"""The main UI application for the PasswordManager."""

from textual.app import App

from src.logging.logging import AuditLog
from src.ui.users import LoginScreen
from src.user.user_manager import UserManager


class PasswordManagerApp(App):
    """The UI component of the PasswordManager"""

    CSS_PATH = 'style.tcss'

    def __init__(self, usr_mgr: UserManager, log: AuditLog):
        super().__init__()
        self.__usr_mgr = usr_mgr
        self.__logger = log

    def on_mount(self) -> None:
        self.push_screen(LoginScreen(self.__usr_mgr, self.__logger))
