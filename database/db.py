import sqlite3

from config import DATABASE_PATH


def get_connection():
    """Create and return a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the tickets table if it does not already exist."""
    connection = get_connection()

    try:
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

        connection.commit()

    finally:
        connection.close()