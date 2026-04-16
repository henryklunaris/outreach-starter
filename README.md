# VAIB Warm Outreach Starter

The only warm outreach workflow you need for [VAIB](https://voiceaibootcamp.com/)

## What this does

You attach a screenshot of someone you know (LinkedIn profile, Instagram, wherever) or yap about them briefly. Claude Code:

1. Asks how you actually know them (hard gate, blocks cold-outreach leaks).
2. Generates a tailored first message using the ACA framework (Acknowledge, Compliment, Ask).
3. Formats it correctly for your channel (LinkedIn, Instagram, SMS, WhatsApp, email, phone, Facebook).
4. Saves the contact and draft to a local SQLite database.
5. Reminds you when to follow up.

This is for your warm audience only.

## Prerequistes:

Have Claude Code installed. Can watch the set up guide: [click here](https://youtu.be/hlCfoUj9GlA)

## Install (90 seconds)

```bash
git clone <this-repo> outreach-starter
cd outreach-starter
claude
```

First time only, in Claude Code type:

```
/activate
```

On the very first run, `/activate` automatically runs `./setup.sh` for you (installs the Python dependency, initializes the local SQLite tracker). Then it kicks into the interview: about 10 minutes, capturing your writing style, the channels you actually use, three tiers of relationship closeness (best mate vs friend vs old acquaintance). Saves a local profile so drafts sound like you.

Then, still on the first run:

```
/mindset
```

A separate back-and-forth. Goes through the three mindset breaks the VAIB method rests on, plus a few pressure-test scenarios. Pushes back if your answer doesn't line up with how the method actually works, the point is to hear yourself say the right thing in your own words. Saves your answers so the daily accountability nudge can echo them back to you.

If you'd rather run setup manually, `./setup.sh` still works standalone.

Then for daily use:

```
/outreach
```

Attach a screenshot or describe who you want to reach out to. Claude does the rest.

## How to use it

Just type `/outreach` and then say what you need. It routes automatically:


| Say this                                                            | What happens                               |
| ------------------------------------------------------------------- | ------------------------------------------ |
| `/outreach` + attach a profile screenshot                           | Adds the contact and drafts first messages |
| `/outreach` + "help me message my cousin Joe, he just got promoted" | Same, but from text instead of an image    |
| `/outreach` + "list my contacts"                                    | Shows everyone in your tracker             |
| `/outreach` + "what's due today"                                    | Today's follow-ups + Golden 100 progress   |
| `/outreach` + "I sent the message to Jake, he replied with X"       | Logs the exchange, suggests next step      |
| `/outreach` + "what should I say next to Amy"                       | Pulls the thread, recommends next move     |


If you ask a question like "what do I do when someone views the demo but doesn't reply" or "I only know 20 people, is this worth it", Claude will auto-load the `/coach` skill and answer from the knowledge base. You can also invoke it directly as `/coach`.

## Daily accountability

Every time you open `claude` in this repo, a SessionStart hook prints a quick nudge: your count toward the Golden 100 today, top follow-ups due, and one of your own mindset commitments from `/activate`. You can ignore it. It's there so the thing you told yourself yesterday doesn't quietly disappear today.

## Direct CLI (optional)

You can also drive the tracker directly without Claude:

```bash
python3 -m outreach.cli add --name "Jake" --how-known "uni friend" --platform linkedin --handle "@jakeh"
python3 -m outreach.cli list
python3 -m outreach.cli due
python3 -m outreach.cli show 1
```

## The Rules (read once, then never forget)

1. **Warm = they know your name.** LinkedIn connections you've never spoken to are not warm.
2. **First 10 contacts = warm-up ritual. Then Golden 100 per day** until discovery calls are booked.
3. **First message is a catchup.** Never mention voice AI, the agency, or the offer in message 1. Later messages are conversation + showing what you do if they ask.
4. **No pitching, ever.** The only two legitimate actions are showing off what you do (when they ask) and asking for a referral.
5. **No niches in warm outreach.** Every person is different. Niche-picking is a stall tactic, go talk to people.
6. **Copy, edit, send manually.** Claude drafts. You send. The tool doesn't have send power.

## The Goal

2-4 weeks to 3 discovery calls. Book the calls, do the discovery properly (see `.claude/skills/outreach/reference/sales-principles.md`), close from there.

## Why this exists

83% of people say the real blocker isn't knowing what to say, it's the awkwardness of actually pressing send. This starter removes the drafting friction and reinforces the three mindsets daily.

## Database

The names and messages are tracked in a local SQLite DB.