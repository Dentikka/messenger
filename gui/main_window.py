"""
Main window for Secure Messenger GUI
"""
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from gui.chat_window import ChatWindow
from gui.login_dialog import LoginDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.messenger_app = None
        self.chat_window = None
        self.init_ui()
        self.show_login()
        
    def init_ui(self):
        self.setWindowTitle("Secure Messenger")
        self.resize(1000, 700)
        
    def show_login(self):
        """Show login dialog"""
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            peer_id, host, port = dialog.get_connection_info()
            self.start_messenger(peer_id, host, port)
        else:
            self.close()
            
    def start_messenger(self, peer_id, host, port):
        """Start messenger application"""
        try:
            from cli.interface import MessengerApp
            self.messenger_app = MessengerApp(peer_id, host, port)
            
            # Setup message callback
            self.messenger_app.client.set_message_callback(self.handle_incoming_message)
            
            # Show chat window
            self.chat_window = ChatWindow(self.messenger_app)
            self.setCentralWidget(self.chat_window)
            self.chat_window.refresh_peers()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start messenger: {str(e)}")
            self.show_login()
            
    def handle_incoming_message(self, message_data):
        """Handle incoming message"""
        if self.chat_window and message_data.get('type') == 'message':
            sender_id = message_data.get('from')
            encrypted_data = message_data.get('data')
            
            try:
                decrypted_message = self.messenger_app.crypto_manager.decrypt_message(encrypted_data)
                self.messenger_app.db_manager.save_message(sender_id, decrypted_message, 'received')
                
                # Update GUI
                if hasattr(self.chat_window, 'incoming_message'):
                    self.chat_window.incoming_message(sender_id, decrypted_message)
                    
            except Exception as e:
                print(f"Error decrypting message: {e}")
                
    def closeEvent(self, event):
        """Handle window close"""
        if self.messenger_app:
            self.messenger_app.client.disconnect()
        event.accept()