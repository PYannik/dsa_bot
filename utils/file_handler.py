"""File handling utilities for the DSA Bot."""

from typing import List
from models.user import User
from config import INI_FILE_PATH

def load_users() -> List[User]:
    """Load users from the ini file.

    Returns:
        List[User]: List of loaded users
    """
    users = []
    try:
        with open(INI_FILE_PATH, 'r') as file:
            print(f'Loading character file from {INI_FILE_PATH}')
            for line in file:
                user = User.from_string(line)
                if user:
                    users.append(user)
            print(f'Loaded {len(users)} characters')
    except FileNotFoundError:
        print(f'No character file found at {INI_FILE_PATH}')
        try:
            with open(INI_FILE_PATH, 'x') as file:
                print(f'Created new character file at {INI_FILE_PATH}')
        except FileExistsError:
            pass
    return users

def save_users(users: List[User]) -> None:
    """Save users to the ini file.

    Args:
        users (List[User]): List of users to save
    """
    with open(INI_FILE_PATH, 'w') as file:
        for user in users:
            file.write(f'{user.to_string()}\n') 