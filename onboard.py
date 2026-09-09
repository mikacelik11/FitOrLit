class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        

class UserStore:
    def __init__(self):
        self.users = []

    def register(self, username, password):
        for i in range(len(self.users)):
            if username in self.users[i].username:
                return False
            
        self.users.append(User(username, password))
        return True
        
        
    def signUp(self):
        while True:
            un = input("Make your username: ")
            pw = input("Make your password: ")
            
            if self.register(un, pw) != True:
                print("invalid username")
                return True
            

            return False
        
user_list = UserStore()
user_list.signUp()
user_list.signUp()

    