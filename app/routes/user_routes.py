from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_session
from app.models import User
from app.auth import hash_password, verify_password, create_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = None

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        full_name=user.full_name
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

@router.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
