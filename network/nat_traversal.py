"""
Утилиты для обхода NAT (Hole Punching)
"""
import socket
import threading
import time
from typing import Callable, Optional, Tuple
import random

class HolePuncher:
    def __init__(self, local_port: int = 0):
        self.local_port = local_port
        self.socket = None
        self.running = False
        self.on_message_callback = None
        self.peers = {}  # peer_id -> (ip, port, last_seen)
        
    def start(self, on_message: Callable = None):
        """
        Запуск Hole Punching клиента
        """
        self.on_message_callback = on_message
        self.running = True
        
        # Создаем UDP сокет
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.local_port))
        
        # Запускаем поток для приема сообщений
        self.receive_thread = threading.Thread(target=self._receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
        print(f"Hole Puncher started on port {self.socket.getsockname()[1]}")
        
    def stop(self):
        """
        Остановка клиента
        """
        self.running = False
        if self.socket:
            self.socket.close()
            
    def _receive_loop(self):
        """
        Цикл приема сообщений
        """
        while self.running:
            try:
                self.socket.settimeout(1.0)
                data, addr = self.socket.recvfrom(4096)
                
                # Обновляем информацию о пире
                self._update_peer_info(addr)
                
                # Обрабатываем сообщение
                if self.on_message_callback:
                    try:
                        message = data.decode('utf-8')
                        self.on_message_callback(message, addr)
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error in receive loop: {e}")
                break
                
    def punch_hole(self, target_ip: str, target_port: int, attempts: int = 20):
        """
        Hole Punching к целевому адресу
        """
        print(f"Punching hole to {target_ip}:{target_port}")
        
        # Отправляем пробные пакеты для открытия порта в NAT
        for i in range(attempts):
            try:
                # Отправляем разные типы сообщений
                messages = [
                    b'PING',
                    f'HOLE_PUNCH_{i}'.encode(),
                    b'KEEP_ALIVE'
                ]
                
                for msg in messages:
                    self.socket.sendto(msg, (target_ip, target_port))
                    
                time.sleep(0.1)  # Небольшая пауза
                
            except Exception as e:
                print(f"Hole punch attempt {i} failed: {e}")
                
    def send_to_peer(self, peer_id: str, message: str) -> bool:
        """
        Отправка сообщения пиру
        """
        if peer_id not in self.peers:
            print(f"Unknown peer: {peer_id}")
            return False
            
        ip, port, _ = self.peers[peer_id]
        try:
            self.socket.sendto(message.encode('utf-8'), (ip, port))
            return True
        except Exception as e:
            print(f"Failed to send to peer {peer_id}: {e}")
            return False
            
    def send_direct(self, ip: str, port: int, message: str) -> bool:
        """
        Прямая отправка сообщения
        """
        try:
            self.socket.sendto(message.encode('utf-8'), (ip, port))
            return True
        except Exception as e:
            print(f"Failed to send direct message: {e}")
            return False
            
    def _update_peer_info(self, addr: Tuple[str, int]):
        """
        Обновление информации о пире
        """
        ip, port = addr
        peer_id = f"{ip}:{port}"
        self.peers[peer_id] = (ip, port, time.time())
        
    def get_local_address(self) -> Tuple[str, int]:
        """
        Получение локального адреса
        """
        if self.socket:
            return self.socket.getsockname()
        return ('127.0.0.1', 0)
        
    def get_peer_info(self, peer_id: str) -> Optional[Tuple[str, int, float]]:
        """
        Получение информации о пире
        """
        return self.peers.get(peer_id)

# Утилита для координированного Hole Punching
class CoordinatedHolePuncher:
    def __init__(self, hole_puncher: HolePuncher):
        self.hole_puncher = hole_puncher
        
    def coordinate_punching(self, peer1_addr: Tuple[str, int], 
                          peer2_addr: Tuple[str, int],
                          coordination_server: Tuple[str, int]):
        """
        Координированный Hole Punching через сервер координации
        """
        # В реальной реализации сервер координации должен:
        # 1. Сообщить каждому клиенту адрес другого
        # 2. Синхронизировать время начала hole punching
        # 3. Обменяться NAT типами клиентов
        
        print(f"Coordinating hole punching between {peer1_addr} and {peer2_addr}")
        
        # Оба клиента начинают отправлять пакеты друг другу одновременно
        def punch_target(target_addr):
            self.hole_puncher.punch_hole(target_addr[0], target_addr[1], attempts=30)
            
        # Запускаем в отдельных потоках
        thread1 = threading.Thread(target=punch_target, args=(peer2_addr,))
        thread2 = threading.Thread(target=punch_target, args=(peer1_addr,))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        print("Hole punching coordination completed")