import sqlite3
from math import isfinite
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

    # Create the health table too, so it is ready when the user answers a question.
    user_health_data(database_path)
  
# NULL means the user has not answered that health question yet.
# CHECK constraints still validate answers that are supplied.
def user_health_data(database_path=DATABASE_PATH):
    connection = sqlite3.connect(database_path)
    
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users_health_data (
                user_id INTEGER PRIMARY KEY,

                age INTEGER CHECK (age > 0),
                height_cm REAL CHECK (height_cm > 0),
                weight_kg REAL CHECK (weight_kg > 0),

                activity_factor REAL CHECK (activity_factor > 0),

                goal TEXT
                    CHECK (goal IN ('maintain', 'cut', 'bulk')),

                bmr_formula TEXT
                    CHECK (bmr_formula IN ('male', 'female')),

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        
        connection.commit()
        
    finally:
        connection.close()
        
def save_health_data(
    user_id,
    database_path=DATABASE_PATH,
    *,
    age=None,
    height_cm=None,
    weight_kg=None,
    activity_factor=None,
    goal=None,
    bmr_formula=None,
):
    """Save any combination of health answers for an existing account.

    Omitted inputs and None leave existing answers unchanged; they do not
    clear answers. Return True after saving, or False for invalid answers,
    an unknown account, or a call with no answers to save.
    """
    # An ID is required: without it, SQLite could generate an unrelated ID.
    if type(user_id) is not int or user_id <= 0:
        return False
    if age is not None and (type(age) is not int or age <= 0):
        return False

    # Measurements can be whole numbers or decimals, but not text or booleans.
    for value in (height_cm, weight_kg, activity_factor):
        if value is not None:
            if type(value) not in (int, float) or value <= 0:
                return False
            if type(value) is float and not isfinite(value):
                return False

    if goal is not None and goal not in ("maintain", "cut", "bulk"):
        return False
    if bmr_formula is not None and bmr_formula not in ("male", "female"):
        return False

    # this groups the six values into a tuple so i can check them together
    
    answers = (age, height_cm, weight_kg, activity_factor, goal, bmr_formula)
    # goes throught each value in that tuple
    # value is None checks whether that answer is missing 
    # all(...) returns true only if every answer is missing
    # when that happends, return false immiediatley stops the fucntion because there is nothing to save 
    if all(value is None for value in answers):
        return False

    connection = sqlite3.connect(database_path)

    try:
        # Reject health answers for an account that does not exist.
        connection.execute("PRAGMA foreign_keys = ON") # Enforces the foreign ket ruels so it links a vlaue to a record in the otehr table 
        # in our instance this is for user_id
        
        # what on conflict does so on colfict reads as if inserting this user id would create a duplicate, update that users existing row instead
        # coalesce chooses the first value that isn't null, reading left to right. if both values are null the result is null
        # example: New age supplied -> use the new age
        # New age missing -> keep the saved data
        # we do this so that if a user only answeres one thing form this table they are kept as null but if they go back then they are updated
        # suppose account 7 exists:
        # they answer age. there is no profile yet, so SQLite inserts one. height remains null
        # later they anser height user id7 already exists in the health table so on clonfilct updates that row coalesce keeps age 25 because no new age was supplied
        # they change age 26 then the same row is updated again
        
        connection.execute(
            """
            INSERT INTO users_health_data (
                user_id, age, height_cm, weight_kg,
                activity_factor, goal, bmr_formula
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                age = COALESCE(excluded.age, users_health_data.age), 
                height_cm = COALESCE(excluded.height_cm, users_health_data.height_cm),
                weight_kg = COALESCE(excluded.weight_kg, users_health_data.weight_kg),
                activity_factor = COALESCE(
                    excluded.activity_factor, users_health_data.activity_factor
                ),
                goal = COALESCE(excluded.goal, users_health_data.goal),
                bmr_formula = COALESCE(
                    excluded.bmr_formula, users_health_data.bmr_formula
                )
            """,
            (user_id,) + answers,
        )
        # The first save creates the row. On later saves, COALESCE chooses
        # the supplied answer, or keeps the existing one if the input is NULL.
        connection.commit()
        return True

    except (sqlite3.IntegrityError, OverflowError):
        # OverflowError covers integers too large for SQLite to store.
        return False

    finally:
        connection.close()
  
# this is how this function should work
# 1. receive the users id and database path
# find their row in users_health_data
# return that row or None if they haven't saved any answers yet      
def get_health_data(user_id, database_path=DATABASE_PATH):
    connection = sqlite3.connect(database_path)
    
    try:
        data = connection.execute(
            '''
            SELECT * FROM users_health_data
            WHERE user_id = ?
            ''',
            # trailing comma so SQLite recieves a sequence containing one parameter
            (user_id,),
        )
        
        found = data.fetchone()
        
        return found
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
