import { decryptString } from "./cryptoTools.js";

async function decodeTokenToUserName(token) {
    if (!token) return null;
    try {
        const resp = await fetch('/api/peek_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token }),
        });
        const data = await resp.json();
        if (!data.success) return null;
        const uname = decryptString(data.var, data.key, data.iv);
        return uname || null;
    } catch (e) {
        console.error(e);
        return null;
    }
}

export { decodeTokenToUserName };