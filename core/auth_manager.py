"""
auth_manager.py
Authentication and user profile manager for ResuMetric AI.
Persists user credentials and display names in sample_data/users.json with secure password hashing.
"""

import os
import json
import hashlib
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

USERS_FILE = "sample_data/users.json"


def _ensure_users_file():
    """Ensures that the users storage file exists with default schema."""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)


def hash_password(password: str) -> str:
    """Generates a SHA-256 hash for a given password."""
    # Using SHA-256 hash with a fixed application salt
    salt = "resumetric_ai_secure_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


def get_all_users() -> Dict[str, Dict[str, Any]]:
    """Loads all registered users from persistent storage."""
    _ensure_users_file()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_users(users: Dict[str, Dict[str, Any]]) -> bool:
    """Saves user records to persistent storage."""
    _ensure_users_file()
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception:
        return False


def register_user(name: str, username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Registers a new user with their display name, username, and password.
    Returns (success, message, user_data).
    """
    clean_name = name.strip()
    clean_username = username.strip().lower()
    clean_password = password.strip()

    if not clean_name:
        return False, "Please enter your full name.", None

    if len(clean_name) < 2:
        return False, "Name must be at least 2 characters long.", None

    if not clean_username:
        return False, "Please choose a username.", None

    if len(clean_username) < 3:
        return False, "Username must be at least 3 characters.", None

    if not re.match(r"^[a-zA-Z0-9_.-]+$", clean_username):
        return False, "Username may only contain letters, numbers, dots, hyphens, and underscores.", None

    if not clean_password:
        return False, "Please enter a password.", None

    if len(clean_password) < 4:
        return False, "Password must be at least 4 characters.", None

    users = get_all_users()

    if clean_username in users:
        return False, f"Username '{clean_username}' is already taken. Please choose another or sign in.", None

    user_data = {
        "name": clean_name,
        "username": clean_username,
        "password_hash": hash_password(clean_password),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    users[clean_username] = user_data
    if _save_users(users):
        return True, "Account created successfully! Welcome aboard.", {
            "name": clean_name,
            "username": clean_username
        }
    else:
        return False, "Failed to save account to database. Please try again.", None


def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticates an existing user by username and password.
    Returns (success, message, user_data).
    """
    clean_username = username.strip().lower()
    clean_password = password.strip()

    if not clean_username:
        return False, "Please enter your username.", None

    if not clean_password:
        return False, "Please enter your password.", None

    users = get_all_users()

    if clean_username not in users:
        return False, "Username not found. Please create an account or verify your spelling.", None

    user = users[clean_username]
    if user.get("password_hash") != hash_password(clean_password):
        return False, "Incorrect password. Please try again.", None

    return True, "Signed in successfully!", {
        "name": user.get("name", clean_username),
        "username": clean_username,
        "created_at": user.get("created_at", "")
    }


def get_user_profile(username: str) -> Optional[Dict[str, Any]]:
    """Fetches user details excluding sensitive password hash."""
    users = get_all_users()
    clean_username = username.strip().lower()
    if clean_username in users:
        u = users[clean_username]
        return {
            "name": u.get("name", clean_username),
            "username": clean_username,
            "created_at": u.get("created_at", "")
        }
    return None
