from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .config import settings
from .db import Base, engine, SessionLocal
from . import crud, schemas

app = FastAPI(title=settings.app_name)
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def root():
    return {"status": "ok"}

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Tickets API ----------

@app.post("/tickets", response_model=schemas.TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_in: schemas.TicketCreate, db: Session = Depends(get_db)):
    return crud.create_ticket(db, ticket_in)

@app.get("/tickets", response_model=list[schemas.TicketRead])
def list_tickets(
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_tickets(db, skip=skip, limit=limit, q=q, status=status)

@app.get("/tickets/{ticket_id}", response_model=schemas.TicketRead)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.patch("/tickets/{ticket_id}", response_model=schemas.TicketRead)
def update_ticket(ticket_id: int, ticket_in: schemas.TicketUpdate, db: Session = Depends(get_db)):
    ticket = crud.update_ticket(db, ticket_id, ticket_in)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    if not crud.delete_ticket(db, ticket_id):
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"detail": "Ticket deleted successfully"}

# ---------- Admin view ----------

@app.get("/admin/tickets", response_class=HTMLResponse)
def admin_tickets(
    request: Request,
    q: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    items = crud.get_tickets(db, q=q, status=status, limit=200)
    return templates.TemplateResponse(
        "tickets.html",
        {"request": request, "items": items, "q": q or "", "status": status or ""},
    )
