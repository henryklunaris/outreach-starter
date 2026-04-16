from typing import Optional
from .db import connect

VALID_STAGES = {"new", "messaged", "replied", "demo_sent", "discovery_booked", "closed", "dead"}
COLD_PHRASES = {
    "linkedin connection",
    "don't know them",
    "dont know them",
    "found their profile",
    "saw their post",
    "random",
    "stranger",
    "cold lead",
    "off google",
    "scraped",
}


def looks_cold(how_known: str) -> bool:
    h = how_known.lower().strip()
    if len(h) < 4:
        return True
    return any(p in h for p in COLD_PHRASES)


def add_contact(
    name: str,
    how_known: str,
    platform: Optional[str] = None,
    handle: Optional[str] = None,
    notes: Optional[str] = None,
) -> int:
    if not name.strip():
        raise ValueError("name required")
    if not how_known.strip():
        raise ValueError("how_known required (how do you actually know this person?)")
    if looks_cold(how_known):
        raise ValueError(
            f"'{how_known}' looks like a cold contact. This skill is warm-only. Not supported."
        )
    conn = connect()
    cur = conn.execute(
        "INSERT INTO contacts (name, how_known, platform, handle, notes) VALUES (?, ?, ?, ?, ?)",
        (name.strip(), how_known.strip(), platform, handle, notes),
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid


def list_contacts(stage: Optional[str] = None) -> list[dict]:
    conn = connect()
    if stage:
        rows = conn.execute("SELECT * FROM contacts WHERE stage = ? ORDER BY added_at DESC", (stage,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM contacts ORDER BY added_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_contact(contact_id: int) -> Optional[dict]:
    conn = connect()
    row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_stage(contact_id: int, stage: str) -> None:
    if stage not in VALID_STAGES:
        raise ValueError(f"stage must be one of {VALID_STAGES}")
    conn = connect()
    conn.execute("UPDATE contacts SET stage = ? WHERE id = ?", (stage, contact_id))
    conn.commit()
    conn.close()


def count_by_stage() -> dict:
    conn = connect()
    rows = conn.execute("SELECT stage, COUNT(*) as n FROM contacts GROUP BY stage").fetchall()
    conn.close()
    return {r["stage"]: r["n"] for r in rows}
