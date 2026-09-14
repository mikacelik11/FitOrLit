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
       
       
    # finds user why searching through our user list and finding if an account matches those credentails     
    def find_user(self, username, password):
        for user in self.users:
            if user.username == username and user.password == password:
                return True
            
        return False
            
    # if user is found then login is accepted
    def login(self, username, password):
        if self.find_user(username, password):
            return True
        else:
            return False
        
    # logout will take in a flag so when a user logs in the flag will be set to true so for a usr to logout their flag will need to be set to false
    # this flag will be checked for everything else in our application.    
    def logout(self, checker):
        if checker == True:
            checker = False
            return checker
        
        return checker
        
            

           
        


    