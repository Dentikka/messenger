"""
CLI интерфейс для Secure Messenger
"""
import click
import json
import base64
from pathlib import Path
from config.settings import DATA_DIR, KEYS_DIR, DB_PATH
from crypto.encryption import CryptoManager
from storage.database import DatabaseManager
from network.client import MessageClient

class MessengerApp:
    def __init__(self, peer_id: str):
        self.peer_id = peer_id
        self.crypto_manager = CryptoManager(KEYS_DIR)
        self.db_manager = DatabaseManager(DB_PATH)
        self.client = MessageClient(peer_id)
        
        # Инициализация
        self._initialize()
        
    def _initialize(self):
        """Инициализация приложения"""
        # Загрузка или генерация ключей
        if not self.crypto_manager.load_keys():
            print("Generating new keys...")
            self.crypto_manager.generate_keys()
            
        # Подключение к серверу с поддержкой P2P
        if not self.client.connect(crypto_manager=self.crypto_manager):
            print("Warning: Could not connect to server")
            
        # Получаем публичный адрес для P2P
        p2p_addr = self.client.get_p2p_address()
        if p2p_addr:
            print(f"P2P address: {p2p_addr[0]}:{p2p_addr[1]}")
            
        # Установка callback для сообщений
        self.client.set_message_callback(self._handle_incoming_message)
        
    def _handle_incoming_message(self, message_data):
        """Обработка входящего сообщения"""
        if message_data.get('type') == 'message':
            sender_id = message_data.get('from')
            encrypted_data = message_data.get('data')
            
            try:
                # Расшифровка сообщения
                decrypted_message = self.crypto_manager.decrypt_message(encrypted_data)
                
                # Сохранение в БД
                self.db_manager.save_message(sender_id, decrypted_message, 'received')
                
                print(f"\n[{sender_id}] {decrypted_message}")
                print("messenger> ", end='', flush=True)
                
            except Exception as e:
                print(f"Error decrypting message: {e}")
                
    def send_message(self, recipient_id: str, message: str):
        """Отправка сообщения"""
        # Получаем публичный ключ получателя
        peer = self.db_manager.get_peer(recipient_id)
        if not peer:
            print(f"Unknown peer: {recipient_id}")
            return False
            
        try:
            # Шифруем сообщение
            recipient_public_key = peer.public_key.encode()
            encrypted_data = self.crypto_manager.encrypt_message(message, recipient_public_key)
            
            # Отправляем через сеть
            if self.client.send_message(recipient_id, encrypted_data):
                # Сохраняем в БД
                self.db_manager.save_message(recipient_id, message, 'sent')
                return True
            else:
                print("Failed to send message")
                return False
                
        except Exception as e:
            print(f"Error encrypting message: {e}")
            return False
            
    def add_peer(self, peer_id: str, public_key_pem: str):
        """Добавление нового пира"""
        self.db_manager.add_peer(peer_id, public_key_pem)
        print(f"Peer {peer_id} added")
        
    def show_history(self, peer_id: str):
        """Показ истории сообщений"""
        messages = self.db_manager.get_message_history(peer_id)
        if not messages:
            print("No messages found")
            return
            
        print(f"\nMessage history with {peer_id}:")
        print("-" * 50)
        for msg in reversed(messages):
            direction = "→" if msg.direction == 'sent' else "←"
            print(f"[{msg.timestamp.strftime('%H:%M:%S')}] {direction} {msg.content}")
            
    def list_peers(self):
        """Список всех пиров"""
        peers = self.db_manager.get_all_peers()
        if not peers:
            print("No peers found")
            return
            
        print("\nKnown peers:")
        print("-" * 30)
        for peer in peers:
            print(f"{peer.peer_id}")

@click.group()
@click.option('--peer-id', required=True, help='Your peer ID')
@click.pass_context
def cli(ctx, peer_id):
    """Secure Messenger CLI"""
    ctx.ensure_object(dict)
    ctx.obj['app'] = MessengerApp(peer_id)

@cli.command()
@click.argument('recipient_id')
@click.argument('message')
@click.pass_obj
def send(obj, recipient_id, message):
    """Send a message to a peer"""
    app = obj['app']
    if app.send_message(recipient_id, message):
        print("Message sent successfully")

@cli.command()
@click.argument('peer_id')
@click.pass_obj
def history(obj, peer_id):
    """Show message history with a peer"""
    app = obj['app']
    app.show_history(peer_id)

@cli.command()
@click.pass_obj
def peers(obj):
    """List all known peers"""
    app = obj['app']
    app.list_peers()

@cli.command()
@click.argument('peer_id')
@click.argument('public_key_file', type=click.Path(exists=True))
@click.pass_obj
def add_peer(obj, peer_id, public_key_file):
    """Add a new peer with their public key"""
    app = obj['app']
    with open(public_key_file, 'r') as f:
        public_key = f.read()
    app.add_peer(peer_id, public_key)

if __name__ == '__main__':
    cli()