"""
Setup script for building Windows executable
"""
from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need fine tuning.
build_options = {
    'packages': ['cryptography', 'sqlalchemy', 'PyQt5'],
    'excludes': [],
    'include_files': ['resources/'],
    'optimize': 1
}

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('main.py', base=base, target_name='SecureMessenger.exe')
]

setup(
    name='SecureMessenger',
    version='1.0',
    description='Secure Messenger with end-to-end encryption',
    options={'build_exe': build_options},
    executables=executables
)