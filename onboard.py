class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        

class UserStore:
    def __init__(self):
        self.users = []
        self.current_user = None
    # takes in a username and password and creates a user object and appends to list
    # of users if the username is unique
    def register(self, username, password):
        for i in range(len(self.users)):
            if username == self.users[i].username:
                return False
            
        self.users.append(User(username, password))
        return True
        
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
    def find_user(self, username, password):
        for user in self.users:
            if user.username == username and user.password == password:
                return user
            
        return None
            
    # if user is found then login is accepted
    def login(self, username, password):
        user = self.find_user(username, password)
        if user is None:
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
        
            

           
        


    