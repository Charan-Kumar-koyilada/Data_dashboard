from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field
from typing import Optional, Dict
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Upload(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    filename: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class DataRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    upload_id: int = Field(foreign_key="upload.id")
    data: Dict = Field(sa_column=Column(JSON))  # ✅ Correct JSON column
