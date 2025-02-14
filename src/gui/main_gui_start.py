from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QDialog, QLabel, QVBoxLayout, QLineEdit
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from PyQt6.QtCore import Qt
from pathlib import Path

import sys
import os
import json


#-------------------- CLASSES --------------------
#Define Login Popup here
class LoginPopup(QDialog):
    def __init__(self, save_file_path):
        """
        Init for Login Popup
        """
        super().__init__()
        self.setWindowTitle("Sign up as new User")
        self.resize(300, 150)

        # Create Widgets
        self.label = QLabel("Enter your username:")
        self.input_field = QLineEdit()
        self.submit_button = QPushButton("Submit")

        # Layout Setup
        layout = QVBoxLayout()
        layout.addWidget(self.label)         # Add label
        layout.addWidget(self.input_field)   # Add input field
        layout.addWidget(self.submit_button) # Add button
        self.setLayout(layout)

        # Button Click Event
        self.submit_button.clicked.connect(self.get_input)

        # Make file_path persist
        self.file_path = save_file_path

        # Try Loading Roboto Font


        # Create Styles 
        self.setStyleSheet("""
            QWidget { 
                background-color: #2E3440;  /* Dark Gray Background */
                color: #D8DEE9;  /* White Text */
            }
            QLineEdit {
                background-color: #4C566A;  /* Input Field Background */
                color: #ECEFF4;  /* Input Text Color */
                border: 1px solid #88C0D0;  /* Border Color */
                padding: 5px;
                           font-family: 'Roboto';
            }
            QPushButton {
                background-color: #5E81AC;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QLabel{
                font-size: 20px;
            }
        """)

    def get_input(self):
        """
        When the Input Field is submitted
        """
        username = self.input_field.text()

        if(username == ""):
            print("User didn't specify a name")
            sys.exit()

        print("Entered Username: ", username)
        print("Saving UserName to File: " + self.file_path.__str__())
        
        # Create and write to the file
        with self.file_path.open("w", encoding="utf-8") as file:
            file.write(f"{{\"username\":\"{username}\"}}")  #--------------- IMPORTANT --------------- Create Keys and format json

        print(f"File created at: {self.file_path}")
        
        self.accept()  # Close the dialog on Name Enter

class ChatApp(QWidget):
    def __init__(self):
        """
        Innit of Main Chat Window
        """
        super().__init__()
        
        # -------------------- INIT --------------------
        self.appdata_path = Path(os.getenv("APPDATA"))  # Convert to Path object
        print("AppData path: " + str(self.appdata_path))  # Print Save Dir
        
        self.file_path = self.appdata_path / "Chat" / "user.txt"  # Correct path creation
        
        # If we dont have a User already set up we need to show the login popup before showing the main window
        if not self.file_path.exists():
            print("File not found. Setting up new User at: " + str(self.file_path))
            self.file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the "Chat" folder exists
            
            # INIT USER HERE WITH POPUP
            newuserpopup = LoginPopup(self.file_path) # Create login popup here
            newuserpopup.exec()
        
        self.load_username()
        self.init_ui()
        
    def load_username(self):
        """Loads the username from the user.txt JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)  # Parse JSON
            self.username = data.get("username", "Username Key not Found!")
        except (json.JSONDecodeError, FileNotFoundError):
            self.username = "Username Key not Found!"
            sys.exit()
        
        print("Found Username: " + self.username)
    
    def init_ui(self):
        """Initializes the GUI components."""
        # -------------------- BASIC WINDOW SETTINGS --------------------
        self.setWindowTitle("Chat")
        self.resize(800, 600)

        # -------------------- CREATE GUI ELEMENTS --------------------
        self.label = QLabel(f"Welcome, {self.username}!", self)
        self.label.setFont(QFont("Any", 10))
        
        # Create Styles
        self.setStyleSheet("""
            QWidget { 
                background-color: #2E3440;  /* Dark Gray Background */
                color: #D8DEE9;  /* White Text */
            }
            QLineEdit {
                background-color: #4C566A;  /* Input Field Background */
                color: #ECEFF4;  /* Input Text Color */
                border: 1px solid #88C0D0;  /* Border Color */
                padding: 5px;
                font-family: 'Roboto';
            }
            QPushButton {
                background-color: #5E81AC;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
        """)
        
        # -------------------- LAYOUT --------------------
        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()  # Pushes everything up, prevents vertical centering
        self.setLayout(layout)

# Main Statement -> Creates the main window
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Initialize the application
    window = ChatApp()            # Create the main chat window

    window.show()                 # Show the GUI
    sys.exit(app.exec())           # Start the application event loop