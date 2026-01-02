import json
import random
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from supabase import create_client
import os

def handler(request):
    try:
        SUPABASE_URL = os.environ["SUPABASE_URL"]
        SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]
        FERNET_KEY = os.environ["FERNET_KEY"].encode()

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        fernet = Fernet(FERNET_KEY)

        body = json.loads(request.body)
        text = body.get("text")
        if not text:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Text required"})
            }

        otp = str(random.randint(100000, 999999))
        encrypted_text = fernet.encrypt(text.encode()).decode()
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

        supabase.table("notes").insert({
            "otp": otp,
            "encrypted_text": encrypted_text,
            "expires_at": expires_at
        }).execute()

        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"otp": otp, "expires_in": "5 minutes"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
