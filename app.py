import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFormLayout, # arranges everything vertically
    QLabel,
    QLineEdit, # creates username and password fields
    QMainWindow,
    QPushButton, # creates the login button
    QStackedWidget,# Will eventually let you switch between login, signup, dsahboard and other pages
    QVBoxLayout, 
    QWidget,
)

from onboard import UserStore

class LoginPage(QWidget):
    def __init__(self, user_store, login_succeeded, signup_requested):
        super().__init__()

        # initialize the variables
        self.user_store = user_store
        self.login_succeeded = login_succeeded
        self.signup_requested = signup_requested
        
        
        # title page aligns the text at the top in a bar manner like it does for any site opened on Mac OS
        title = QLabel("FitOrLit Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Lets users type in an input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: red;")

        # creates button 
        login_button = QPushButton("Log in")
        signUp_button = QPushButton("Create Account")

        # Formates the inputs 
        form_layout = QFormLayout()
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        # page layout
        page_layout = QVBoxLayout(self)
        page_layout.addStretch()
        page_layout.addWidget(title)
        page_layout.addLayout(form_layout)
        page_layout.addWidget(login_button)
        page_layout.addWidget(signUp_button)
        page_layout.addWidget(self.message_label)
        page_layout.addStretch()

        # connects the buttons with the needed functions
        login_button.clicked.connect(self.attempt_login)
        signUp_button.clicked.connect(self.signup_requested)
        self.password_input.returnPressed.connect(self.attempt_login)
    
    # function for user to attempt login and messages the user if wrong usernamme or password is done 
    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if username == "" or password == "":
            self.message_label.setText("Please enter a username and password.")
            return

        if self.user_store.login(username, password):
            self.message_label.clear()
            self.password_input.clear()
            self.login_succeeded()
        else:
            self.message_label.setText("Incorrect username or password.")
            
class HomePage(QWidget):
    def __init__(self, user_store, logout_success):
        super().__init__()
        self.user_store = user_store
        self.logout_success = logout_success
        
        #Title Page
        title = QLabel("FitOrLit")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        #buttons
        logout_button = QPushButton("Logout")
        
        #page layout
        page_layout = QVBoxLayout(self)
        page_layout.addStretch()
        page_layout.addWidget(title)
        page_layout.addWidget(logout_button)
        page_layout.addStretch()
        
        #Connects
        logout_button.clicked.connect(self.logout_user)
        
    def logout_user(self):
        self.user_store.logout()
        self.logout_success()
        
##class UserInfo(QWidget):
    ##def __init__(self, user_store):
        ##super().__init__()
        ##self.user_store = user_store
    
        
            
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FitOrLit")
        self.resize(500, 400)

        self.user_store = UserStore()

        # Temporary account for testing the login page
        self.user_store.register("mika", "123")

        self.pages = QStackedWidget()

        # creates the login page  with the shared user store and callbacks
        # for navigating to the dashboard or signup page.
        self.login_page = LoginPage(
            self.user_store,
            self.show_homepage,
            self.show_signup,
        )
        
        self.signup_page = SignUpWindow(
            self.user_store,
            self.show_login,
        )
        
        self.home_page = HomePage (
            self.user_store,
            self.show_login
        )

        self.dashboard_label = QLabel()
        self.dashboard_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # every new page must be added here so everytime a new place of the app is created it must be refrenced here (this might be in a stack)
        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.signup_page)
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.dashboard_label)

        self.setCentralWidget(self.pages)

    def show_dashboard(self):
        current_user = self.user_store.current_user
        self.dashboard_label.setText(
            f"Welcome, {current_user.username}!"
        )
        self.pages.setCurrentWidget(self.dashboard_label)
    # these functions are needed so when we call them they can make the current page the specific thing we need.   
    def show_signup(self):
        self.pages.setCurrentWidget(self.signup_page)
        
    def show_login(self):
        self.pages.setCurrentWidget(self.login_page)
        
    def show_homepage(self):
        self.pages.setCurrentWidget(self.home_page)
        
class SignUpWindow(QWidget):
    def __init__(self, user_store, create_succeeded):
        
        super().__init__()
        
        #initalize
        self.create_succeeded = create_succeeded
        self.user_store = user_store
        
        
        title = QLabel("FitOrLit SignUp")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # user inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Create Username:")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.c_password_input = QLineEdit()
        self.c_password_input.setPlaceholderText("Confirm your password")
        self.c_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: red;")
        
        # button creation   
        create_button = QPushButton("Create Account")
        
        # formatting
        form_layout = QFormLayout()
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Confirm Password:", self.c_password_input)
        
        page_layout = QVBoxLayout(self)
        page_layout.addStretch()
        page_layout.addWidget(title)
        page_layout.addLayout(form_layout)
        page_layout.addWidget(create_button)
        page_layout.addWidget(self.message_label)
        page_layout.addStretch()
        
         
        # button connecting
        create_button.clicked.connect(self.attempt_create)
        self.password_input.returnPressed.connect(self.attempt_create)
     
    # The fuction that creates a user, the user must follow the rules of password with a len of 6 >=  and must have a special character contain in it.  
    def attempt_create(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_p = self.c_password_input.text()
        
        if username == "" or password == "":
            self.message_label.setText("Please enter a username and password.")
            return
        
        if password != confirm_p:
            self.message_label.setText("Passwords do not match")
            return 
            
        if self.user_store.password_error(password):
            message = self.user_store.password_error(password)
            self.message_label.setText(message)
                        
        
        elif self.user_store.register(username, password):
            self.message_label.clear()
            self.password_input.clear()
            self.create_succeeded()
        else:
            self.message_label.setText("The User already exists")
            
            

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())