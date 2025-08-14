"""
Сервер для Secure Messenger
"""
import socket
import threading
import json
import base64
from config.settings import DEFAULT_HOST, DEFAULT_PORT

class MessageServer:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = None
        
    def start(self):
        """Запуск сервера"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        print(f"Server started on {self.host}:{self.port}")
        
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server_socket.close()
            
    def handle_client(self, client_socket, address):
        """Обработка клиента"""
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                try:
                    message = json.loads(data.decode())
                    self.process_message(message, client_socket)
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            
    def process_message(self, message, client_socket):
        """Обработка сообщения"""
        msg_type = message.get('type')
        
        if msg_type == 'register':
            peer_id = message.get('peer_id')
            self.clients[peer_id] = client_socket
            print(f"Registered peer: {peer_id}")
            
        elif msg_type == 'message':
            recipient_id = message.get('to')
            if recipient_id in self.clients:
                recipient_socket = self.clients[recipient_id]
                try:
                    recipient_socket.send(json.dumps(message).encode())
                except:
                    del self.clients[recipient_id]
                    
    def stop(self):
        """Остановка сервера"""
        if self.server_socket:
            self.server_socket.close()