from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
import redis.asyncio as redis
import json
from typing import Optional

from ..core.config import settings
from ..core.database import get_db

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: datetime

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Check cache first
    cached_user = await request.app.redis.get(f"user:{user_id}")
    if cached_user:
        return json.loads(cached_user)
    
    # Query database
    result = await db.execute(
        text("SELECT id, email, username, first_name, last_name, is_active FROM users.users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    user = result.fetchone()
    
    if user is None:
        raise credentials_exception
    
    user_dict = dict(user._mapping)
    
    # Cache user for 15 minutes
    await request.app.redis.setex(
        f"user:{user_id}",
        900,  # 15 minutes
        json.dumps(user_dict, default=str)
    )
    
    return user_dict

# Routes
@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    
    # Check if user already exists
    result = await db.execute(
        text("SELECT id FROM users.users WHERE email = :email OR username = :username"),
        {"email": user_data.email, "username": user_data.username}
    )
    existing_user = result.fetchone()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    result = await db.execute(
        text("""
            INSERT INTO users.users (email, username, password_hash, first_name, last_name)
            VALUES (:email, :username, :password_hash, :first_name, :last_name)
            RETURNING id, email, username, first_name, last_name, is_active, created_at
        """),
        {
            "email": user_data.email,
            "username": user_data.username,
            "password_hash": hashed_password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name
        }
    )
    
    new_user = result.fetchone()
    await db.commit()
    
    # Publish user registration event
    await request.app.redis.publish(
        settings.channel_user_notifications,
        json.dumps({
            "event": "user_registered",
            "user_id": str(new_user.id),
            "email": new_user.email,
            "timestamp": datetime.utcnow().isoformat()
        })
    )
    
    return UserResponse(**dict(new_user._mapping))

@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    
    # Get user from database
    result = await db.execute(
        text("SELECT id, email, username, password_hash, first_name, last_name, is_active FROM users.users WHERE email = :email"),
        {"email": user_credentials.email}
    )
    user = result.fetchone()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    user_info = {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
    
    # Cache user session
    await request.app.redis.setex(
        f"session:{user.id}",
        settings.jwt_expire_minutes * 60,
        json.dumps({
            "user_id": str(user.id),
            "login_time": datetime.utcnow().isoformat(),
            "token": access_token
        })
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
        user_info=user_info
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

@router.post("/logout")
async def logout_user(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Logout user (invalidate session)"""
    user_id = current_user["id"]
    
    # Remove user from cache
    await request.app.redis.delete(f"user:{user_id}")
    await request.app.redis.delete(f"session:{user_id}")
    
    return {"message": "Successfully logged out"}
