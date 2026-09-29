import sqlite3
from pathlib import Path


# sqlite3 communicates with SQLite
# Path helps place the database beside database.py
# regardless of where you run the program from


# represents the current python file and with_name selects a database file in the same directory
DATABASE_PATH = Path(__file__).with_name("fitorlit.db")

# initalize function
def initialize_database():
    # SQLite opens fitorlit.db if the files does exist, SQLite creates it
    connection = sqlite3.connect(DATABASE_PATH)
    # creates the table
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # saves the changes
        connection.commit()
        
    # section runs whether table creation succeeds or fails. This ensures the connection is closed properly.
    finally:
        connection.close()
        

if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DATABASE_PATH}")