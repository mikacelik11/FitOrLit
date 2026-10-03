from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import database

ph = PasswordHasher()

# forzen set means it cannot be accidently modified 
SPECIAL_CHARACTERS = frozenset("!@#$%^&*()_+.")

class User:
    def __init__(self, user_id, username, password_hash):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        

class UserStore:
    def __init__(self, database_path = database.DATABASE_PATH):
        self.database_path = database_path
        self.current_user = None
        
        database.initialize_database(self.database_path)
    # takes in a username and password and creates a user object and appends to list
    # of users if the username is unique
    
    # password must follow these set of rules, if not then an error message must be thrown so they try again
    def password_error(self, password):
        if not any(character in SPECIAL_CHARACTERS for character in password):
            return "Password must contain at least 1 special characters !@#$%^&*()_+."
        elif len(password) < 6:
            return "Password must be at least 6 characters long"
        
        return None
        
    # fixed register function
    def register(self, username, password):
        # call the get user in the database is a user is found this means the username is taken
    
        user_exist = database.get_user_by_username(username, database_path=self.database_path)
        if user_exist:
            return False
            
        # if there is now password error hash the password and then return that user was registered.
        if self.password_error(password) is None:
            hash_p = ph.hash(password)
            user = database.create_user(username, hash_p, database_path=self.database_path)
            if user: 
                return True
        
        return False
        
    # prompts the user to create an account and if the username is already taken it
    # reprompts the user until they enter a valid unique username.   
    def signUp(self):
        while True:
            un = input("Make your username: ")
            pw = input("Make your password: ")
            
            if self.register(un, pw):
                print("account made")
                return True
            print("account already exists, try again")
       
       
    # finds user why searching through our user list and finding if an account matches those credentails     
    def find_user(self, username):
        # must call database
        user = database.get_user_by_username(username, database_path=self.database_path)
        if user is None:
            return None
        
        # The database row contains the account ID, username, and password hash.
        found_user = User(user[0], user[1], user[2])
        return found_user
            
    # user logs in and we find the user by username because each username must be unique
    # once a user is found we check if his hashed password is the same as the password he typed out
    # if so current user is set else we return an error
    def login(self, username, password):
        user = self.find_user(username)
        if user is None:
            return False
        
        try:
            ph.verify(user.password_hash, password)
        except VerifyMismatchError:
            return False
            
        self.current_user = user
        return True
        
    # logout will take in a flag so when a user logs in the flag will be set to true so for a usr to logout their flag will need to be set to false
    # this flag will be checked for everything else in our application.    
    def logout(self):
        self.current_user = None
        
    # Check if the current user is logged in
    def is_logged_in(self):
        return self.current_user is not None
