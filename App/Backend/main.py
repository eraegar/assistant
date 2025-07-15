import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Header, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
import models, schemas, database, auth
import sys
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Import new API routers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from routers.client_api import router as client_router
    print("✅ Client API router loaded successfully")
except ImportError as e:
    print(f"⚠️ Client API router not found, creating placeholder. Error: {e}")
    from fastapi import APIRouter
    client_router = APIRouter(prefix="/api/v1/clients", tags=["clients"])

try:
    from routers.assistant_api import router as assistant_router
    print("✅ Assistant API router loaded successfully")
except ImportError as e:
    print(f"⚠️ Assistant API router not found, creating placeholder. Error: {e}")
    from fastapi import APIRouter
    assistant_router = APIRouter(prefix="/api/v1/assistants", tags=["assistants"])

try:
    from routers.management_api import router as management_router
    print("✅ Management API router loaded successfully")
except ImportError as e:
    print(f"⚠️ Management API router not found, creating placeholder. Error: {e}")
    from fastapi import APIRouter
    management_router = APIRouter(prefix="/api/v1/management", tags=["management"])

# Create database tables
print("Creating database tables...")
models.Base.metadata.create_all(bind=database.engine)
print("Database tables created successfully!")

app = FastAPI(
    title="Assistant-for-Rent API", 
    version="2.0.0",
    description="Multi-service API for Client, Assistant, and Management interfaces"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    print(f"➡️  Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"⬅️  Outgoing response: {response.status_code} for {request.method} {request.url.path}")
    return response

# Background task lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize application services"""
    print("🚀 Application starting up...")
    print("✅ Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup application services"""
    print("🛑 Application shutting down...")
    print("✅ Application shutdown complete")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://t.me",
        "https://web.telegram.org",
        "*"  # Keep wildcard for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# INCLUDE NEW API ROUTERS
# =============================================================================

# Include the new service-specific routers
app.include_router(client_router)
app.include_router(assistant_router)
app.include_router(management_router)

# =============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# =============================================================================

from fastapi import APIRouter
auth_router = APIRouter(prefix="/auth", tags=["legacy-auth"])

@auth_router.post("/register", response_model=schemas.UserOut)
def legacy_register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Legacy registration endpoint - redirects to client registration"""
    print(f"🔥 Legacy registration attempt - redirecting to client API")
    
    # For now, assume all legacy registrations are clients
    if user.role == models.UserRole.client:
        # Redirect to client registration logic
        existing_user = db.query(models.User).filter(models.User.phone == user.phone).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Phone already registered")
        
        hashed = auth.get_password_hash(user.password)
        db_user = models.User(
            phone=user.phone, 
            password_hash=hashed, 
            name=user.name,
            role=user.role,
            telegram_username=user.telegram_username
        )
        
        db.add(db_user)
        db.flush()
        
        # Create appropriate profile based on role
        if user.role == models.UserRole.client:
            client_profile = models.ClientProfile(user_id=db_user.id)
            db.add(client_profile)
        
        db.commit()
        db.refresh(db_user)
        
        return db_user
    else:
        raise HTTPException(status_code=400, detail="Use role-specific registration endpoints")

@auth_router.post("/login")
def legacy_login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Legacy login endpoint"""
    print(f"🔑 Legacy login attempt: {user.phone}")
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if not db_user or not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect phone or password")
    
    token = auth.create_access_token({
        "user_id": db_user.id, 
        "role": db_user.role.value
    })
    return {"access_token": token, "token_type": "bearer"}

@auth_router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# Include legacy auth router
app.include_router(auth_router)

# Include legacy tasks router for backward compatibility
try:
    from routers import tasks as legacy_tasks
    app.include_router(legacy_tasks.router, prefix="/legacy")
    print("✅ Legacy tasks router loaded successfully")
except ImportError as e:
    print(f"⚠️ Legacy tasks router not found. Error: {e}")

# =============================================================================
# STATIC FILES & FRONTEND
# =============================================================================

# Mount static files - commented out since we use separate React apps now
# frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
# app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Serve a simple API info page instead of HTML frontend
@app.get("/")
def read_root():
    """API information root endpoint"""
    print("🏠 Serving API info")
    return {
        "message": "Telegram Assistant API v2.0.0",
        "services": {
            "client_app": os.getenv("CLIENT_APP_URL", "http://localhost:3000"),
            "manager_app": os.getenv("MANAGER_APP_URL", "http://localhost:3001"),
            "api_docs": f'{os.getenv("API_URL", "http://localhost:8000")}/docs'
        },
        "status": "running"
    }


# =============================================================================
# DUPLICATE ENDPOINTS REMOVED
# =============================================================================
# The endpoints previously defined directly in this file were duplicates of
# the ones in the /routers directory. They have been removed to ensure that
# the modular router-based implementations are used, which is the correct
# and maintainable approach. All logic should now reside in the respective
# router files (client_api.py, assistant_api.py, management_api.py).
# =============================================================================