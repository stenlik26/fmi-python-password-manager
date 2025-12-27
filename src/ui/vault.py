"""Main textual screen module for password vault management"""

from textual.app import ComposeResult
from textual.widgets import Footer, Header, DataTable
from textual.screen import Screen

from src.manager.password_manager import PasswordManager, LoginEntry
from src.user.user_manager import UserManager
from src.ui.entry import EntryScreen
from src.ui.modals import (
    EditModal, DeleteModal,
    PasswordGeneratorModal, CreateGroupModal,
    FilterByGroupModal
)


class VaultScreen(Screen):
    """
    Textual screen for vault management
    """

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Logout'),
        ('f', 'filter_grp', 'Group filter'),
        ('Enter', 'enter_entry', 'View'),
        ('c', 'create_entry', 'Create'),
        ('e', 'edit_entry', 'Edit'),
        ('d', 'delete_entry', 'Delete'),
        ('p', 'generate_password', 'Generate'),
        ('g', 'create_group', 'Create group'),
    ]

    def __init__(self, pwd_manager: PasswordManager, user_manager: UserManager):
        super().__init__()
        self.pwd_manager = pwd_manager
        self.user_manager = user_manager


    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id='table', cursor_type='row')
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns('Address', 'Username', 'Created At', 'Updated At', 'Group')
        self.__load_table()
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key.value is None:
            return
        entry = self.pwd_manager.fetch_entry_by_id(event.row_key.value)
        if entry is None:
            return

        self.app.push_screen(EntryScreen(entry))

    def action_create_entry(self) -> None:
        self.app.push_screen(
            EditModal(
                "Create a new password entry", 
                None,
                self.user_manager.fetch_groups(self.pwd_manager.get_username())),
            self.__edit_callback
        )

    def action_edit_entry(self) -> None:
        table = self.query_one(DataTable)
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        if row_key.value is None:
            return

        entry = self.pwd_manager.fetch_entry_by_id(row_key.value)
        if entry is None:
            return

        self.app.push_screen(
            EditModal(
                "Edit an existing password entry", 
                entry,
                self.user_manager.fetch_groups(self.pwd_manager.get_username())),
            self.__edit_callback
        )

    def action_delete_entry(self) -> None:
        table = self.query_one(DataTable)
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        if row_key.value is None:
            return

        entry = self.pwd_manager.fetch_entry_by_id(row_key.value)
        if entry is None:
            return

        self.app.push_screen(
            DeleteModal(entry),
            self.__delete_callback
        )

    def action_generate_password(self) -> None:
        self.app.push_screen(
            PasswordGeneratorModal(),
            self.__generate_callback
        )

    def action_create_group(self) -> None:
        self.app.push_screen(
            CreateGroupModal(),
            self.__create_group_callback
        )

    def action_filter_grp(self) -> None:
        self.app.push_screen(
            FilterByGroupModal(self.user_manager.fetch_groups(self.pwd_manager.get_username())),
            self.__filter_callback
        )

    def __edit_callback(self, res: LoginEntry | None) -> None:
        if res is None:
            return

        if res.id != '':
            self.pwd_manager.edit_entry(res.id, res)
        else:
            self.pwd_manager.create_entry(res.address, res.username, res.password)

        self.__load_table()

    def __delete_callback(self, res: LoginEntry | None) -> None:
        if res is None:
            return

        self.pwd_manager.delete_entry(res.id)
        self.__load_table()

    def __generate_callback(self, res: str | None) -> None:
        if res is None or res == '':
            return

        entry = LoginEntry('', '', res, '', '', '', '')

        self.app.push_screen(
            EditModal(
                "Create a new password entry", 
                entry,
                self.user_manager.fetch_groups(self.pwd_manager.get_username())),
            self.__edit_callback
        )

    def __create_group_callback(self, res: str | None) -> None:
        if res is None or res == '':
            return

        self.user_manager.create_group(self.pwd_manager.get_username(), res)

    def __filter_callback(self, res: str | None) -> None:
        if res is None:
            self.app.notify('Listing all entries')
            self.__load_table()
            return

        self.app.notify(f'Listing entries with group: {res}', severity='warning')

        self.__load_table(res)

    def __load_table(self, group: str | None = None) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for e in self.pwd_manager.list_passwords():
            if group is None or e.group == group:
                table.add_row(e.address, e.username, e.created_at, e.updated_at, e.group, key=e.id)
