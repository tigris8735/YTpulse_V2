# backend/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import User
from ..auth import hash_password, verify_password, create_jwt , decode_jwt
import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status


router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str

@router.post("/register", response_model=AuthResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = hash_password(data.password)
    user = User(email=data.email, password_hash=hashed, plan="free")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_jwt(str(user.id), user.email)
    return {"access_token": token, "user_id": str(user.id)}

@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt(str(user.id), user.email)
    return {"access_token": token, "user_id": str(user.id)}
