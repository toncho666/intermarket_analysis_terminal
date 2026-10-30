"""
Intermarket Analysis Terminal - Backend API
FastAPI application with all endpoints
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from app.config import settings
from app.database import get_db, init_db, close_db
from app.schemas import HealthResponse, Token, LoginRequest, UserResponse
from app.services.auth_service import auth_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Intermarket Analysis Terminal API",
    version="2.4.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# ===== Startup/Shutdown =====
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    logger.info("Starting Intermarket Analysis Terminal API...")
    await init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown():
    """Close database connections on shutdown"""
    logger.info("Shutting down API...")
    await close_db()


# ===== Dependencies =====
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = auth_service.decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Fetch user from database
    from app.models import User
    from sqlalchemy import select
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# ===== Health Check =====
@app.get("/api/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    from app.services.cache_service import cache_service
    
    # Check database
    try:
        await db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    # Check Redis
    redis_status = "connected" if cache_service.health_check() else "disconnected"
    
    return HealthResponse(
        status="ok",
        version=settings.MODEL_VERSION,
        timestamp=datetime.utcnow(),
        database=db_status,
        redis=redis_status,
    )


# ===== Auth Routes =====
@app.post("/api/auth/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and get JWT token"""
    from app.models import User
    from sqlalchemy import select
    
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not auth_service.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create token
    access_token = auth_service.create_access_token(
        data={"user_id": user.id, "email": user.email, "role": user.role}
    )
    
    return Token(access_token=access_token)


# ===== Include Routers =====
from app.routers import assets, prices, correlations, pairs, anomalies, regime, strategies, backtests, alerts, macro, reports

app.include_router(assets.router, prefix="/api", tags=["assets"])
app.include_router(prices.router, prefix="/api", tags=["prices"])
app.include_router(correlations.router, prefix="/api", tags=["correlations"])
app.include_router(pairs.router, prefix="/api", tags=["pairs"])
app.include_router(anomalies.router, prefix="/api", tags=["anomalies"])
app.include_router(regime.router, prefix="/api", tags=["regime"])
app.include_router(strategies.router, prefix="/api", tags=["strategies"])
app.include_router(backtests.router, prefix="/api", tags=["backtests"])
app.include_router(alerts.router, prefix="/api", tags=["alerts"])
app.include_router(macro.router, prefix="/api", tags=["macro"])
app.include_router(reports.router, prefix="/api", tags=["reports"])


# ===== Root =====
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Intermarket Analysis Terminal API",
        "version": settings.MODEL_VERSION,
        "docs": "/docs",
    }
