const logLevel = {
    INFO: "info",
    WARNING: "warning",
    ERROR: "error",
    CRITICAL: "critical"
}

async function sendLog(type, message) {
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
    await resp.json()
        .then((msg) => {
            if (!msg.success) console.warn(msg.message);
        })
        .catch((err) => {
            console.warn(err);
        });
    return;
}

export const Log = {
    info: (msg) => sendLog(logLevel.INFO, msg),
    warning: (msg) => sendLog(logLevel.WARNING, msg),
    error: (msg) => sendLog(logLevel.ERROR, msg),
    critical: (msg) => sendLog(logLevel.CRITICAL, msg),
}
