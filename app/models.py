from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .db import Base
import enum

class ConversationStatus(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived" 
    ESCALATED = "escalated"

class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    role = Column(String(20), default="user")  # "user" or "admin"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tickets = relationship("Ticket", back_populates="creator")
    conversations = relationship("Conversation", back_populates="user")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Optional: link ticket to user who created it
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", back_populates="tickets")
    
    # Optional: link ticket to conversation that escalated
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    conversation = relationship("Conversation", back_populates="escalated_ticket")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)  # Auto-generated or user-defined
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Optional: link to user (null for anonymous conversations)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="conversations")
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    escalated_ticket = relationship("Ticket", back_populates="conversation", uselist=False)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Link to conversation
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    conversation = relationship("Conversation", back_populates="messages")
    
    # Optional metadata for AI responses
    ai_confidence = Column(Integer, nullable=True)  # 0-100 confidence score
    ai_action = Column(String(50), nullable=True)  # "answer", "escalate", etc.
