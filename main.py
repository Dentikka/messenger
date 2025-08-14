#!/usr/bin/env python3
"""
Secure Messenger - Main Entry Point
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from network.stun_client import get_public_address

def main():
    print("Getting public address...")
    public_addr = get_public_address()
    if public_addr:
        print(f"Public address: {public_addr[0]}:{public_addr[1]}")
    else:
        print("Could not determine public address")

    app = QApplication(sys.argv)
    app.setApplicationName("SecureMessenger")
    app.setApplicationVersion("1.0.0")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()