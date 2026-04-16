from typing import Optional
from .db import connect

VALID_CHANNELS = {"linkedin", "instagram", "sms", "whatsapp", "email", "phone", "facebook", "telegram", "other"}
VALID_DIRECTIONS = {"out", "in"}
VALID_STATUSES = {"draft", "sent", "replied", "ignored"}


def log_message(
    contact_id: int,
    direction: str,
    channel: str,
    body: str,
    status: str = "draft",
) -> int:
    if direction not in VALID_DIRECTIONS:
        raise ValueError(f"direction must be one of {VALID_DIRECTIONS}")
    if channel not in VALID_CHANNELS:
        raise ValueError(f"channel must be one of {VALID_CHANNELS}")
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {VALID_STATUSES}")
    if not body.strip():
        raise ValueError("body required")
    conn = connect()
    cur = conn.execute(
        "INSERT INTO messages (contact_id, direction, channel, body, status) VALUES (?, ?, ?, ?, ?)",
        (contact_id, direction, channel, body.strip(), status),
    )
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    return mid


def get_thread(contact_id: int) -> list[dict]:
    conn = connect()
    rows = conn.execute(
        "SELECT * FROM messages WHERE contact_id = ? ORDER BY sent_at ASC", (contact_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_status(message_id: int, status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {VALID_STATUSES}")
    conn = connect()
    conn.execute("UPDATE messages SET status = ? WHERE id = ?", (status, message_id))
    conn.commit()
    conn.close()


def last_outbound(contact_id: int) -> Optional[dict]:
    conn = connect()
    row = conn.execute(
        "SELECT * FROM messages WHERE contact_id = ? AND direction = 'out' ORDER BY sent_at DESC LIMIT 1",
        (contact_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
