import time
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from app.models.user import User
import uuid
from app.core import security
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

LOGIN_ATTEMPTS = defaultdict(list)

def rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    attempts = [t for t in LOGIN_ATTEMPTS[ip] if now - t < 60]
    LOGIN_ATTEMPTS[ip] = attempts
    
    if len(attempts) >= 5:
        raise HTTPException(status_code=429, detail="Too many internal attempts mapping fault blocks implicitly. Cooldown triggered.")
    
    LOGIN_ATTEMPTS[ip].append(now)

async def _claim_guest_data(db: AsyncSession, guest_id: str, new_user_id: uuid.UUID):
    try:
        g_uuid = uuid.UUID(guest_id)
        # Update Projects and Chats safely via direct SQL binding since foreign keys cascade natively
        await db.execute(text("UPDATE projects SET user_id = :n WHERE user_id = :g").bindparams(n=new_user_id, g=g_uuid))
        await db.execute(text("UPDATE chat_sessions SET user_id = :n WHERE user_id = :g").bindparams(n=new_user_id, g=g_uuid))
        await db.execute(text("DELETE FROM users WHERE id = :g AND is_guest = true").bindparams(g=g_uuid))
        await db.commit()
    except Exception:
        await db.rollback()
        pass # Ignore claiming errors if guest didn't trace appropriately

@router.post("/register", response_model=UserResponse)
async def register(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
         raise HTTPException(status_code=400, detail="Constraints strictly dictate implicitly unique email references.")
         
    hashed_password = security.get_password_hash(user_in.password)
    guest_id = request.headers.get("X-Guest-Session-Id")
    
    # Check if we can just promote the shadow user instead
    if guest_id:
        try:
            g_uuid = uuid.UUID(guest_id)
            stmt = select(User).where(User.id == g_uuid, User.is_guest == True)
            res = await db.execute(stmt)
            shadow_user = res.scalar_one_or_none()
            if shadow_user:
                shadow_user.email = user_in.email
                shadow_user.hashed_password = hashed_password
                shadow_user.is_guest = False
                try:
                    await db.commit()
                    await db.refresh(shadow_user)
                    return UserResponse(id=str(shadow_user.id), email=shadow_user.email, created_at=shadow_user.created_at)
                except IntegrityError:
                    await db.rollback()
        except Exception:
            pass

    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_guest=False
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error inherently halting mapping updates.")
        
    return UserResponse(id=str(new_user.id), email=new_user.email, created_at=new_user.created_at)

@router.post("/login", response_model=TokenResponse)
async def login(request: Request, user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    rate_limit(request)
    
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    
    if not user or not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal authentication token parameters",
        )
        
    guest_id = request.headers.get("X-Guest-Session-Id")
    if guest_id:
        await _claim_guest_data(db, guest_id, user.id)
        
    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=str(current_user.id), email=current_user.email, created_at=current_user.created_at)
