const logLevel = {
    INFO: "info",
    WARNING: "warning",
    ERROR: "error",
    CRITICAL: "critical"
}

async function sendLog(type, message) {
    try {
        const resp = await fetch('/api/logger', {
            method: "POST",
            headers: {
                "Content-type": "application/json",
            },
            body: JSON.stringify({
                "logger_level": type,
                "logger_message": message
            })
        });
        const msg = await resp.json();
        if (!msg.success) throw new Error(msg.message);
    } catch (err) {
        console.warn("Logger reported failure: " + err);
    }
}

export const Log = {
    info: (msg) => sendLog(logLevel.INFO, msg),
    warning: (msg) => sendLog(logLevel.WARNING, msg),
    error: (msg) => sendLog(logLevel.ERROR, msg),
    critical: (msg) => sendLog(logLevel.CRITICAL, msg),
}
