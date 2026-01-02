import json
import random
import os
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]
FERNET_KEY = os.environ["FERNET_KEY"].encode()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
fernet = Fernet(FERNET_KEY)

def handler(request):
    try:
        if not hasattr(request, "body") or not request.body:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "No request body provided"})
            }

        body = json.loads(request.body.decode("utf-8"))
        text = body.get("text")

        if not text:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Text is required"})
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
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "otp": otp,
                "expires_in": "5 minutes"
            })
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Server error: " + str(e)})
        }