"""
Клиент для Secure Messenger
"""
import socket
import json
import threading
from config.settings import DEFAULT_HOST, DEFAULT_PORT

class MessageClient:
    def __init__(self, peer_id, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.peer_id = peer_id
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.message_callback = None
        
    def connect(self):
        """Подключение к серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Регистрация клиента
            register_msg = {
                'type': 'register',
                'peer_id': self.peer_id
            }
            self.socket.send(json.dumps(register_msg).encode())
            
            self.connected = True
            
            # Запуск потока для получения сообщений
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
            
    def disconnect(self):
        """Отключение от сервера"""
        self.connected = False
        if self.socket:
            self.socket.close()
            
    def send_message(self, to_peer_id: str, encrypted_ dict):
        """Отправка зашифрованного сообщения"""
        if not self.connected:
            return False
            
        message = {
            'type': 'message',
            'from': self.peer_id,
            'to': to_peer_id,
            'data': encrypted_data
        }
        
        try:
            self.socket.send(json.dumps(message).encode())
            return True
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
            
    def receive_messages(self):
        """Получение сообщений"""
        try:
            while self.connected:
                data = self.socket.recv(4096)
                if not 
                    break
                    
                try:
                    message = json.loads(data.decode())
                    if self.message_callback:
                        self.message_callback(message)
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            if self.connected:
                print(f"Error receiving messages: {e}")
        finally:
            self.connected = False
            
    def set_message_callback(self, callback):
        """Установка callback для входящих сообщений"""
        self.message_callback = callback