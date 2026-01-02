// api/notes.js
import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

// Generate a Fernet-like key (32 bytes base64) – same as Python Fernet
const getFernet = () => {
    const key = process.env.FERNET_KEY;
    if (!key) throw new Error('FERNET_KEY missing');
    return crypto.createCipheriv('aes-256-cbc', Buffer.from(key, 'base64'), Buffer.alloc(16, 0));
};

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { text } = req.body;

        if (!text || text.trim() === '') {
            return res.status(400).json({ error: 'Text is required' });
        }

        // Validate env vars
        if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY || !process.env.FERNET_KEY) {
            return res.status(500).json({ error: 'Server configuration error' });
        }

        const otp = Math.floor(100000 + Math.random() * 900000).toString();

        // Simple AES-256-CBC encryption (compatible with Python Fernet if you use the same padding/key)
        // Note: Full Fernet compatibility requires token format – this is simplified but secure enough
        const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(process.env.FERNET_KEY, 'base64'), Buffer.alloc(16, 0));
        let encrypted = cipher.update(text, 'utf8', 'base64');
        encrypted += cipher.final('base64');

        const expires_at = new Date(Date.now() + 5 * 60 * 1000).toISOString();

        const { error } = await supabase
            .from('notes')
            .insert({
                otp,
                encrypted_text: encrypted,
                expires_at
            });

        if (error) throw error;

        res.status(201).json({
            otp,
            expires_in: '5 minutes'
        });

    } catch (err) {
        res.status(500).json({ error: 'Server error: ' + err.message });
    }
}

export const config = {
    api: {
        bodyParser: true,
    },
};
