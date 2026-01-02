import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_ANON_KEY
);

export default async function handler(req, res) {
    if (req.method !== "POST") {
        return res.status(405).json({ error: "Method not allowed" });
    }

    const { otp } = req.body;
    if (!otp) return res.status(400).json({ error: "OTP required" });

    const { data, error } = await supabase
        .from("notes")
        .select("*")
        .eq("otp", otp)
        .single();

    if (error || !data) {
        return res.status(404).json({ error: "Invalid OTP" });
    }

    if (new Date() > new Date(data.expires_at)) {
        await supabase.from("notes").delete().eq("id", data.id);
        return res.status(410).json({ error: "OTP expired" });
    }

    await supabase.from("notes").delete().eq("id", data.id);
    res.status(200).json({ text: data.encrypted_text });
}
