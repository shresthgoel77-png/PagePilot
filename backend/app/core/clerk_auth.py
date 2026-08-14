from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from clerk_backend_api import Clerk
import uuid
import os

from app.db.session import get_db
from app.models.user import User

CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY")
if not CLERK_SECRET_KEY:
    raise RuntimeError("CLERK_SECRET_KEY environment variable is missing. Clerk authentication cannot be configured.")
clerk_client = Clerk(bearer_auth=CLERK_SECRET_KEY)

async def get_current_user_clerk(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise credentials_exception
        
    token = auth_header.split(' ')[1]
    
    try:
        # Use Clerk client to verify the JWT
        token_payload = clerk_client.authenticate_request(request)
        if not token_payload.is_signed_in:
            raise credentials_exception
            
        clerk_id = token_payload.payload.get('sub')
        email = token_payload.payload.get('email', f"clerk_{clerk_id}@researchos.user")
    except Exception as e:
        print(f"Token validation fault cleanly constrained: {e}")
        raise credentials_exception
        
    stmt = select(User).where(User.clerk_id == clerk_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        return user
        
    # Create JIT user on first invocation naturally
    new_user = User(
        id=uuid.uuid4(),
        email=email,
        clerk_id=clerk_id
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        # Fallback in case of race condition structurally
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return user
        raise credentials_exception
