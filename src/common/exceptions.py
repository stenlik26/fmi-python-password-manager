""" Exceptions used in the project """

class UsernameTakenException(Exception):
    """
    UsernameTakenException is used when a user tries to register with a taken username
    """

class UserInvalidLoginException(Exception):
    """
    UserInvalidLoginException is used when an invalid username/password combination is used
    """

class InvalidEntryException(Exception):
    """
    InvalidEntryException is used when an invalid entry id is requested
    """
