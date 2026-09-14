
from onboard import UserStore

# This test is to check if register function works and a new user is registered
def test_new_username_is_accepted(): 
    store = UserStore()
    assert store.register('mika', '123') is True

# Now if there are duplicate username the person should be reprompted to make a different password
# and should not be registered unless it is a unique username.  
def test_duplicate_username_is_rejected():
    store = UserStore()
    store.register('mika', '123') 
    assert store.register('mika', '123') is False
    
def test_find_user():
    store = UserStore()
    store.register('luka', '123')
    assert store.find_user('luka', '123') is True
    
    
def test_login():
    store = UserStore()
    store.register('joe', '123')
    assert store.login('joe', '123') is True
    
def test_login_duplicate():
    store = UserStore()
    store.register('max', '123')
    assert store.login('joe', '123') is False
    
def test_logout():
    store = UserStore()
    checker = store.login('joe', '123')
    assert store.logout(checker) is False
        
    
