"""
Модуль работы с базой данных для Secure Messenger
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Peer(Base):
    __tablename__ = 'peers'
    
    id = Column(Integer, primary_key=True)
    peer_id = Column(String, unique=True, nullable=False)
    public_key = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    peer_id = Column(String, ForeignKey('peers.peer_id'), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    direction = Column(String, nullable=False)  # 'sent' or 'received'
    
    peer = relationship("Peer")

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def add_peer(self, peer_id: str, public_key: str):
        """Добавление нового пира"""
        peer = self.session.query(Peer).filter_by(peer_id=peer_id).first()
        if not peer:
            peer = Peer(peer_id=peer_id, public_key=public_key)
            self.session.add(peer)
            self.session.commit()
        return peer
        
    def get_peer(self, peer_id: str):
        """Получение пира по ID"""
        return self.session.query(Peer).filter_by(peer_id=peer_id).first()
        
    def save_message(self, peer_id: str, content: str, direction: str):
        """Сохранение сообщения"""
        message = Message(
            peer_id=peer_id,
            content=content,
            direction=direction
        )
        self.session.add(message)
        self.session.commit()
        return message
        
    def get_message_history(self, peer_id: str, limit: int = 50):
        """Получение истории сообщений с пиром"""
        return self.session.query(Message)\
            .filter_by(peer_id=peer_id)\
            .order_by(Message.timestamp.desc())\
            .limit(limit)\
            .all()
            
    def get_all_peers(self):
        """Получение всех пиров"""
        return self.session.query(Peer).all()