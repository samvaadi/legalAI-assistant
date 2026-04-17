CREATE TABLE IF NOT EXISTS default.chat_logs (
    session_id STRING,
    title STRING,
    role STRING,
    content STRING,
    ts TIMESTAMP
)
USING DELTA;