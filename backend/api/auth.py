"""
Authentication & Authorization - JWT + OAuth2
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional, Dict
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-this-for-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

# Models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    role: str = "viewer"

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict

class TokenData(BaseModel):
    username: Optional[str] = None

# Fake database - replace with real DB in production
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@deepguard.com",
        "full_name": "System Administrator",
        "hashed_password": "$2b$12$8KqZ4XK5YxLZxILxILxILuIlIuIlIuIlIuIlIuIlIuIlIuIlIuIl",  # "admin123"
        "disabled": False,
        "role": "admin"
    },
    "security": {
        "username": "security",
        "email": "security@deepguard.com",
        "full_name": "Security Officer",
        "hashed_password": "$2b$12$8KqZ4XK5YxLZxILxILxILuIlIuIlIuIlIuIlIuIlIuIlIuIlIuIl",  # "security123"
        "disabled": False,
        "role": "security"
    }
}

# Simple password verification (for demo - use proper hashing in production)
def verify_password(plain_password, hashed_password):
    # For demo purposes, accept these simple passwords
    # In production, use proper password hashing like bcrypt
    demo_passwords = {
        "admin": "admin123",
        "security": "security123"
    }
    return demo_passwords.get(plain_password) == plain_password or plain_password in ["admin123", "security123"]

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # Simple password check for demo
    if (username == "admin" and password == "admin123") or (username == "security" and password == "security123"):
        return user
    return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # For demo, return a simple token (in production, use JWT)
    return data.get("sub", "demo_token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    # For demo, return admin user if token exists
    if token:
        return User(username="admin", role="admin", full_name="Admin User")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    # Simple authentication for demo
    if form_data.username == "admin" and form_data.password == "admin123":
        user_data = {
            "username": "admin",
            "email": "admin@deepguard.com",
            "full_name": "System Administrator",
            "role": "admin"
        }
        access_token = create_access_token(data={"sub": form_data.username, "role": "admin"})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }
    elif form_data.username == "security" and form_data.password == "security123":
        user_data = {
            "username": "security",
            "email": "security@deepguard.com",
            "full_name": "Security Officer",
            "role": "security"
        }
        access_token = create_access_token(data={"sub": form_data.username, "role": "security"})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user

@router.post("/register")
async def register_user(username: str, password: str, email: str = None, full_name: str = None):
    """Register a new user"""
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # In production, hash the password
    fake_users_db[username] = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "hashed_password": password,  # In production, store hashed password
        "disabled": False,
        "role": "viewer"
    }
    return {"message": "User created successfully", "username": username}