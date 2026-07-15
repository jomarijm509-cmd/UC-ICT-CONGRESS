

import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registration.db")

CAMPUSES = ["Main", "Banilad", "LM", "Pardo"]


def get_connection():
    """Return a new sqlite3 connection with row access by column name."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(seed=True):
    """Create the Registration table if it doesn't exist yet."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Registration (
            idNum      TEXT PRIMARY KEY,
            campus     TEXT NOT NULL,
            studFName  TEXT NOT NULL,
            studLName  TEXT NOT NULL,
            amountPaid REAL NOT NULL DEFAULT 0,
            attended   TEXT NOT NULL DEFAULT 'No'
        )
        """
    )
    conn.commit()

    if seed:
        cur.execute("SELECT COUNT(*) AS c FROM Registration")
        count = cur.fetchone()["c"]
        if count == 0:
            sample = [
                ("1234567", "LM", "Paul", "Yparoto", 425.00, "No"),
                ("2345678", "Banilad", "Janeth", "Borja", 400.00, "Yes"),
                ("3456789", "LM", "Shiela", "Mendez", 450.00, "No"),
                ("7654321", "Main", "Ruth", "Sombrana", 425.00, "No"),
                ("8765432", "Main", "John", "Tesorio", 400.00, "No"),
                ("9876543", "Banilad", "Rey", "Argote", 400.00, "No"),
                ("4567890", "Banilad", "Joseph", "Saing", 450.00, "No"),
            ]
            cur.executemany(
                """
                INSERT INTO Registration
                    (idNum, campus, studFName, studLName, amountPaid, attended)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                sample,
            )
            conn.commit()

    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_NAME}")
