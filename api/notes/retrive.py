# api/notes/retrieve.py
import json
import os
from datetime import datetime, timezone
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
        otp = body.get("otp", "").strip()

        if not otp:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "OTP is required"})
            }

        res = supabase.table("notes") \
            .select("id", "encrypted_text", "expires_at") \
            .eq("otp", otp) \
            .single() \
            .execute()

        if not res.data:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid or unknown OTP"})
            }

        note = res.data
        expires_at = datetime.fromisoformat(note["expires_at"].replace("Z", "+00:00"))

        if datetime.now(timezone.utc) > expires_at:
            supabase.table("notes").delete().eq("id", note["id"]).execute()
            return {
                "statusCode": 410,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "OTP has expired"})
            }

        text = fernet.decrypt(note["encrypted_text"].encode()).decode()

        supabase.table("notes").delete().eq("id", note["id"]).execute()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"text": text})
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