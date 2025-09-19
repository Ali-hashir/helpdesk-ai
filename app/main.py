from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .config import settings
from .db import Base, engine, SessionLocal
from . import crud, schemas, ai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.app_name)
templates = Jinja2Templates(directory="app/templates")

# Configure CORS origins
if settings.cors_origins:
    if settings.cors_origins == "*":
        ALLOWED = ["*"]
    else:
        ALLOWED = [origin.strip() for origin in settings.cors_origins.split(",")]
else:
    # Default origins for production/development
    ALLOWED = [
        "https://helpdesk-ai-eight.vercel.app/",
        "https://helpdesk-ai-eight.vercel.app",
        "https://n8n-latest-c77l.onrender.com/",
        "http://localhost:3000",  # Vite dev server
        "http://localhost:5173",  # Alternative Vite port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5678",  # n8n local
        "http://127.0.0.1:5678",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ---------- AI Assistant Webhook ----------

@app.post("/webhook/assist-or-ticket")
async def assist_or_ticket(request: schemas.AssistRequest, db: Session = Depends(get_db)):
    """
    AI-powered assistant endpoint that either provides an answer or creates a ticket.
    
    This endpoint replaces the n8n workflow functionality.
    """
    try:
        # Get AI decision from Groq
        decision = await ai.call_groq_api(request.message)
        
        # Check if we should provide direct answer (matches n8n Decision node logic)
        if ai.should_answer_directly(decision):
            return {
                "action": "answer",
                "confidence": decision.get("confidence", 0.0),
                "reply_text": decision.get("reply_text", "")
            }
        else:
            # AI decided to escalate: create a ticket
            ticket_data = ai.create_ticket_from_decision(request.message, decision)
            ticket = crud.create_ticket(db, ticket_data)
            
            return {
                "action": "escalate",
                "ticket_id": ticket.id,
                "status": ticket.status
            }
            
    except Exception as e:
        # API error - return error to user (don't create ticket)
        raise HTTPException(
            status_code=500, 
            detail=f"AI service error: {str(e)}"
        )

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
