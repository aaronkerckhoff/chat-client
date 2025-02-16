from src.client_state import ClientState, load_or_new_client
from src import packet_parser
from src import chat_app
from PyQt6.QtWidgets import QApplication
import sys
import io

app = QApplication(sys.argv)  # Initialize the application
window = chat_app.ChatApp()            # Create the main chat window

window.show()                 # Show the GUI
sys.exit(app.exec())          # Start the application event loop
