import time
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from app.models.user import User
from app.core import security
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Localized basic naive logic bounds: Limits requests implicitly globally simulating standard Redis throttles safely
# For production scale deployments utilize redis based throttles implicitly parsing `fastapi-limiter` properly.
LOGIN_ATTEMPTS = defaultdict(list)

def rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    # Prune historical states aggressively resolving bounds
    attempts = [t for t in LOGIN_ATTEMPTS[ip] if now - t < 60]
    LOGIN_ATTEMPTS[ip] = attempts
    
    if len(attempts) >= 5:
        raise HTTPException(status_code=429, detail="Too many internal attempts mapping fault blocks implicitly. Cooldown triggered.")
    
    LOGIN_ATTEMPTS[ip].append(now)

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
         raise HTTPException(status_code=400, detail="Constraints strictly dictate implicitly unique email references.")
         
    hashed_password = security.get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error inherently halting mapping updates.")
        
    return UserResponse(from_attributes=True, id=str(new_user.id), email=new_user.email, created_at=new_user.created_at)

@router.post("/login", response_model=TokenResponse)
async def login(request: Request, user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    rate_limit(request)
    
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    
    if not user or not security.verify_password(user_in.password, user.hashed_password):
        # Strict indistinguishable feedback protecting underlying database enumerators accurately.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal authentication token parameters",
        )
        
    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(from_attributes=True, id=str(current_user.id), email=current_user.email, created_at=current_user.created_at)
