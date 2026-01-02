import json
from datetime import datetime
from cryptography.fernet import Fernet
from supabase import create_client
import os

# Supabase client
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"]
)

# Encryption key
fernet = Fernet(os.environ["FERNET_KEY"].encode())

def handler(request):
    body = json.loads(request.body)
    otp = body.get("otp")

    res = supabase.table("notes") \
        .select("id, encrypted_text, expires_at") \
        .eq("otp", otp) \
        .single() \
        .execute()

    if not res.data:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Invalid OTP"})
        }

    expires_at = datetime.fromisoformat(res.data["expires_at"])
    if datetime.utcnow() > expires_at:
        # Delete expired note
        supabase.table("notes").delete().eq("id", res.data["id"]).execute()
        return {
            "statusCode": 410,
            "body": json.dumps({"error": "OTP expired"})
        }

    # Decrypt note
    text = fernet.decrypt(res.data["encrypted_text"].encode()).decode()

    # Delete after reading (one-time retrieval)
    supabase.table("notes").delete().eq("id", res.data["id"]).execute()

    return {
        "statusCode": 200,
        "body": json.dumps({"text": text})
    }
