import { createClient } from "@supabase/supabase-js";
import crypto from "crypto";

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
);

export default async function handler(req, res) {
    if (req.method !== "POST") {
        return res.status(405).json({ error: "Method not allowed" });
    }

    const { text } = req.body;
    if (!text) {
        return res.status(400).json({ error: "Text required" });
    }

    const otp = crypto.randomInt(100000, 999999).toString();
    const expiresAt = new Date(Date.now() + 5 * 60 * 1000).toISOString();

    const encryptedText = Buffer.from(text).toString("base64");

    await supabase.from("notes").insert([{
        otp,
        encrypted_text: encryptedText,
        expires_at: expiresAt
    }]);

    res.status(201).json({
        otp,
        expires_in: "5 minutes"
    });
}
