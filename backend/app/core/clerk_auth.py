import logging
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from clerk_backend_api import Clerk
from clerk_backend_api.security import AuthenticateRequestOptions
import uuid
import os

from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger("researchos.auth")

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
        logger.warning(f"Auth: Missing or malformed Authorization header on {request.method} {request.url.path}")
        raise credentials_exception
        
    token = auth_header.split(' ')[1]
    
    try:
        from app.core.config import settings
        if token == "MOCK_TOKEN" and settings.BYPASS_CLERK:
            clerk_id = "mock_clerk_id"
            email = "mock@example.com"
            logger.info(f"Auth: MOCK_TOKEN verified clerk_id={clerk_id} on {request.method} {request.url.path}")
        else:
            # Use Clerk client to verify the JWT
            token_payload = clerk_client.authenticate_request(request, AuthenticateRequestOptions())
            if not token_payload.is_signed_in:
                logger.warning(f"Auth: Token not signed in on {request.method} {request.url.path}")
                raise credentials_exception
                
            clerk_id = token_payload.payload.get('sub')
            email = token_payload.payload.get('email', f"clerk_{clerk_id}@researchos.user")
            logger.info(f"Auth: Verified clerk_id={clerk_id} on {request.method} {request.url.path}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth: Token verification failed on {request.method} {request.url.path}: {type(e).__name__}: {e}")
        raise credentials_exception
        
    stmt = select(User).where(User.clerk_id == clerk_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        return user
        
    # Create JIT user on first invocation
    new_user = User(
        id=uuid.uuid4(),
        email=email,
        clerk_id=clerk_id
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        logger.info(f"Auth: Created new user for clerk_id={clerk_id}")
        return new_user
    except IntegrityError:
        await db.rollback()
        # Fallback in case of race condition
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return user
        raise credentials_exception
