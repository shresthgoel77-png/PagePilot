"""Dev-only router for creating Clerk sign-in tokens for E2E testing.
Only available when BYPASS_CLERK=true. Returns 404 otherwise."""
import logging
import os
from fastapi import APIRouter, HTTPException

logger = logging.getLogger("researchos.dev_auth")

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/create-test-session")
async def create_test_session():
    """Generate a one-time Clerk sign-in token for the test user.
    This uses Clerk's official sign_in_tokens API."""
    from app.core.config import settings

    if not settings.BYPASS_CLERK:
        raise HTTPException(status_code=404, detail="Not found")

    test_user_id = settings.TEST_CLERK_USER_ID
    if not test_user_id:
        raise HTTPException(
            status_code=500,
            detail="TEST_CLERK_USER_ID not set in environment",
        )

    try:
        from app.core.clerk_auth import clerk_client

        result = clerk_client.sign_in_tokens.create(
            request={"user_id": test_user_id}
        )
        token = result.token if hasattr(result, "token") else str(result)
        logger.info(f"Dev: Created sign-in token for test user {test_user_id}")
        return {"token": token}
    except Exception as e:
        logger.error(f"Dev: Failed to create sign-in token: {e}")
        raise HTTPException(status_code=500, detail=f"Clerk API error: {e}")
