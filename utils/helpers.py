"""
Вспомогательные функции
"""
import os
import json
from datetime import datetime

def format_timestamp(timestamp_str):
    """Форматирование временной метки"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str

def safe_json_loads(data):
    """Безопасная загрузка JSON"""
    try:
        return json.loads(data)
    except:
        return None

def ensure_directory(path):
    """Создание директории если она не существует"""
    os.makedirs(path, exist_ok=True)