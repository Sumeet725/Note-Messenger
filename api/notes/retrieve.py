import json
from datetime import datetime, timezone
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
        otp = body.get("otp")
        if not otp:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "OTP required"})
            }

        res = supabase.table("notes") \
            .select("id, encrypted_text, expires_at") \
            .eq("otp", otp) \
            .single() \
            .execute()

        if not res.data:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid OTP"})
            }

        expires_at = datetime.fromisoformat(res.data["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            supabase.table("notes").delete().eq("id", res.data["id"]).execute()
            return {
                "statusCode": 410,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "OTP expired"})
            }

        text = fernet.decrypt(res.data["encrypted_text"].encode()).decode()
        supabase.table("notes").delete().eq("id", res.data["id"]).execute()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"text": text})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
