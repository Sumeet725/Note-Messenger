import json, os, random
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from supabase import create_client

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"]
)

fernet = Fernet(os.environ["FERNET_KEY"].encode())

def handler(request):
    body = json.loads(request.body.decode("utf-8"))
    text = body["text"]

    otp = str(random.randint(100000, 999999))
    encrypted = fernet.encrypt(text.encode()).decode()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

    supabase.table("notes").insert({
        "otp": otp,
        "encrypted_text": encrypted,
        "expires_at": expires_at
    }).execute()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"otp": otp})
    }
