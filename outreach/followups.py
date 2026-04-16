from datetime import datetime, timedelta
from typing import Optional
from .db import connect


def schedule(contact_id: int, due_in_days: int = 3, note: Optional[str] = None) -> int:
    due_at = (datetime.utcnow() + timedelta(days=due_in_days)).isoformat(timespec="seconds")
    conn = connect()
    cur = conn.execute(
        "INSERT INTO followups (contact_id, due_at, note) VALUES (?, ?, ?)",
        (contact_id, due_at, note),
    )
    conn.commit()
    fid = cur.lastrowid
    conn.close()
    return fid


def due_today() -> list[dict]:
    now = datetime.utcnow().isoformat(timespec="seconds")
    conn = connect()
    rows = conn.execute(
        """
        SELECT f.id, f.contact_id, f.due_at, f.note, c.name, c.platform, c.stage, c.how_known
        FROM followups f
        JOIN contacts c ON c.id = f.contact_id
        WHERE f.completed = 0 AND f.due_at <= ?
        ORDER BY f.due_at ASC
        """,
        (now,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def silent_contacts(days: int = 3) -> list[dict]:
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat(timespec="seconds")
    conn = connect()
    rows = conn.execute(
        """
        SELECT c.id, c.name, c.platform, c.stage, c.how_known,
               (SELECT MAX(sent_at) FROM messages WHERE contact_id = c.id AND direction = 'out') AS last_out,
               (SELECT MAX(sent_at) FROM messages WHERE contact_id = c.id AND direction = 'in') AS last_in
        FROM contacts c
        WHERE c.stage IN ('messaged', 'replied', 'demo_sent')
        """
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        if d["last_out"] and (not d["last_in"] or d["last_in"] < d["last_out"]):
            if d["last_out"] <= cutoff:
                out.append(d)
    return out


def mark_done(followup_id: int) -> None:
    conn = connect()
    conn.execute("UPDATE followups SET completed = 1 WHERE id = ?", (followup_id,))
    conn.commit()
    conn.close()


def today_counts() -> dict:
    today = datetime.utcnow().date().isoformat()
    conn = connect()
    added = conn.execute("SELECT COUNT(*) AS n FROM contacts WHERE DATE(added_at) = ?", (today,)).fetchone()["n"]
    sent = conn.execute(
        "SELECT COUNT(*) AS n FROM messages WHERE DATE(sent_at) = ? AND direction = 'out' AND status = 'sent'",
        (today,),
    ).fetchone()["n"]
    conn.close()
    return {"contacts_added_today": added, "messages_sent_today": sent}
