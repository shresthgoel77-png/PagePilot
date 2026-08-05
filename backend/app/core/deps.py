from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import uuid
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User

# Localized explicitly capturing Bearer tokens logically validating
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id_str: str | None = payload.get("sub")
            if user_id_str is None:
                raise credentials_exception
            user_id = uuid.UUID(user_id_str)
        except (JWTError, ValueError):
            raise credentials_exception
            
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
            
        return user
        
    guest_id = request.headers.get("X-Guest-Session-Id")
    if guest_id:
        try:
            guest_uuid = uuid.UUID(guest_id)
        except ValueError:
            raise credentials_exception
            
        stmt = select(User).where(User.id == guest_uuid)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user and user.is_guest:
            return user
            
        # Create shadow guest user
        new_guest = User(
            id=guest_uuid,
            email=f"guest_{guest_uuid}@researchos.guest",
            hashed_password="guest",
            is_guest=True
        )
        db.add(new_guest)
        try:
            await db.commit()
            await db.refresh(new_guest)
            return new_guest
        except IntegrityError:
            await db.rollback()
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            if user and user.is_guest:
                return user
            raise credentials_exception

    raise credentials_exception
