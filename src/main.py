from client_state import ClientState, load_or_new_client
import packet_parser
from PyQt6.QtWidgets import QApplication
import chat_app as chat_app
import sys
import io

app = QApplication(sys.argv)  # Initialize the application
window = chat_app.ChatApp()            # Create the main chat window

window.show()                 # Show the GUI
sys.exit(app.exec())          # Start the application event loop
