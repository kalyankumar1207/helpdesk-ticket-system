from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_connection


def create_user(username, password, confirm_password):
    """Create a new user account."""

    username = username.strip()

    if not username:
        raise ValueError("Username is required.")

    if not password:
        raise ValueError("Password is required.")

    if not confirm_password:
        raise ValueError("Please confirm your password.")

    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters long.")

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    if password != confirm_password:
        raise ValueError(
            "Password and Confirm Password do not match."
        )

    password_hash = generate_password_hash(password)

    connection = get_connection()

    try:
        existing_user = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if existing_user:
            raise ValueError("Username already exists.")

        connection.execute(
            """
            INSERT INTO users (
                username,
                password_hash,
                created_date,
                role
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                password_hash,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "User",
            ),
        )

        connection.commit()

    finally:
        connection.close()


def authenticate_user(username, password):
    """Check username and password and return the user if valid."""

    username = username.strip()

    if not username or not password:
        return None

    connection = get_connection()

    try:
        user = connection.execute(
            """
            SELECT
                id,
                username,
                password_hash,
                role
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if user and check_password_hash(
            user["password_hash"],
            password,
        ):
            return user

        return None

    finally:
        connection.close()


def get_all_users():
    """Return all registered users."""

    connection = get_connection()

    try:
        users = connection.execute(
            """
            SELECT
                id,
                username,
                created_date,
                role
            FROM users
            ORDER BY id ASC
            """
        ).fetchall()

        return users

    finally:
        connection.close()