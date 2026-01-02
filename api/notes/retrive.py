import json
import os
from datetime import datetime, timezone
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
        otp = body.get("otp")

        if not otp:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "OTP is required"})
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
                "body": json.dumps({"error": "Invalid or unknown OTP"})
            }

        expires_at = datetime.fromisoformat(res.data["expires_at"].replace("Z", "+00:00"))

        if datetime.now(timezone.utc) > expires_at:
            supabase.table("notes").delete().eq("id", res.data["id"]).execute()
            return {
                "statusCode": 410,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "OTP has expired"})
            }

        text = fernet.decrypt(res.data["encrypted_text"].encode()).decode()

        supabase.table("notes").delete().eq("id", res.data["id"]).execute()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"text": text})
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