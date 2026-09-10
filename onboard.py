class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        

class UserStore:
    def __init__(self):
        self.users = []
    # takes in a username and password and creates a user object and appends to list
    # of users if the username is unique
    def register(self, username, password):
        for i in range(len(self.users)):
            if username in self.users[i].username:
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
            

           
        


    