"""
Chat window for Secure Messenger
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QListWidget, QLabel, 
                            QSplitter, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor

class ChatWindow(QWidget):
    def __init__(self, messenger_app, parent=None):
        super().__init__(parent)
        self.messenger_app = messenger_app
        self.current_peer = None
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        self.setWindowTitle(f"Secure Messenger - {self.messenger_app.peer_id}")
        self.resize(1000, 700)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel - Peers list
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Contacts:"))
        
        self.peers_list = QListWidget()
        self.peers_list.itemClicked.connect(self.on_peer_selected)
        left_panel.addWidget(self.peers_list)
        
        # Add peer button
        self.add_peer_button = QPushButton("Add Peer")
        self.add_peer_button.clicked.connect(self.add_peer)
        left_panel.addWidget(self.add_peer_button)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_peers)
        left_panel.addWidget(self.refresh_button)
        
        # Right panel - Chat area
        right_panel = QVBoxLayout()
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)
        right_panel.addWidget(self.chat_display)
        
        # Message input
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        right_panel.addLayout(input_layout)
        
        # History button
        self.history_button = QPushButton("Show History")
        self.history_button.clicked.connect(self.show_history)
        right_panel.addWidget(self.history_button)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([200, 800])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Setup auto-refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_peers)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def setup_connections(self):
        """Setup connections with messenger app"""
        pass
        
    def refresh_peers(self):
        """Refresh peers list"""
        self.peers_list.clear()
        peers = self.messenger_app.db_manager.get_all_peers()
        for peer in peers:
            self.peers_list.addItem(peer.peer_id)
            
    def on_peer_selected(self, item):
        """Handle peer selection"""
        self.current_peer = item.text()
        self.chat_display.clear()
        self.chat_display.append(f"Selected peer: {self.current_peer}")
        self.message_input.setFocus()
        
    def add_peer(self):
        """Add new peer"""
        peer_id, ok = self.get_text_input("Add Peer", "Enter peer ID:")
        if not ok or not peer_id:
            return
            
        public_key_path, ok = self.get_text_input("Add Peer", "Enter path to public key file:")
        if not ok or not public_key_path:
            return
            
        try:
            with open(public_key_path, 'r') as f:
                public_key = f.read()
            self.messenger_app.add_peer(peer_id, public_key)
            self.refresh_peers()
            QMessageBox.information(self, "Success", f"Peer {peer_id} added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add peer: {str(e)}")
            
    def get_text_input(self, title, label):
        """Get text input from user"""
        from PyQt5.QtWidgets import QInputDialog
        return QInputDialog.getText(self, title, label)
        
    def send_message(self):
        """Send message to current peer"""
        if not self.current_peer:
            QMessageBox.warning(self, "Warning", "Please select a peer first")
            return
            
        message = self.message_input.text().strip()
        if not message:
            return
            
        try:
            if self.messenger_app.send_message(self.current_peer, message):
                self.append_message(f"You: {message}", "sent")
                self.message_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to send message")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send message: {str(e)}")
            
    def append_message(self, message, direction):
        """Append message to chat display"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(f"\n{message}")
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()
        
    def incoming_message(self, sender_id, message):
        """Handle incoming message"""
        self.append_message(f"{sender_id}: {message}", "received")
        
    def show_history(self):
        """Show message history with current peer"""
        if not self.current_peer:
            QMessageBox.warning(self, "Warning", "Please select a peer first")
            return
            
        try:
            messages = self.messenger_app.db_manager.get_message_history(self.current_peer)
            if not messages:
                QMessageBox.information(self, "History", "No messages found")
                return
                
            history_text = "Message History:\n" + "="*50 + "\n"
            for msg in reversed(messages):
                direction = "You" if msg.direction == 'sent' else msg.peer_id
                timestamp = msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                history_text += f"[{timestamp}] {direction}: {msg.content}\n"
                
            # Show in message area
            self.chat_display.clear()
            self.chat_display.append(history_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load history: {str(e)}")