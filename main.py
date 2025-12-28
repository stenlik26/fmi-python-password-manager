"""Main module"""

from src.logging.logging import AuditLog
from src.user.user_manager import UserManager
from src.ui.ui import PasswordManagerApp
from src.common.config import APP_DATA_DIR

def main():
    """Main function"""

    if not APP_DATA_DIR.exists():
        APP_DATA_DIR.mkdir()

    audit_log = AuditLog(APP_DATA_DIR / 'trail.log')
    usr_mgr = UserManager(audit_log, APP_DATA_DIR / 'users.json')

    app = PasswordManagerApp(usr_mgr, audit_log)
    app.run()


if __name__ == "__main__":
    main()
