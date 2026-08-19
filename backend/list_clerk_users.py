"""One-time script to list Clerk users and find/create a test user."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from clerk_backend_api import Clerk

secret = os.environ.get("CLERK_SECRET_KEY")
if not secret:
    print("ERROR: CLERK_SECRET_KEY not set"); sys.exit(1)

client = Clerk(bearer_auth=secret)

# List existing users
result = client.users.list()
print("=== Existing Clerk Users ===")

# Handle both list and paginated response
users = result if isinstance(result, list) else getattr(result, 'data', result)

if not users:
    print("  (none found)")
    print("\nCreating a test user...")
    new_user = client.users.create(request={
        "email_address": ["researchos-test@example.com"],
        "password": "TestPassword123!",
        "skip_password_checks": True,
    })
    print(f"  Created: ID={new_user.id}")
    print(f"\n>>> Add to .env: TEST_CLERK_USER_ID={new_user.id}")
else:
    for u in users:
        emails = u.email_addresses if hasattr(u, 'email_addresses') else []
        email = emails[0].email_address if emails else "no-email"
        print(f"  ID: {u.id}  Email: {email}")
    print(f"\n>>> Suggested: TEST_CLERK_USER_ID={users[0].id}")
