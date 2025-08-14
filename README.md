# Secure Messenger

Безопасный мессенджер с end-to-end шифрованием для Windows.

## Особенности

- End-to-end шифрование (RSA + AES)
- Локальное хранение сообщений в SQLite
- CLI интерфейс
- Безопасная передача через TCP сервер

## Установка

1. Установите Python 3.8+
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Использование

### Запуск сервера
```bash
python -m network.server
```

### Запуск клиента
```bash
python main.py --peer-id your_id send recipient_id "Hello!"
python main.py --peer-id your_id history recipient_id
python main.py --peer-id your_id peers
```

### Добавление пира
```bash
python main.py --peer-id your_id add_peer peer_id path/to/public_key.pem
```

## Структура проекта

- `cli/` - командный интерфейс
- `crypto/` - шифрование
- `network/` - сетевые функции
- `storage/` - работа с БД
- `models/` - модели данных
- `config/` - конфигурация
- `utils/` - вспомогательные функции

## Безопасность

- RSA 2048 для обмена ключами
- AES-256 для шифрования сообщений
- Все ключи хранятся локально
- Приватные ключи не передаются по сети
```

## 🚀 Как запустить

1. **Установка зависимостей:**
```bash
pip install -r requirements.txt
```

2. **Запуск сервера (на одном из устройств):**
```bash
python -m network.server
```

3. **Запуск клиентов на обоих устройствах:**

Устройство 1:
```bash
python main.py --peer-id user1
```

Устройство 2:
```bash
python main.py --peer-id user2
```

4. **Обмен публичными ключами:**

Скопируйте публичные ключи из `data/keys/` и добавьте пиров:
```bash
python main.py --peer-id user1 add_peer user2 data/keys/public_key.pem
python main.py --peer-id user2 add_peer user1 data/keys/public_key.pem
```

5. **Отправка сообщений:**
```bash
python main.py --peer-id user1 send user2 "Привет от user1!"
python main.py --peer-id user2 send user1 "Привет от user2!"
```

6. **Просмотр истории:**
```bash
python main.py --peer-id user1 history user2
```

## 📦 Сборка .exe

```bash
pip install pyinstaller
pyinstaller --onefile main.py
```
