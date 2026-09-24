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
    def __init__(self, user_store, login_succeeded):
        super().__init__()

        self.user_store = user_store
        self.login_succeeded = login_succeeded

        title = QLabel("FitOrLit Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: red;")

        login_button = QPushButton("Log in")
        signUp_button = QPushButton("Create Account")

        form_layout = QFormLayout()
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        page_layout = QVBoxLayout(self)
        page_layout.addStretch()
        page_layout.addWidget(title)
        page_layout.addLayout(form_layout)
        page_layout.addWidget(login_button)
        page_layout.addWidget(signUp_button)
        page_layout.addWidget(self.message_label)
        page_layout.addStretch()

        login_button.clicked.connect(self.attempt_login)
        signUp_button.clicked.connect(SignUpWindow)
        self.password_input.returnPressed.connect(self.attempt_login)
        
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
            
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FitOrLit")
        self.resize(500, 400)

        self.user_store = UserStore()

        # Temporary account for testing the login page
        self.user_store.register("mika", "123")

        self.pages = QStackedWidget()

        self.login_page = LoginPage(
            self.user_store,
            self.show_dashboard,
        )

        self.dashboard_label = QLabel()
        self.dashboard_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.dashboard_label)

        self.setCentralWidget(self.pages)

    def show_dashboard(self):
        current_user = self.user_store.current_user
        self.dashboard_label.setText(
            f"Welcome, {current_user.username}!"
        )
        self.pages.setCurrentWidget(self.dashboard_label)
        
class SignUpWindow(QWidget):
    def __init__(self, username, password, confirmpass):
        title = QLabel("FitOrLit Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Create Username:")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        
            
        create_button = QPushButton("Create Account")
        
        form_layout = QFormLayout()
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        
        page_layout = QVBoxLayout(self)
        page_layout.addStretch()
        page_layout.addWidget(title)
        page_layout.addLayout(form_layout)
        page_layout.addWidget(create_button)
        page_layout.addStretch()
        
        create_button.clicked.connect(self.attempt_create)
        self.password_input.returnPressed.connect(self.attempt_create)
     
    # TODO     
    def attempt_create(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
            
            

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())