"""Typer CLI for the warm outreach tracker.

Claude Code invokes this via `python3 -m outreach.cli <cmd>` from within the skill.
Students can also use it directly.
"""
from __future__ import annotations
import json
import sys
from typing import Optional

try:
    import typer
except ImportError:
    print("typer not installed. Run: pip install typer", file=sys.stderr)
    sys.exit(1)

from . import contacts as C
from . import messages as M
from . import followups as F
from .db import init_db

app = typer.Typer(add_completion=False, help="VAIB warm outreach tracker")


@app.command()
def init():
    """Initialize the SQLite database."""
    init_db()
    typer.echo("DB ready.")


@app.command()
def add(
    name: str = typer.Option(..., "--name"),
    how_known: str = typer.Option(..., "--how-known", help="How you actually know this person"),
    platform: Optional[str] = typer.Option(None, "--platform"),
    handle: Optional[str] = typer.Option(None, "--handle"),
    notes: Optional[str] = typer.Option(None, "--notes"),
):
    """Add a warm contact. Refuses obviously-cold entries."""
    try:
        cid = C.add_contact(name, how_known, platform, handle, notes)
    except ValueError as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(1)
    typer.echo(json.dumps({"id": cid, "name": name}))


@app.command("list")
def list_cmd(stage: Optional[str] = typer.Option(None, "--stage")):
    """List contacts, optionally filtered by stage."""
    rows = C.list_contacts(stage)
    if not rows:
        typer.echo("No contacts yet. Run /outreach new to add someone.")
        return
    for r in rows:
        typer.echo(f"[{r['id']}] {r['name']} ({r['platform'] or '?'}) stage={r['stage']} known={r['how_known']}")


@app.command()
def show(contact_id: int):
    """Show a contact + full message thread."""
    c = C.get_contact(contact_id)
    if not c:
        typer.echo(f"Contact {contact_id} not found", err=True)
        raise typer.Exit(1)
    typer.echo(json.dumps(c, indent=2))
    thread = M.get_thread(contact_id)
    typer.echo(f"\n--- Thread ({len(thread)} messages) ---")
    for m in thread:
        arrow = ">>" if m["direction"] == "out" else "<<"
        typer.echo(f"{arrow} [{m['channel']}/{m['status']}] {m['sent_at']}\n   {m['body']}\n")


@app.command()
def log(
    contact_id: int = typer.Option(..., "--contact-id"),
    direction: str = typer.Option(..., "--direction", help="out | in"),
    channel: str = typer.Option(..., "--channel"),
    body: str = typer.Option(..., "--body"),
    status: str = typer.Option("draft", "--status"),
):
    """Log a message (draft, sent, replied)."""
    try:
        mid = M.log_message(contact_id, direction, channel, body, status)
    except ValueError as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(1)
    typer.echo(json.dumps({"message_id": mid}))


@app.command()
def stage(contact_id: int, new_stage: str):
    """Update a contact's stage."""
    try:
        C.update_stage(contact_id, new_stage)
    except ValueError as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Contact {contact_id} -> {new_stage}")


@app.command()
def followup(
    contact_id: int = typer.Option(..., "--contact-id"),
    days: int = typer.Option(3, "--days"),
    note: Optional[str] = typer.Option(None, "--note"),
):
    """Schedule a follow-up."""
    fid = F.schedule(contact_id, days, note)
    typer.echo(json.dumps({"followup_id": fid}))


@app.command()
def due():
    """Show follow-ups due and silent contacts that need a nudge."""
    counts = F.today_counts()
    typer.echo(f"Today: {counts['contacts_added_today']} added, {counts['messages_sent_today']} sent.")
    by_stage = C.count_by_stage()
    if by_stage:
        typer.echo("By stage: " + ", ".join(f"{k}={v}" for k, v in by_stage.items()))

    items = F.due_today()
    typer.echo(f"\n--- Due follow-ups ({len(items)}) ---")
    for i in items:
        typer.echo(f"[{i['contact_id']}] {i['name']} ({i['platform'] or '?'}) due={i['due_at']} note={i['note'] or ''}")

    silent = F.silent_contacts(days=3)
    typer.echo(f"\n--- Silent 3+ days ({len(silent)}) ---")
    for s in silent:
        typer.echo(f"[{s['id']}] {s['name']} ({s['platform'] or '?'}) stage={s['stage']} last_out={s['last_out']}")


@app.command("mark-done")
def mark_done(followup_id: int):
    """Mark a follow-up as completed."""
    F.mark_done(followup_id)
    typer.echo(f"Followup {followup_id} done.")


@app.command("count-today")
def count_today(as_json: bool = typer.Option(False, "--json", help="Emit JSON")):
    """Today's stats vs the Golden 100 target. Used by the SessionStart hook."""
    from datetime import date
    try:
        counts = F.today_counts()
    except Exception:
        counts = {"contacts_added_today": 0, "messages_sent_today": 0}
    payload = {
        "date": date.today().isoformat(),
        "sent_today": counts["messages_sent_today"],
        "added_today": counts["contacts_added_today"],
        "target": 100,
        "warmup_target": 10,
    }
    if as_json:
        typer.echo(json.dumps(payload))
    else:
        typer.echo(f"{payload['sent_today']} / {payload['target']} sent today ({payload['added_today']} new contacts logged)")


@app.command("due-json")
def due_json():
    """Emit today's due follow-ups and silent contacts as JSON. For the SessionStart hook."""
    try:
        due_items = F.due_today()
        silent = F.silent_contacts(days=3)
    except Exception:
        due_items, silent = [], []
    payload = {
        "due": [{"contact_id": i["contact_id"], "name": i["name"], "due_at": i["due_at"], "note": i.get("note")} for i in due_items],
        "silent": [{"id": s["id"], "name": s["name"], "stage": s["stage"], "last_out": s["last_out"]} for s in silent],
    }
    typer.echo(json.dumps(payload))


if __name__ == "__main__":
    app()
