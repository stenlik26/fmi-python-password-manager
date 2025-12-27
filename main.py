"""Main module"""

from src.logging.logging import AuditLog
from src.user.user_manager import UserManager
from src.ui.ui import PasswordManagerApp

def main():
    """Main function"""

    audit_log = AuditLog('trail.log')
    usr_mgr = UserManager(audit_log)

    app = PasswordManagerApp(usr_mgr, audit_log)
    app.run()


if __name__ == "__main__":
    main()
