def handler(request):
    try:
        body = json.loads(request.body.decode("utf-8")) 
        text = body.get("text")
        if not text:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Text required"})
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
            "body": json.dumps({"otp": otp, "expires_in": "5 minutes"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
