from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from . import models, schemas
from typing import Optional, List

# ---------- Ticket CRUD ----------

def create_ticket(db: Session, ticket_in: schemas.TicketCreate, user_id: int = None) -> models.Ticket:
    ticket_data = ticket_in.dict()
    if user_id:
        ticket_data["user_id"] = user_id
    ticket = models.Ticket(**ticket_data)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_tickets(db: Session, skip: int = 0, limit: int = 100, q: str | None = None, status: str | None = None):
    query = db.query(models.Ticket)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(models.Ticket.title.ilike(like), models.Ticket.description.ilike(like)))
    if status:
        query = query.filter(models.Ticket.status == status)
    return query.order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()

def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

def update_ticket(db: Session, ticket_id: int, ticket_in: schemas.TicketUpdate):
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return None
    for field, value in ticket_in.dict(exclude_unset=True).items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket

def delete_ticket(db: Session, ticket_id: int) -> bool:
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return False
    db.delete(ticket)
    db.commit()
    return True

# ---------- Conversation CRUD ----------

def create_conversation(db: Session, conversation_in: schemas.ConversationCreate, user_id: Optional[int] = None) -> models.Conversation:
    """Create a new conversation."""
    conversation_data = conversation_in.dict()
    if user_id:
        conversation_data["user_id"] = user_id
    
    conversation = models.Conversation(**conversation_data)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_conversations(
    db: Session, 
    user_id: Optional[int] = None, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[models.ConversationStatus] = None
) -> List[models.Conversation]:
    """Get conversations for a user (or all if user_id is None)."""
    query = db.query(models.Conversation)
    
    if user_id is not None:
        query = query.filter(models.Conversation.user_id == user_id)
    
    if status:
        query = query.filter(models.Conversation.status == status)
    
    return query.order_by(desc(models.Conversation.updated_at)).offset(skip).limit(limit).all()

def get_conversation(db: Session, conversation_id: int, user_id: Optional[int] = None) -> Optional[models.Conversation]:
    """Get a specific conversation."""
    query = db.query(models.Conversation).filter(models.Conversation.id == conversation_id)
    
    # Add user filter for security (users can only access their own conversations)
    if user_id is not None:
        query = query.filter(models.Conversation.user_id == user_id)
    
    return query.first()

def update_conversation(
    db: Session, 
    conversation_id: int, 
    conversation_in: schemas.ConversationUpdate,
    user_id: Optional[int] = None
) -> Optional[models.Conversation]:
    """Update a conversation."""
    conversation = get_conversation(db, conversation_id, user_id)
    if not conversation:
        return None
    
    for field, value in conversation_in.dict(exclude_unset=True).items():
        setattr(conversation, field, value)
    
    db.commit()
    db.refresh(conversation)
    return conversation

def delete_conversation(db: Session, conversation_id: int, user_id: Optional[int] = None) -> bool:
    """Delete a conversation and all its messages."""
    conversation = get_conversation(db, conversation_id, user_id)
    if not conversation:
        return False
    
    db.delete(conversation)
    db.commit()
    return True

def get_conversation_with_messages(db: Session, conversation_id: int, user_id: Optional[int] = None) -> Optional[models.Conversation]:
    """Get a conversation with all its messages loaded."""
    query = db.query(models.Conversation).filter(models.Conversation.id == conversation_id)
    
    if user_id is not None:
        query = query.filter(models.Conversation.user_id == user_id)
    
    conversation = query.first()
    if conversation:
        # Explicitly load messages if not already loaded
        conversation.messages  # This will trigger loading due to relationship
    
    return conversation

# ---------- Message CRUD ----------

def create_message(
    db: Session, 
    conversation_id: int, 
    content: str, 
    role: models.MessageRole,
    ai_confidence: Optional[int] = None,
    ai_action: Optional[str] = None
) -> models.Message:
    """Create a new message in a conversation."""
    message = models.Message(
        conversation_id=conversation_id,
        content=content,
        role=role,
        ai_confidence=ai_confidence,
        ai_action=ai_action
    )
    
    db.add(message)
    
    # Update conversation's updated_at timestamp
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if conversation:
        conversation.updated_at = func.now()
    
    db.commit()
    db.refresh(message)
    return message

def get_messages(
    db: Session, 
    conversation_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.Message]:
    """Get messages for a conversation."""
    return (db.query(models.Message)
            .filter(models.Message.conversation_id == conversation_id)
            .order_by(models.Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all())

def get_message(db: Session, message_id: int) -> Optional[models.Message]:
    """Get a specific message."""
    return db.query(models.Message).filter(models.Message.id == message_id).first()

def delete_message(db: Session, message_id: int) -> bool:
    """Delete a specific message."""
    message = get_message(db, message_id)
    if not message:
        return False
    
    db.delete(message)
    db.commit()
    return True

# ---------- Helper Functions ----------

def generate_conversation_title(db: Session, conversation_id: int) -> str:
    """Generate a title for a conversation based on the first user message."""
    first_message = (db.query(models.Message)
                    .filter(models.Message.conversation_id == conversation_id)
                    .filter(models.Message.role == models.MessageRole.USER)
                    .order_by(models.Message.created_at.asc())
                    .first())
    
    if first_message:
        # Take first 50 characters and add ellipsis if longer
        content = first_message.content.strip()
        if len(content) > 50:
            return content[:50] + "..."
        return content
    
    return "New Conversation"

def update_conversation_title(db: Session, conversation_id: int) -> Optional[models.Conversation]:
    """Auto-generate and update conversation title if not set."""
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    
    if conversation and not conversation.title:
        conversation.title = generate_conversation_title(db, conversation_id)
        db.commit()
        db.refresh(conversation)
    
    return conversation
