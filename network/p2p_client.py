"""
P2P клиент для Secure Messenger
"""
import json
import time
from typing import Callable, Optional, Tuple
from network.stun_client import get_public_address
from network.nat_traversal import HolePuncher, CoordinatedHolePuncher
from crypto.encryption import CryptoManager

class P2PClient:
    def __init__(self, peer_id: str, crypto_manager: CryptoManager):
        self.peer_id = peer_id
        self.crypto_manager = crypto_manager
        self.hole_puncher = HolePuncher()
        self.coordinated_puncher = CoordinatedHolePuncher(self.hole_puncher)
        self.message_callback = None
        self.connected_peers = {}  # peer_id -> (ip, port, public_key)
        self.public_address = None
        
    def start(self):
        """
        Запуск P2P клиента
        """
        # Получаем публичный адрес через STUN
        print("Getting public address via STUN...")
        self.public_address = get_public_address()
        
        if self.public_address:
            print(f"Public address: {self.public_address[0]}:{self.public_address[1]}")
        else:
            # Если STUN не работает, используем локальный адрес
            local_addr = self.hole_puncher.get_local_address()
            self.public_address = local_addr
            print(f"Using local address: {local_addr[0]}:{local_addr[1]}")
            
        # Запускаем Hole Puncher
        self.hole_puncher.start(on_message=self._handle_p2p_message)
        
    def stop(self):
        """
        Остановка P2P клиента
        """
        self.hole_puncher.stop()
        
    def add_peer(self, peer_id: str, ip: str, port: int, public_key: str):
        """
        Добавление пира для P2P соединения
        """
        self.connected_peers[peer_id] = (ip, port, public_key)
        print(f"Added P2P peer: {peer_id} at {ip}:{port}")
        
    def establish_p2p_connection(self, peer_id: str, peer_public_ip: str, peer_port: int):
        """
        Установка P2P соединения с пиром
        """
        print(f"Attempting P2P connection to {peer_id} at {peer_public_ip}:{peer_port}")
        
        # Hole Punching
        self.hole_puncher.punch_hole(peer_public_ip, peer_port, attempts=20)
        
        # Проверяем, установилось ли соединение
        test_message = {
            'type': 'p2p_test',
            'from': self.peer_id,
            'timestamp': time.time()
        }
        
        success = self.hole_puncher.send_direct(peer_public_ip, peer_port, json.dumps(test_message))
        if success:
            print(f"P2P connection established with {peer_id}")
            return True
        else:
            print(f"Failed to establish P2P connection with {peer_id}")
            return False
            
    def send_p2p_message(self, to_peer_id: str, encrypted_ dict) -> bool:
        """
        Отправка сообщения через P2P
        """
        if to_peer_id not in self.connected_peers:
            print(f"Unknown P2P peer: {to_peer_id}")
            return False
            
        ip, port, _ = self.connected_peers[to_peer_id]
        
        message = {
            'type': 'p2p_message',
            'from': self.peer_id,
            'to': to_peer_id,
            'data': encrypted_data,
            'timestamp': time.time()
        }
        
        message_str = json.dumps(message)
        success = self.hole_puncher.send_direct(ip, port, message_str)
        
        if success:
            print(f"P2P message sent to {to_peer_id}")
        else:
            print(f"Failed to send P2P message to {to_peer_id}")
            
        return success
        
    def _handle_p2p_message(self, message_str: str, sender_addr: Tuple[str, int]):
        """
        Обработка входящего P2P сообщения
        """
        try:
            message = json.loads(message_str)
            msg_type = message.get('type')
            
            if msg_type == 'p2p_test':
                # Ответ на тестовое сообщение
                response = {
                    'type': 'p2p_test_response',
                    'from': self.peer_id,
                    'timestamp': time.time()
                }
                self.hole_puncher.send_direct(sender_addr[0], sender_addr[1], json.dumps(response))
                print(f"Received P2P test from {sender_addr[0]}:{sender_addr[1]}")
                
            elif msg_type == 'p2p_test_response':
                print(f"P2P connection confirmed with {sender_addr[0]}:{sender_addr[1]}")
                
            elif msg_type == 'p2p_message':
                # Обработка входящего сообщения
                sender_id = message.get('from')
                encrypted_data = message.get('data')
                
                if self.message_callback:
                    # Передаем сообщение основному приложению
                    p2p_message = {
                        'type': 'p2p_message',
                        'from': sender_id,
                        'data': encrypted_data
                    }
                    self.message_callback(p2p_message)
                    
        except Exception as e:
            print(f"Error handling P2P message: {e}")
            
    def set_message_callback(self, callback: Callable):
        """
        Установка callback для входящих сообщений
        """
        self.message_callback = callback
        
    def get_public_address(self) -> Optional[Tuple[str, int]]:
        """
        Получение публичного адреса клиента
        """
        return self.public_address

# Пример использования
if __name__ == "__main__":
    # Тест P2P клиента
    from crypto.encryption import CryptoManager
    from config.settings import KEYS_DIR
    
    crypto_manager = CryptoManager(KEYS_DIR)
    if not crypto_manager.load_keys():
        crypto_manager.generate_keys()
        
    p2p_client = P2PClient("test_user", crypto_manager)
    p2p_client.start()
    
    try:
        input("P2P client running. Press Enter to stop...")
    finally:
        p2p_client.stop()