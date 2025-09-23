# app/schemas.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from .models import ConversationStatus, MessageRole

class TicketBase(BaseModel):
    title: str
    description: str | None = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None

class TicketRead(TicketBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------- AI Assistant Schemas ----------

class AssistRequest(BaseModel):
    message: str

# ---------- User Schemas ----------

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserRead(UserBase):
    id: int
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserRead

# ---------- Conversation Schemas ----------

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None

class ConversationRead(ConversationBase):
    id: int
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime
    user_id: Optional[int] = None
    message_count: Optional[int] = None  # Computed field

    model_config = ConfigDict(from_attributes=True)

# ---------- Message Schemas ----------

class MessageBase(BaseModel):
    content: str
    role: MessageRole

class MessageCreate(BaseModel):
    content: str
    # role will be set automatically based on context

class MessageRead(MessageBase):
    id: int
    created_at: datetime
    conversation_id: int
    ai_confidence: Optional[int] = None
    ai_action: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# ---------- Chat API Schemas ----------

class ChatSendMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    response: str
    action: str  # "answer" or "escalate"
    confidence: Optional[float] = None

class ConversationWithMessages(ConversationRead):
    messages: List[MessageRead] = []

    model_config = ConfigDict(from_attributes=True)