import json
import random
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from supabase import create_client
import os

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"]
)

fernet = Fernet(os.environ["FERNET_KEY"].encode())

def handler(request):
    try:
        body = json.loads(request.get_data().decode())
    except:
        body = {}

    text = body.get("text")
    if not text:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Text required"})
        }

    otp = str(random.randint(100000, 999999))
    encrypted = fernet.encrypt(text.encode()).decode()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

    supabase.table("notes").insert({
        "otp": otp,
        "encrypted_text": encrypted,
        "expires_at": expires_at
    }).execute()

    return {
        "statusCode": 201,
        "body": json.dumps({"otp": otp, "expires_in": "5 minutes"})
    }
