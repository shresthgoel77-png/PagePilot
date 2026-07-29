from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must strictly be at least 8 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one fundamental numeric value')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
