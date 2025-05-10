"""User management module for the DSA Bot."""

from utils.file_handler import load_users, save_users

# Global users list
_users = []

def get_users():
    """Get the global users list."""
    global _users
    return _users

def set_users(new_users):
    """Set the global users list."""
    global _users
    _users = new_users

def load_all_users():
    """Load all users from file."""
    global _users
    _users = load_users()
    return _users

def save_all_users():
    """Save all users to file."""
    save_users(_users) 