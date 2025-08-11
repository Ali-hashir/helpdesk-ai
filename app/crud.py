from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas

def create_ticket(db: Session, ticket_in: schemas.TicketCreate) -> models.Ticket:
    ticket = models.Ticket(**ticket_in.dict())
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
