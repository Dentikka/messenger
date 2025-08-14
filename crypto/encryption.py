"""
Модуль шифрования для Secure Messenger
"""
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
import os
import base64

class CryptoManager:
    def __init__(self, keys_dir):
        self.keys_dir = keys_dir
        self.private_key_path = keys_dir / "private_key.pem"
        self.public_key_path = keys_dir / "public_key.pem"
        self.private_key = None
        self.public_key = None
        
    def generate_keys(self):
        """Генерация пары ключей RSA"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        public_key = private_key.public_key()
        
        # Сохраняем приватный ключ
        with open(self.private_key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        
        # Сохраняем публичный ключ
        with open(self.public_key_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )
        
        self.private_key = private_key
        self.public_key = public_key
        
    def load_keys(self):
        """Загрузка существующих ключей"""
        if not self.private_key_path.exists() or not self.public_key_path.exists():
            return False
            
        with open(self.private_key_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
            )
        
        with open(self.public_key_path, "rb") as f:
            self.public_key = serialization.load_pem_public_key(f.read())
            
        return True
        
    def get_public_key_pem(self):
        """Получение публичного ключа в формате PEM"""
        if not self.public_key:
            return None
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
    def encrypt_message(self, message: str, recipient_public_key_pem: bytes):
        """Шифрование сообщения для получателя"""
        # Генерируем симметричный ключ
        symmetric_key = os.urandom(32)  # AES-256
        
        # Шифруем сообщение симметричным ключом
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Добавляем паддинг
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        
        encrypted_message = encryptor.update(padded_data) + encryptor.finalize()
        
        # Шифруем симметричный ключ публичным ключом получателя
        recipient_public_key = serialization.load_pem_public_key(recipient_public_key_pem)
        encrypted_key = recipient_public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            'encrypted_message': base64.b64encode(encrypted_message).decode(),
            'encrypted_key': base64.b64encode(encrypted_key).decode(),
            'iv': base64.b64encode(iv).decode()
        }
        
    def decrypt_message(self, encrypted_data: dict):
        """Расшифровка сообщения"""
        if not self.private_key:
            raise Exception("Private key not loaded")
            
        # Расшифровываем симметричный ключ
        encrypted_key = base64.b64decode(encrypted_data['encrypted_key'])
        symmetric_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Расшифровываем сообщение
        encrypted_message = base64.b64decode(encrypted_data['encrypted_message'])
        iv = base64.b64decode(encrypted_data['iv'])
        
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
        
        # Убираем паддинг
        unpadder = sym_padding.PKCS7(128).unpadder()
        message = unpadder.update(padded_message) + unpadder.finalize()
        
        return message.decode()