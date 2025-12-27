"""Textual pop-up modals for user / password interactions."""

import copy

from textual.app import ComposeResult
from textual.widgets import Input, Button, Label, Static, Checkbox, Select
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal

from src.manager.password_manager import PasswordManager, LoginEntry

import src.common.generators as generators

ALL_FILTER = "<All>"

class EditModal(ModalScreen[LoginEntry | None]):
    """Modal dialog for editing / creating a login entry."""

    def __init__(self, prompt: str, entry: LoginEntry | None, groups: list[str]) -> None:
        super().__init__()
        if entry is None:
            self.__entry = LoginEntry("","","","","","","")
        else:
            self.__entry = entry

        self.__groups = copy.deepcopy(groups)
        self.__groups.append("")
        self.__prompt = prompt

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.__prompt),
            Label("Address:"),
            Input(id="address"),
            Label("Username:"),
            Input(id="username"),
            Label("Password:"),
            Input(id="password"),

            Label("Group:"),
            Select(
                options=[(g, g) for g in self.__groups],
                id="group",
            ),

            Horizontal(
                Button("OK", id="ok", variant="primary"),
                Button("Cancel", id="cancel"),
            ),
            id="dialog",
        )

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self.query_one("#address", Input).value = self.__entry.address
        self.query_one("#username", Input).value = self.__entry.username
        self.query_one("#password", Input).value = self.__entry.password
        self.query_one("#group", Select).value = self.__entry.group


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.__entry.address = self.query_one("#address",Input).value
            self.__entry.username = self.query_one("#username",Input).value
            self.__entry.password = self.query_one("#password",Input).value

            select_value = self.query_one("#group",Select[str]).value
            if select_value == Select.BLANK:
                select_value = ""

            self.__entry.group = str(select_value)
            self.dismiss(self.__entry)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event):
        self.dismiss(event.value)


class DeleteModal(ModalScreen[LoginEntry | None]):
    """Modal dialog asking the user to confirm deletion."""

    def __init__(self, entry: LoginEntry) -> None:
        super().__init__()
        self.entry = entry

    def compose(self):
        yield Vertical(
            Static(f"Are you sure you want to delete {self.entry.address} - {self.entry.username}", id="message"),
            Horizontal(
                Button("Delete", id="confirm", variant="error"),
                Button("Cancel", id="cancel"),
            ),
            id="dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#confirm", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.dismiss(self.entry)
        else:
            self.dismiss(None)


class PasswordGeneratorModal(ModalScreen[str]):
    """Modal for password generation and account creation."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Generate a Secure Password"),

            Horizontal(
                Label("Password Length:"),
                Input(placeholder="12", id="length_input"),
                id="length_container"
            ),

            Checkbox("Include Uppercase", id="uppercase"),
            Checkbox("Include Numbers", id="numbers"),
            Checkbox("Include Symbols", id="symbols"),

            Input(placeholder="Generated Password", id="password_display", disabled=True),

            Horizontal(
                Button("Generate Password", id="generate"),
                Button("Copy password", id="copy"),
                Button("Create Account", id="create"),
                Button("Cancel", id="cancel"),
                id="buttons"
            ),
            id="modal_content",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "generate":
            self.generate_password()
        elif button_id == "create":
            self.create_account()
        elif button_id == "cancel":
            self.dismiss("")
        elif button_id == "copy":
            pwd = self.query_one("#password_display", Input).value
            PasswordManager.copy_password_to_clipboard(pwd)
            self.app.notify("Password copied to clipboard")

    def generate_password(self) -> None:
        include_upper = self.query_one("#uppercase", Checkbox).value
        include_numbers = self.query_one("#numbers", Checkbox).value
        include_symbols = self.query_one("#symbols", Checkbox).value

        length_input = self.query_one("#length_input", Input).value
        try:
            length = max(1, int(length_input))
        except (ValueError, TypeError):
            length = 12

        generated_password = generators.generate_password(
            length, include_upper,
            include_symbols, include_numbers
        )
        self.query_one("#password_display", Input).value = generated_password

    def create_account(self) -> None:
        password = self.query_one("#password_display", Input).value
        if not password:
            return

        self.dismiss(password)

class CreateGroupModal(ModalScreen[str | None]):
    """
    Modal dialog asking the user to create a new group.
    """

    def __init__(self) -> None:
        super().__init__()

    def compose(self):
        yield Vertical(
            Static("Create a new group", id="message"),
            Vertical(
                Label("Group name:"),
                Input(id="group_name_input"),
                Horizontal(
                    Button("Create", id="accept"),
                    Button("Cancel", id="cancel_btn")
                )
            )
        )

    def on_mount(self) -> None:
        self.query_one("#group_name_input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        group_name = str(self.query_one("#group_name_input", Input).value)
        if event.button.id == "accept" and len(group_name.strip()) > 0:
            self.dismiss(group_name)
        else:
            self.dismiss(None)

class FilterByGroupModal(ModalScreen[str | None]):
    """
    Modal dialog asking the user to filter a group.
    """
    def __init__(self, groups: list[str]) -> None:
        super().__init__()
        self.__groups = copy.deepcopy(groups)
        self.__groups.insert(0, ALL_FILTER)


    def compose(self):
        yield Vertical(
            Static("Show entries for group", id="message"),
            Vertical(
                Select(
                    options=[(g, g) for g in self.__groups],
                    id="group_filter",
                ),
                Button("Filter", id="filter"),
            )
        )

    def on_mount(self) -> None:
        self.query_one("#group_filter", Select).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        select_value = self.query_one("#group_filter", Select).value
        if select_value == Select.BLANK or select_value == ALL_FILTER:
            self.dismiss(None)

        if event.button.id == "filter":
            self.dismiss(str(select_value))
        else:
            self.dismiss(None)
