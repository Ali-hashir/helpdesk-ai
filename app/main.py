from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
from .config import settings
from .db import Base, engine, SessionLocal
from . import crud, schemas, ai, auth, models
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
    """Initialize database tables on startup."""
    try:
        print("🔄 Initializing database...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        print("💡 You may need to run: python create_tables.py")

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
async def assist_or_ticket(
    assist_request: schemas.AssistRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_optional)
):
    """
    AI-powered assistant endpoint that either provides an answer or creates a ticket.
    
    This endpoint replaces the n8n workflow functionality.
    Works with or without authentication.
    """
    try:
        # Get AI decision from Groq
        decision = await ai.call_groq_api(assist_request.message)
        
        # Check if we should provide direct answer (matches n8n Decision node logic)
        if ai.should_answer_directly(decision):
            return {
                "action": "answer",
                "confidence": decision.get("confidence", 0.0),
                "reply_text": decision.get("reply_text", "")
            }
        else:
            # AI decided to escalate: create a ticket
            ticket_data = ai.create_ticket_from_decision(assist_request.message, decision)
            ticket = crud.create_ticket(db, ticket_data, user_id=current_user.id if current_user else None)
            
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

# ---------- Authentication Routes ----------

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    """Signup page."""
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/auth/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = auth.create_user(db, user)
    
    # Create access token
    access_token_expires = timedelta(hours=settings.access_token_expire_hours)
    access_token = auth.create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    
    user_data = schemas.UserRead.model_validate(db_user)
    response = JSONResponse({
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data.model_dump(mode='json')
    })
    # Set httpOnly cookie for browser navigation
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.access_token_expire_hours * 3600,
        path="/",
    )
    return response

@app.post("/auth/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token."""
    user = auth.authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(hours=settings.access_token_expire_hours)
    access_token = auth.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    user_data = schemas.UserRead.model_validate(user)
    response = JSONResponse({
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data.model_dump(mode='json')
    })
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.access_token_expire_hours * 3600,
        path="/",
    )
    return response

@app.get("/auth/me", response_model=schemas.UserRead)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):
    """Get current user information."""
    return schemas.UserRead.model_validate(current_user)

@app.post("/auth/logout")
def logout():
    """Logout user: clear httpOnly cookie."""
    response = JSONResponse({"message": "Successfully logged out"})
    response.delete_cookie("access_token", path="/")
    return response

@app.post("/auth/create-admin", response_model=schemas.Token)
def create_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create an admin user. For setup purposes only."""
    # Check if username or email already exists
    if auth.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    if auth.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create admin user
    hashed_password = auth.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role="admin"  # Admin role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(hours=settings.access_token_expire_hours)
    access_token = auth.create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    
    user_data = schemas.UserRead.model_validate(db_user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

# ---------- Protected User Dashboard ----------

@app.get("/dashboard", response_class=HTMLResponse)
def user_dashboard(
    request: Request,
    current_user: models.User = Depends(auth.get_current_user)
):
    """User dashboard for asking questions."""
    user_data = schemas.UserRead.model_validate(current_user)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user_data}
    )

# ---------- Admin view ----------

@app.get("/admin/tickets", response_class=HTMLResponse)
def admin_tickets(
    request: Request,
    q: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user)
):
    """Admin dashboard for viewing tickets."""
    items = crud.get_tickets(db, q=q, status=status, limit=200)
    admin_data = schemas.UserRead.model_validate(current_admin)
    return templates.TemplateResponse(
        "tickets.html",
        {"request": request, "items": items, "q": q or "", "status": status or "", "admin": admin_data},
    )
