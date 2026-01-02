import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
);

export default async function handler(req, res) {
    if (req.method !== "POST") {
        return res.status(405).json({ error: "Method not allowed" });
    }

    const { otp } = req.body;
    if (!otp) {
        return res.status(400).json({ error: "OTP required" });
    }

    const { data } = await supabase
        .from("notes")
        .select("*")
        .eq("otp", otp)
        .single();

    if (!data) {
        return res.status(404).json({ error: "Invalid OTP" });
    }

    if (new Date(data.expires_at) < new Date()) {
        return res.status(410).json({ error: "OTP expired" });
    }

    // decode
    const text = Buffer.from(data.encrypted_text, "base64").toString("utf-8");

    // one-time read
    await supabase.from("notes").delete().eq("otp", otp);

    res.status(200).json({ text });
}
