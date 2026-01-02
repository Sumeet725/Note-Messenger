import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_ANON_KEY
);

export default async function handler(req, res) {
    if (req.method !== "POST") {
        return res.status(405).json({ error: "Method not allowed" });
    }

    const { text } = req.body;
    if (!text) return res.status(400).json({ error: "Text required" });

    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    const expires_at = new Date(Date.now() + 5 * 60 * 1000).toISOString();

    const { error } = await supabase.from("notes").insert({
        otp,
        encrypted_text: text, // encryption optional
        expires_at
    });

    if (error) return res.status(500).json({ error: error.message });

    res.status(201).json({ otp });
}
