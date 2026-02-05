# Password Manager

A simple, console-based Password Manager project built with Python and Textual.

## Description

This application allows users to securely store, generate, and manage passwords for various websites and accounts. It features a Textual User Interface (TUI) for ease of use directly from the console.

## Features

- **User Accounts**: Multi-user support with secure registration and login.
- **Encryption**: Strong encryption (AES) using the `cryptography` library. Passwords are never stored in plain text.
- **Password Generator**: Built-in tool to generate strong, random passwords.
- **Grouping**: Organize your passwords into custom groups (e.g., Work, Personal, Banking).
- **Clipboard Integration**: Easily copy passwords to your clipboard for quick use.
- **Audit Logging**: Tracks security-critical actions (login, access, modification).

## Installation

1.  Clone the repository.
2.  Install the dependencies:

```bash
git clone https://github.com/stenlik26/fmi-python-password-manager

cd fmi-python-password-manager

pip install -r requirements.txt
```

## Usage

To start the application, run:

```bash
python main.py
```

### Controls

-   **Mouse**: The UI supports mouse interactions.
-   **Keyboard navigation**: Use `Tab` and `Arrow Keys` to navigate.
-   **Shortcuts**:
    -   `d`: Toggle Dark Mode
    -   `c`: Create new entry
    -   `e`: Edit selected entry
    -   `Del`: Delete selected entry
    -   `p`: Open Password Generator
    -   `g`: Create new Group
    -   `f`: Filter by Group
    -   `Esc`: Logout / Back
-   **Exit**: `Ctrl+Q`
