import os
from pathlib import Path

# Базовые настройки
APP_NAME = "SecureMessenger"
APP_VERSION = "1.0.0"

# Пути
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "messages.db"
KEYS_DIR = DATA_DIR / "keys"

# Создаем директории если их нет
DATA_DIR.mkdir(exist_ok=True)
KEYS_DIR.mkdir(exist_ok=True)

# Настройки сети
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8888

# Настройки шифрования
KEY_SIZE = 2048  # для RSA
SYMMETRIC_KEY_SIZE = 32  # 256 bits

# GUI настройки
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
REFRESH_INTERVAL = 30000  # 30 секунд