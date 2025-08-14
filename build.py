"""
Build script for Secure Messenger using PyInstaller
"""
import PyInstaller.__main__
import sys
import os

# Путь к вашему проекту
project_path = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'main.py',
    '--name=SecureMessenger',
    '--windowed',  # Без консоли
    '--onefile',   # Один файл
    '--icon=resources/icons/app_icon.ico',
    '--add-data=resources;resources',
    '--hidden-import=PyQt5.sip',
    '--hidden-import=cryptography',
    '--hidden-import=sqlalchemy',
    '--clean',
    '--noconfirm'
])