"""
Login dialog for Secure Messenger
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.peer_id = None
        self.server_host = None
        self.server_port = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Secure Messenger - Login")
        self.setFixedSize(400, 250)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Secure Messenger")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Peer ID
        peer_layout = QHBoxLayout()
        peer_layout.addWidget(QLabel("Your Peer ID:"))
        self.peer_id_input = QLineEdit()
        peer_layout.addWidget(self.peer_id_input)
        layout.addLayout(peer_layout)
        
        # Server settings
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("Server Host:"))
        self.host_input = QLineEdit("localhost")
        server_layout.addWidget(self.host_input)
        layout.addLayout(server_layout)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Server Port:"))
        self.port_input = QLineEdit("8888")
        self.port_input.setFixedWidth(100)
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Connect")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus
        self.peer_id_input.setFocus()
        
    def accept(self):
        peer_id = self.peer_id_input.text().strip()
        host = self.host_input.text().strip()
        port = self.port_input.text().strip()
        
        if not peer_id:
            QMessageBox.warning(self, "Warning", "Please enter your Peer ID")
            return
            
        if not host:
            QMessageBox.warning(self, "Warning", "Please enter server host")
            return
            
        try:
            port = int(port)
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter valid port number")
            return
            
        self.peer_id = peer_id
        self.server_host = host
        self.server_port = port
        super().accept()
        
    def get_connection_info(self):
        return self.peer_id, self.server_host, self.server_port