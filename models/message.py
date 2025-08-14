"""
Модель сообщения
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Message:
    id: Optional[int]
    peer_id: str
    content: str
    timestamp: datetime
    direction: str  # 'sent' or 'received'
    
    def to_dict(self):
        return {
            'id': self.id,
            'peer_id': self.peer_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'direction': self.direction
        }