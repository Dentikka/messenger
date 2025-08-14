"""
Основной клиент для Secure Messenger с поддержкой P2P
"""
import socket
import json
import threading
from typing import Callable, Optional
from config.settings import DEFAULT_HOST, DEFAULT_PORT

class MessageClient:
    def __init__(self, peer_id: str, host=DEFAULT_HOST, port=DEFAULT_PORT, 
                 use_p2p: bool = True):
        self.peer_id = peer_id
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.message_callback = None
        self.use_p2p = use_p2p
        self.p2p_client = None
        
    def connect(self, crypto_manager=None):
        """
        Подключение к серверу и инициализация P2P
        """
        # Подключение к центральному серверу
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
            
            print("Connected to relay server")
            
        except Exception as e:
            print(f"Connection to relay server failed: {e}")
            return False
            
        # Инициализация P2P если включено
        if self.use_p2p and crypto_manager:
            try:
                from network.p2p_client import P2PClient
                self.p2p_client = P2PClient(self.peer_id, crypto_manager)
                self.p2p_client.start()
                self.p2p_client.set_message_callback(self._handle_p2p_message)
                print("P2P client initialized")
            except Exception as e:
                print(f"P2P initialization failed: {e}")
                
        return True
        
    def disconnect(self):
        """
        Отключение от сервера и P2P
        """
        self.connected = False
        
        if self.socket:
            self.socket.close()
            
        if self.p2p_client:
            self.p2p_client.stop()
            
    def send_message(self, to_peer_id: str, encrypted_data: dict, 
                    try_p2p: bool = True) -> bool:
        """
        Отправка сообщения (сначала P2P, потом через сервер)
        """
        # Пытаемся отправить через P2P если доступно
        if try_p2p and self.p2p_client:
            try:
                if self.p2p_client.send_p2p_message(to_peer_id, encrypted_data):
                    return True
            except Exception as e:
                print(f"P2P send failed: {e}")
                
        # Если P2P не сработал, отправляем через сервер
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
            print(f"Failed to send message through relay: {e}")
            return False
            
    def receive_messages(self):
        """
        Получение сообщений через сервер
        """
        try:
            while self.connected:
                data = self.socket.recv(4096)
                if not data:
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
            
    def set_message_callback(self, callback: Callable):
        """
        Установка callback для входящих сообщений
        """
        self.message_callback = callback
        
    def _handle_p2p_message(self, message):
        """
        Обработка сообщения от P2P клиента
        """
        if self.message_callback:
            self.message_callback(message)
            
    def get_p2p_address(self) -> Optional[tuple]:
        """
        Получение публичного адреса P2P клиента
        """
        if self.p2p_client:
            return self.p2p_client.get_public_address()
        return None
        
    def establish_p2p_connection(self, peer_id: str, peer_ip: str, peer_port: int):
        """
        Установка P2P соединения
        """
        if self.p2p_client:
            return self.p2p_client.establish_p2p_connection(peer_id, peer_ip, peer_port)
        return False
        
    def add_p2p_peer(self, peer_id: str, ip: str, port: int, public_key: str):
        """
        Добавление пира для P2P соединения
        """
        if self.p2p_client:
            self.p2p_client.add_peer(peer_id, ip, port, public_key)