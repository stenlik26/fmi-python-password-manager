"""Textual screen for password entry management"""

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Label
from textual.containers import Vertical
from textual.screen import Screen

from src.manager.password_manager import LoginEntry, PasswordManager


class EntryScreen(Screen):
    """
    Textual screen for password entry management
    """
    def __init__(self, entry: LoginEntry):
        super().__init__()
        self.__entry = entry

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Return'),
        ('r', 'reveal_pass', 'Reveal password'),
        ('c', 'copy_pass', 'Copy password to clipboard'),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
         Label(f'Address: {self.__entry.address}'),
         Label(f'Username: {self.__entry.username}'),
         Label(f'Group: {self.__entry.group}'),
         Label('Password: <press-r-to-reveal>', id="password-label"),
            id="entry_screen",
        )
        yield Footer()

    def on_mount(self) -> None:
        pass

    def action_reveal_pass(self) -> None:
        label = self.query_one('#password-label', Label)
        label.update(f'Password: {self.__entry.password}')

    def action_copy_pass(self) -> None:
        PasswordManager.copy_password_to_clipboard(self.__entry.password)
        self.app.notify('Password copied to clipboard')
