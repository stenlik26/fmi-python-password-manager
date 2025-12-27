"""Audit logging module."""

from enum import Enum
from pathlib import Path
from datetime import datetime

class Level(Enum):
    """Enum for log levels."""
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

class AuditLog:
    """Class for audit logging."""
    def __init__(self, path: str) -> None:
        self.__logfile = Path(path)
        if not self.__logfile.exists():
            self.__logfile.write_text('', encoding='utf-8')

    def log(self, msg: str, lvl: Level = Level.INFO) -> None:
        """Logs a message with a given level."""

        with self.__logfile.open('a', encoding='utf-8') as f:
            f.write(f'{datetime.now().isoformat()} - {lvl.name} - {msg}\n')

    def log_with_user(self, msg: str,  usr: str, lvl: Level = Level.INFO) -> None:
        """Logs a message with a given level and user."""
        with self.__logfile.open('a', encoding='utf-8') as f:
            f.write(f'{datetime.now().isoformat()} - {lvl.name} - (User: {usr}) - {msg}\n')
