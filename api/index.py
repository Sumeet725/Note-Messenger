# api/notes.py
import json
import random
import os
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet
from supabase import create_client

def handler(request):
    try:
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
        FERNET_KEY = os.environ.get("FERNET_KEY")

        if not all([SUPABASE_URL, SUPABASE_KEY, FERNET_KEY]):
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required environment variables"})
            }

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        fernet = Fernet(FERNET_KEY.encode())

        if not request.body:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Empty request body"})
            }

        body = json.loads(request.body.decode("utf-8"))
        text = body.get("text", "").strip()

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
            "body": json.dumps({"error": "Invalid JSON"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Server error: {str(e)}"})
        }