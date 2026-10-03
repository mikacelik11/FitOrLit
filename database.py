import sqlite3
from pathlib import Path


# sqlite3 communicates with SQLite
# Path helps place the database beside database.py
# regardless of where you run the program from


# represents the current python file and with_name selects a database file in the same directory
DATABASE_PATH = Path(__file__).with_name("fitorlit.db")

# initalize function
def initialize_database(database_path=DATABASE_PATH):
    # SQLite opens fitorlit.db if the files does exist, SQLite creates it
    connection = sqlite3.connect(database_path)
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
  
# sql table that stoes all user health data     
def user_health_data(database_path=DATABASE_PATH):
    connection = sqlite3.connect(database_path)
    
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users_health_data (
                user_id INTEGER PRIMARY KEY,

                age INTEGER NOT NULL CHECK (age > 0),
                height_cm REAL NOT NULL CHECK (height_cm > 0),
                weight_kg REAL NOT NULL CHECK (weight_kg > 0),

                activity_factor REAL NOT NULL CHECK (activity_factor > 0),

                goal TEXT NOT NULL
                    CHECK (goal IN ('maintain', 'cut', 'bulk')),

                bmr_formula TEXT NOT NULL
                    CHECK (bmr_formula IN ('male', 'female')),

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        
        connection.commit()
        
    finally:
        connection.close()
        
def create_user(username, password_hash, database_path=DATABASE_PATH):
    connection = sqlite3.connect(database_path)
    
    try:
        ## creates a new row in users, placing one value in username and another in password_hash
        # the question marks are placeholders. the actual values are supplied separately
        # SQLite trates those values as data rather than executable SQL
        connection.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash),
        )
        # when user is successfully inserted
        connection.commit()
        return True
    # rejects the insert 
    # if you insert the same username twice then SQL raises sqlite3.integrityError
    except sqlite3.IntegrityError:
        return False
    # ensures the connection is closed properly
    finally:
        connection.close()
 
# gets user by their username       
def get_user_by_username(find_username, database_path=DATABASE_PATH):
    connection = sqlite3.connect(database_path)
    
    # select all attributes from that user and return those with that specific username
    try:
        user = connection.execute(
            """
            SELECT * FROM users
            WHERE username = ?
            """,
            (find_username,),
        )
        #fetch a single user thats why fetchone and not fetch all
        
        found = user.fetchone()
             
        # fetchone either returns the user or none
        return found
    finally:
        connection.close()
        
    

if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DATABASE_PATH}")