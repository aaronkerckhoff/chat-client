from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QDialog, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QFileDialog, QScrollArea, QSizePolicy, QLayout, QLayoutItem
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QEvent, QObject, QTimer
from pathlib import Path
from web_client.client import Client

import packet_parser
import public_key
import packet_creator
import sys
import os
import json

import threading
import io
import time

from blocking import check_blocked, block, unblock
from client_state import ClientState, load_or_new_client, ChatState

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
        # May not this life, because ths aint working

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

class WorkerThread(threading.Thread):
    def __init__(self, client: ClientState):
        super().__init__()
        self.daemon = True  # Ensures thread stops when the main program exits
        self.running = True
        self.client = client

    def run(self):
        running_secs = 0
        while self.running:
            self.task()
            if running_secs % 50 == 0:
                self.client.broadcast_self()
            running_secs += 1
            time.sleep(1)  

    def stop(self):
        self.running = False

    def start_task(self):
        """Starts the task in a separate thread"""
        self.running = True
        if not self.is_alive():
            self.start()  # Start the thread if not already running

    def stop_task(self):
        """Stops the task execution"""
        self.running = False

    def task(self):
        """The hardcoded task the thread will execute"""
        #print("Running task")
        message = self.client.client_socket.receive_message()
        if not message:
            return
        message = io.BytesIO(message)
        if not message:
            print("Connection closed")
            return
        
        print(f"Message Recieved: {message}")

        packet_parser.parse_packet(message, self.client)

class EventFilter(QObject):
    def __init__(self, main):
        super().__init__()
        self.main = main

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and isinstance(obj, QLineEdit):
            if event.key() == Qt.Key.Key_Return:  # Enter key
                if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                    obj.setText(obj.text() + "\n")
                    
                    print("Shift enter pressed")
                else:
                    self.main.bottom_send_message()
                    
                    print("Enter pressed")
                return True  # Block the event from reaching the default handler
        return super().eventFilter(obj, event)

class ChatApp(QWidget):
    def __init__(self):
        """
        Innit of Main Chat Window
        """
        super().__init__()
        
        # -------------------- INIT --------------------

        if os.name == "nt":
            self.appdata_path = Path(os.getenv("APPDATA"))  # Convert to Path object
        else:
            self.appdata_path = Path(os.getenv("HOME")) # Assume linux
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

        # ---------- New Chat System Setup ----------
        # Dictionary to store messages per chat (key: chat partner, value: list of (sender, message))
        self.chats: dict[public_key.PublicKey, ] = {}      
        # Currently selected chat partner (for messages sent by you)
        self.current_chat = None
        
        # INIT HT EUPDATE QUEUE FOR CHATS
        # Create a timer that updates every 16ms (~60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)  # 16ms ≈ 60 FPS

        self.init_ui()
        #self.add_test_messages()  # Add some test messages to verify the functionality
        self.init_web_client() #  Set up the Web Client
        
    def update_frame(self):
        for sender, message in self.client_backend.message_queue:
            self.msg_recieved(sender, message)
        
        self.client_backend.message_queue.clear()

    def init_web_client(self):
        print("Starting Web Client Connection...")
        #self.web_client = Client("192.168.176.160", 12345, on_message_received=self.msg_recieved)
        # Init client_state here
        self.client_backend = load_or_new_client(self.username, self.msg_recieved)
        #init poller
        self.poller_thread = WorkerThread(self.client_backend)
        self.poller_thread.start_task()

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

    def on_top_right_button_click(self):
        if check_blocked(self.current_chat):
            print("UNBLOCKING")
            unblock(self.current_chat)
            self.top_right_button.setText("FREE✅")
        else:
            print("BLOCKING")
            block(self.current_chat)
            self.top_right_button.setText("BLOCKED🚫")

    def block_button_update(self):
          self.top_right_button.setText("BLOCKED🚫" if check_blocked(self.current_chat) else "FREE✅")

    def init_ui(self):
        """Initializes the GUI components."""
        # -------------------- Apply Styling ----------------
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

        # -------------------- BASIC WINDOW SETTINGS --------------------
        self.setWindowTitle("Chat")
        self.setFixedSize(800, 600)

        # -------------------- CREATE GUI ELEMENTS --------------------
        self.label = QLabel(f"Welcome, {self.username} 👋!", self)
        self.label.setFont(QFont("Any", 10))

        # -------------------- MAIN LAYOUT --------------------
        self.layout = QVBoxLayout()

        # Add the welcome label
        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # -------------------- CHAT INTERFACE --------------------
        chat_layout = QHBoxLayout()  # Layout for left (contacts) and middle (chat messages)

        # --- Left Bar: Contacts/Users ---
        self.user_list_layout = QVBoxLayout()

        # Create "Contacts" label and add it at the top
        self.user_list_label = QLabel("📂 Contacts")
        self.user_list_label.setFont(QFont("Any", 12, QFont.Weight.Bold))
        self.user_list_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.user_list_layout.addWidget(self.user_list_label)

        # Scroll area for contacts
        self.scroll_contacts = QScrollArea(self)
        self.scroll_contacts.setWidgetResizable(True)
        self.scroll_contacts.setFixedWidth(150)

        # Container for contacts inside the scroll area
        self.contacts_container = QWidget()
        self.contacts_layout = QVBoxLayout()
        self.contacts_layout.setSpacing(2)  # Minimal spacing
        self.contacts_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        # --- NEW CHAT BUTTON ---
        self.new_chat_button = QPushButton("➕", self)  # Added an icon for better visibility
        self.new_chat_button.clicked.connect(self.create_new_chat_popup)
        self.new_chat_button.setFixedSize(30, 30)
        self.new_chat_button.move(70, 475)
        self.new_chat_button.raise_()
        self.new_chat_button.show()

        # Add test users
        #self.test_users = ["Bob", "Alice", "Martin"] # Simulating many users -> REMOVE IN PROD
        self.test_users = []
        #for user in self.test_users:
        #    user_button = QPushButton(user)
        #    user_button.clicked.connect(lambda checked, u=user: self.on_user_selected(u))
        #    self.contacts_layout.addWidget(user_button)

        # Add a stretch at the bottom to keep spacing consistent
        self.contacts_layout.addStretch(1)

        self.contacts_container.setLayout(self.contacts_layout)
        self.scroll_contacts.setWidget(self.contacts_container)

        # Add the scrollable contacts list to the left sidebar
        self.user_list_layout.addWidget(self.scroll_contacts)
        chat_layout.addLayout(self.user_list_layout, 1)

        # --- Middle: Chat Messages ---
        self.message_area_layout = QVBoxLayout()
        self.message_area_label = QLabel("Chat Messages")
        self.message_area_label.setFont(QFont("Any", 12))
        self.message_area_layout.addWidget(self.message_area_label)

        # Wrap messages in a scrollable area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Container for messages inside the scroll area
        self.message_container = QWidget()
        self.message_container_layout = QVBoxLayout()
        self.message_container_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        # Ensure messages are always pushed up when the list is empty
        self.message_container_layout.addStretch(1)

        self.message_container.setLayout(self.message_container_layout)
        self.scroll_area.setWidget(self.message_container)

        # Allow chat messages to expand as much as possible
        self.message_area_layout.addWidget(self.scroll_area, stretch=1)
        chat_layout.addLayout(self.message_area_layout, 3)  # Chat area gets more space

        self.layout.addLayout(chat_layout, stretch=5)

        #----------------------BLOCKIN BUTTON ---------------------

        # Create a top bar layout for the button
        self.top_bar_layout = QHBoxLayout()

        # Create the button
        self.top_right_button = QPushButton("BLOCKED🚫" if check_blocked(self.current_chat) else "FREE✅", self)  # Settings or any function
        self.top_right_button.setFixedSize(100, 30)  # Set size
        self.top_right_button.clicked.connect(self.on_top_right_button_click)  # Connect to function

        # Align the button to the right
        self.top_bar_layout.addStretch(1)  # Push button to the right
        self.top_bar_layout.addWidget(self.top_right_button)  # Add button to layout

        # Add the top bar layout to the main layout
        self.layout.insertLayout(2, self.top_bar_layout)  # Insert at the top


        # -------------------- BOTTOM INPUT BAR --------------------
        self.bottom_input_layout = QHBoxLayout()
        self.bottom_message_input = QLineEdit()
        self.bottom_send_button = QPushButton("Send")
        self.bottom_upload_button = QPushButton("Upload File")

        self.bottom_input_layout.addWidget(self.bottom_message_input, stretch=3)
        self.bottom_input_layout.addWidget(self.bottom_send_button, stretch=1)
        self.bottom_input_layout.addWidget(self.bottom_upload_button, stretch=1)

        # Connect signals to the new bottom bar
        self.bottom_send_button.clicked.connect(self.bottom_send_message)
        self.bottom_upload_button.clicked.connect(self.upload_file)

        # Detect Enter / Shift+Enter for newline characters separately
        self.eventFilter = EventFilter(self)
        self.bottom_message_input.installEventFilter(self.eventFilter)

        # Ensure the input bar stays at the bottom
        self.layout.addStretch(1)  # Pushes input field down
        self.layout.addLayout(self.bottom_input_layout)

        # Set the final layout
        self.setLayout(self.layout)

        # Set default current chat to the first contact (if any)
        #Init OpenKeyChatTuple
        if self.test_users:
            self.display_chat(self.test_users[0])
            self.current_chat = self.test_users[0]

    def msg_recieved(self, message, sender):
        """
        Called when a new message is received.
        Creates a new label in the chat message area.
        Also checks if the sender is already in the contacts sidebar;
        if not, you could add it.
        """
        print(message)
        #sernder = ...
        #return
        # Modify this to adapt to the new system of JSON Format 
        # For simplicity, the message will be displayed as "Sender: Message"
        sender_name = self.client_backend.discovered_clients[sender]

        # (Optional) If sender is not in your contacts, you could add a new button/label.
        if sender not in self.test_users and sender_name != self.username:
            print(f"New sender detected: {sender_name} (not in contacts)")
            self.add_new_chat(sender_name, None)

        self.add_message_to_chat(sender, message, sender_name)
        #self.display_chat(sender)

    def on_user_selected(self, user: public_key.PublicKey):
        """
        Called when a user in the contacts list is clicked.
        Updates the current chat and displays its messages.
        """
        print(f"Selected chat with: {user}")
        self.current_chat = user
        self.display_chat(user)
    
    
    def bottom_send_message(self):
        """
        Called when the bottom send button is clicked.
        Adds the message to the active chat using the new bottom input bar.
        """
        # Add Send via tcp here
        if not self.current_chat:
            print("No chat selected!")
            return
        text = self.bottom_message_input.text().strip()
        if text:
            self.add_message_to_chat(self.current_chat, text, self.username)
            self.bottom_message_input.clear()
        else:
            print("Text was empty. Escaping...")
            return
        
        # Send message via web_client
        # IMPORTANT ------ Implement Encryption before sending
        if not self.current_chat in self.client_backend.chats:
            self.client_backend.send_shared_secret(self.current_chat)
        try:
            self.client_backend.send_message(self.current_chat, text) # Need \n escape in order to be able to send message
            print("Message sent to web client")
        except Exception as e:
            print(f"CRITICAL: The message wasnt able to be sent: {e}")

        
    
    def upload_file(self):
        """
        Called when the upload button is clicked.
        Currently left empty for later implementation.
        """
        file_bytes = self.open_file_dialog()

        # Send message with different Type
        # Implement Encryption before sending
        self.web_client.send(file_bytes)
        pass
    
    # -------------------- New Chat Message System --------------------
    def add_message_to_chat(self, chat_user, message, sender):
        """
        Stores a message for a given chat and displays it if that chat is active.
        """
        if chat_user not in self.chats:
            self.chats[chat_user] = []
        self.chats[chat_user].append((sender, message))
        if self.current_chat == None or self.current_chat == chat_user:
            self.add_message_label(sender, message)
    
    def add_message_label(self, sender, message):
        """
        Adds a new message label to the chat display.
        """
        label = QLabel(f"{sender}: {message}")
        self.message_container_layout.addWidget(label)
    
    def display_chat(self, chat_user: public_key.PublicKey):
        """
        Clears and displays all messages for the specified chat.
        """
        # Clear existing messages in the display area
        while self.message_container_layout.count():
            child = self.message_container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        # Display stored messages for the selected chat
        for sender, message in self.chats.get(chat_user, []):
            self.add_message_label(sender, message)
        username = self.client_backend.discovered_clients[chat_user]
        self.message_area_label.setText(f"Chat Messages - {username}")

    
    def receive_message(self, message, sender):
        """
        New method to receive a message using the new system.
        If the sender is not the current user, the chat partner is the sender.
        If the message is from the current user, it's added to the active chat.
        """
        # Replace in new System where sender is specified
        chat_user = sender if sender != self.username else self.current_chat
        if chat_user is None:
            chat_user = sender
        self.add_message_to_chat(chat_user, message, sender)
        # Also add to contacts if not already present
        if sender != self.username and sender not in self.test_users:
            print(f"New sender detected: {sender} (added to contacts)")
            new_contact = QPushButton(sender)
            new_contact.clicked.connect(lambda checked, u=sender: self.on_user_selected(u))
            self.user_list_layout.addWidget(new_contact)
            self.test_users.append(sender)
    
    def add_test_messages(self):
        """
        Adds some test messages to the chat area using the new system.
        """
        self.receive_message("Hello, how are you?", "Alice")
        self.receive_message("I'm good, thanks!", self.username)
        self.receive_message("Are you coming to the party?", "Bob")
    
    # -------------------- New Chat Creation Methods --------------------
    def create_new_chat_popup(self):
        """
        Creates a new chat via a popup dialog styled similar to the sign-up popup.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("New Chat")
        dialog.resize(300, 150)
        
        label = QLabel("Enter contact's name:")
        input_field = QLineEdit()
        submit_button = QPushButton("Create Chat")
        
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(input_field)
        layout.addWidget(submit_button)
        dialog.setLayout(layout)
        
        submit_button.clicked.connect(lambda: self.add_new_chat(input_field.text(), dialog))
        dialog.exec()
    
    def add_new_chat(self, contact_name, dialog):
        """
        Adds a new chat contact if a valid name is provided.
        The new chat button is inserted before the New Chat button so that it always remains last.
        """
        found_users = []
        for key in self.client_backend.discovered_clients.keys():
            key_name = self.client_backend.discovered_clients[key]
            if key_name == contact_name:
                found_users.append(key)

        
                
        # Request Open Key From Buffer
        if len(found_users) == 0:
            print("No users found")
            return
        if len(found_users) > 1:
            print("There were multipe users with that name, Todo: let client select.")
            return
        
        contact_key = found_users[0]
        if contact_key in self.test_users:
            print("Chat with that contact already exists")
            return
        
        self.test_users.append(contact_key)

        # Remove stretch temporarily
        new_user_button = QPushButton(contact_name)
        new_user_button.clicked.connect(lambda checked, u=contact_key: self.on_user_selected(u))

        # ✅ Remove the existing stretch before adding a new contact
        if self.contacts_layout.count() > 0:
            item = self.contacts_layout.itemAt(self.contacts_layout.count() - 1)
            if item and isinstance(item, QLayoutItem):  # Check if it's the stretch
                self.contacts_layout.removeItem(item)

        # ✅ Add new contact button at the bottom (normal behavior)
        self.contacts_layout.addWidget(new_user_button)

        # ✅ Re-add the stretch at the end to keep contacts aligned properly
        self.contacts_layout.addStretch(1)
        if dialog:
            dialog.accept()

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")

        if file_path:  # If a file was selected
            with open(file_path, "rb") as file:
                file_bytes = file.read()  # Read file as bytes
                print(f"Sending File Bytes...")  # Print first 50 bytes as a check
        
        # Return File Bytes
        return file_bytes.decode('utf-8')



# Main Statement -> Creates the main window
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Initialize the application
    window = ChatApp()            # Create the main chat window

    window.show()                 # Show the GUI
    sys.exit(app.exec())          # Start the application event loop