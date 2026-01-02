import json, os
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from supabase import create_client

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"]
)

fernet = Fernet(os.environ["FERNET_KEY"].encode())

def handler(request):
    body = json.loads(request.body.decode("utf-8"))
    otp = body["otp"]

    res = supabase.table("notes") \
        .select("id, encrypted_text, expires_at") \
        .eq("otp", otp) \
        .single() \
        .execute()

    note = res.data
    expires_at = datetime.fromisoformat(note["expires_at"].replace("Z", "+00:00"))

    if datetime.now(timezone.utc) > expires_at:
        supabase.table("notes").delete().eq("id", note["id"]).execute()
        return {"statusCode": 410, "body": "Expired"}

    text = fernet.decrypt(note["encrypted_text"].encode()).decode()
    supabase.table("notes").delete().eq("id", note["id"]).execute()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"text": text})
    }
