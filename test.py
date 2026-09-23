
from onboard import UserStore

from calc import *

# onboard.py

def test_new_store_starts_logged_out():
    store = UserStore()
    
    assert store.current_user is None
    assert store.is_logged_in() is False
    


# This test is to check if register function works and a new user is registered
def test_new_username_is_accepted(): 
    store = UserStore()
    assert store.register('mika', '123') is True
    assert len(store.users) == 1
    assert store.users[0].username == 'mika'

# Now if there are duplicate username the person should be reprompted to make a different password
# and should not be registered unless it is a unique username.  
def test_duplicate_username_is_rejected():
    store = UserStore()
    store.register('mika', '123') 
    result = store.register('mika', '123')
    
    assert result is False
    assert len(store.users) == 1
    
## make sure that partial username is treated as a duplicate 
# this was an issue with my previous code 
def test_partial_username_is_not_treated_as_duplicate():
    store = UserStore()
    store.register("samantha", "123")

    result = store.register("sam", "456")

    assert result is True
    assert len(store.users) == 2

    
def test_find_user():
    store = UserStore()
    store.register('luka', '123')
    user = store.find_user('luka', '123')
    
    assert user is not None
    assert user.username == 'luka'
    

# Make sure if username is right but the password is differen tthen we can't find the user
def test_find_user_returns_none_for_wrong_password():
    store = UserStore()
    store.register("luka", "123")

    user = store.find_user("luka", "wrong-password")

    assert user is None
    
# make sure login is successful  and our current user is the one we logged in with
def test_login():
    store = UserStore()
    store.register('joe', '123')
    expected_user = store.find_user('joe', '123')
    
    result = store.login('joe', '123')
    
    assert result is True
    assert store.current_user is expected_user
    assert store.is_logged_in() is True
    
# test checks the login in with different password doesn't work
def test_failed_login_does_not_set_current_user():
    store = UserStore()
    store.register("joe", "123")

    result = store.login("joe", "456")

    assert result is False
    assert store.current_user is None
    assert store.is_logged_in() is False


# test log out and makes sure that if logout is called then current user is set to None.
def test_logout_clears_current_user():
    store = UserStore()
    store.register("joe", "123")
    store.login("joe", "123")

    store.logout()

    assert store.current_user is None
    assert store.is_logged_in() is False
    
# Calc.py
        
def test_bmi():
    assert bmi_calc(5, 5) == 1.0
    
def test_cut():
    assert cut_cal(160) == 1900
    
def test_bulk():
    assert bulk_cal(160) == 2900

