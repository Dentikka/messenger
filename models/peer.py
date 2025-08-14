"""
Модель пира
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Peer:
    id: Optional[int]
    peer_id: str
    public_key: str
    created_at: datetime
    
    def to_dict(self):
        return {
            'id': self.id,
            'peer_id': self.peer_id,
            'public_key': self.public_key,
            'created_at': self.created_at.isoformat()
        }