import json
from datetime import datetime, timezone
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

    otp = body.get("otp")
    if not otp:
        return {"statusCode": 400, "body": json.dumps({"error": "OTP required"})}

    res = supabase.table("notes") \
        .select("id, encrypted_text, expires_at") \
        .eq("otp", otp) \
        .single() \
        .execute()

    if not res.data:
        return {"statusCode": 404, "body": json.dumps({"error": "Invalid OTP"})}

    expires_at = datetime.fromisoformat(res.data["expires_at"]).replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        supabase.table("notes").delete().eq("id", res.data["id"]).execute()
        return {"statusCode": 410, "body": json.dumps({"error": "OTP expired"})}

    text = fernet.decrypt(res.data["encrypted_text"].encode()).decode()

    supabase.table("notes").delete().eq("id", res.data["id"]).execute()

    return {"statusCode": 200, "body": json.dumps({"text": text})}
