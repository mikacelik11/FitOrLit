import unittest
from FitOrLit.onboard import User
from unittest.mock import Mock, patch

class testClass:
    def test_login_bool(self):
        
        User.input = lambda: 'mika', '123'
        output = User.signUp()
        assert output == 'expected_output'
        
        
    
