"""
STUN клиент для определения внешнего IP и порта
"""
import socket
import struct
import random
from typing import Tuple, Optional

class STUNClient:
    def __init__(self, stun_servers=None):
        # Список публичных STUN серверов
        self.stun_servers = stun_servers or [
            'stun.l.google.com:19302',
            'stun1.l.google.com:19302',
            'stun.stunprotocol.org:3478',
            'stun.voiparound.com:3478'
        ]
        
    def get_external_address(self) -> Optional[Tuple[str, int]]:
        """
        Получение внешнего IP и порта через STUN
        Возвращает: (external_ip, external_port) или None
        """
        for server in self.stun_servers:
            try:
                host, port = server.split(':')
                port = int(port)
                
                external_addr = self._query_stun_server(host, port)
                if external_addr:
                    return external_addr
            except Exception as e:
                print(f"STUN server {server} failed: {e}")
                continue
                
        return None
        
    def _query_stun_server(self, host: str, port: int) -> Optional[Tuple[str, int]]:
        """
        Отправка STUN запроса и обработка ответа
        """
        try:
            # Создаем UDP сокет
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)  # 3 секунды таймаут
            
            # STUN Binding Request
            transaction_id = random.getrandbits(96).to_bytes(12, 'big')
            stun_request = self._create_binding_request(transaction_id)
            
            # Отправляем запрос
            sock.sendto(stun_request, (host, port))
            
            # Получаем ответ
            response, _ = sock.recvfrom(1024)
            
            # Парсим ответ
            external_addr = self._parse_binding_response(response, transaction_id)
            
            sock.close()
            return external_addr
            
        except Exception as e:
            print(f"STUN query failed: {e}")
            return None
            
    def _create_binding_request(self, transaction_id: bytes) -> bytes:
        """
        Создание STUN Binding Request
        """
        # STUN message type: Binding Request (0x0001)
        message_type = 0x0001
        # Message length: 0 (no attributes)
        message_length = 0
        # Magic cookie
        magic_cookie = 0x2112A442
        
        # Pack header
        stun_header = struct.pack('!HHI12s', 
                                 message_type, 
                                 message_length, 
                                 magic_cookie, 
                                 transaction_id)
        return stun_header
        
    def _parse_binding_response(self, response: bytes, expected_tid: bytes) -> Optional[Tuple[str, int]]:
        """
        Парсинг STUN Binding Response
        """
        try:
            # Parse header
            message_type, message_length, magic_cookie, transaction_id = struct.unpack('!HHI12s', response[:20])
            
            # Check if it's our response
            if transaction_id != expected_tid:
                return None
                
            # Check if it's success response (0x0101)
            if message_type != 0x0101:
                return None
                
            # Parse attributes to find XOR-MAPPED-ADDRESS
            offset = 20
            while offset < len(response):
                if offset + 4 > len(response):
                    break
                    
                attr_type, attr_length = struct.unpack('!HH', response[offset:offset+4])
                offset += 4
                
                if offset + attr_length > len(response):
                    break
                    
                attr_value = response[offset:offset+attr_length]
                offset += attr_length
                
                # XOR-MAPPED-ADDRESS (0x0020)
                if attr_type == 0x0020 and len(attr_value) >= 8:
                    # Parse address family and port
                    family = struct.unpack('!H', attr_value[2:4])[0]
                    if family == 0x01:  # IPv4
                        xor_port = struct.unpack('!H', attr_value[4:6])[0]
                        port = xor_port ^ (magic_cookie >> 16)
                        
                        # Parse IP
                        xor_ip = struct.unpack('!I', attr_value[6:10])[0]
                        ip = xor_ip ^ magic_cookie
                        
                        ip_str = socket.inet_ntoa(struct.pack('!I', ip))
                        return (ip_str, port)
                        
            return None
            
        except Exception as e:
            print(f"Error parsing STUN response: {e}")
            return None

# Удобная функция для использования
def get_public_address() -> Optional[Tuple[str, int]]:
    """
    Получение публичного адреса текущего устройства
    """
    stun_client = STUNClient()
    return stun_client.get_external_address()

if __name__ == "__main__":
    # Тест STUN клиента
    print("Getting public address via STUN...")
    addr = get_public_address()
    if addr:
        print(f"Public address: {addr[0]}:{addr[1]}")
    else:
        print("Failed to get public address")