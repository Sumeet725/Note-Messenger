// api/notes/retrieve.js
import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { otp } = req.body;

        if (!otp || otp.trim() === '') {
            return res.status(400).json({ error: 'OTP is required' });
        }

        if (!process.env.FERNET_KEY) {
            return res.status(500).json({ error: 'Server configuration error' });
        }

        const { data, error } = await supabase
            .from('notes')
            .select('id, encrypted_text, expires_at')
            .eq('otp', otp)
            .single();

        if (error || !data) {
            return res.status(404).json({ error: 'Invalid or unknown OTP' });
        }

        const expires_at = new Date(data.expires_at);
        if (new Date() > expires_at) {
            await supabase.from('notes').delete().eq('id', data.id);
            return res.status(410).json({ error: 'OTP has expired' });
        }

        // Decrypt
        const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(process.env.FERNET_KEY, 'base64'), Buffer.alloc(16, 0));
        let text = decipher.update(data.encrypted_text, 'base64', 'utf8');
        text += decipher.final('utf8');

        // Burn after reading
        await supabase.from('notes').delete().eq('id', data.id);

        res.status(200).json({ text });

    } catch (err) {
        res.status(500).json({ error: 'Server error: ' + err.message });
    }
}

export const config = {
    api: {
        bodyParser: true,
    },
};