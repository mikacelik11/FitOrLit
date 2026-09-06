class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.users = []

    # Sign up function for user, it first checks if the username already exists if so the function fails and should
    # reprompt the user to login in again until a valid username is made.
    def signUp(self):
        username = input("Make your username: ")
        password = input("Make your password: ")
        
        user = User(username, password)
    
        for i in range(len(self.users)):
            if self.users[i].username == user.username:
                print("account already exists")
                return False
            
            
        self.users.append(user)
        print(user.username)
        print("account made")
        return True
    
    
p1 = User('', '')
p1.signUp()
p1.signUp()