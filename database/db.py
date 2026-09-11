import sqlite3

from config import DATABASE_PATH


def get_connection():
    """Create and return a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the application tables if they do not already exist."""
    connection = get_connection()

    try:
        # Create the tickets table.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_date TEXT NOT NULL,
                assigned_to TEXT NOT NULL
            )
            """
        )

        # Create the users table.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_date TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'User',
                full_name TEXT NOT NULL DEFAULT ''
            )
            """
        )

        # Check the existing users table columns.
        columns = connection.execute(
            "PRAGMA table_info(users)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        # Add role to an existing database if the column is missing.
        if "role" not in column_names:
            connection.execute(
                """
                ALTER TABLE users
                ADD COLUMN role TEXT NOT NULL DEFAULT 'User'
                """
            )

        # Add full_name to an existing database if the column is missing.
        if "full_name" not in column_names:
            connection.execute(
                """
                ALTER TABLE users
                ADD COLUMN full_name TEXT NOT NULL DEFAULT ''
                """
            )

        connection.commit()

    finally:
        connection.close()