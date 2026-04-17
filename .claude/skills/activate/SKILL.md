---
name: activate
description: One-time onboarding. Use when the user types /activate, typically on first clone of this repo. Captures their writing voice, which channels they use for warm outreach, and three tiers of relationship closeness, then persists a profile at .claude/state/user-profile.json that /outreach reads when drafting. Also use if they say "redo activate", "reset my profile", or "update my voice".
disable-model-invocation: true
---

# /activate Skill

The user invokes this skill by typing `/activate`. It runs once on first clone, then only again if they want to update.

Your job: interview them in a chill, low-friction way, pull out a voice fingerprint and 3 tiers of relationship tone, save it to `.claude/state/user-profile.json`, and hand off to `/outreach`.

Every future `/outreach` draft will read this file. Garbage in, garbage out. Take it seriously but keep it casual.

## Pre-flight: repo setup

Before the routing check, make sure the repo is actually ready to use:

1. Check if `outreach.db` exists in the repo root. If it does, the student has already bootstrapped, skip to Routing.
2. If `outreach.db` is missing, this is a fresh clone. Tell them one line: "first run, setting up local tracker, takes about 10 seconds" and run `./setup.sh` in a single bash call. That script installs the Python `typer` dependency (idempotent) and initializes the SQLite schema. It's safe to re-run.
3. Only after setup completes, continue to Routing.

Don't make a big deal of the setup step, it's just plumbing. If `./setup.sh` fails for any reason (no Python, network issue, permission error), show the error to the user verbatim and stop, they'll need to debug their env before the skill can proceed.

## Hard rules while running this skill

- Do NOT generate any outreach messages from inside `/activate`. That's `/outreach`'s job.
- Do NOT use em dashes in anything you write to the user or to the file. Use commas, periods, or restructure. Ever.
- Do NOT make up sample messages on behalf of the user. If they don't give you samples, the fingerprint is thinner, fine, but don't fabricate.
- Do NOT save the profile until you've shown the user the extracted fingerprint and they've confirmed or tweaked it.
- **Do NOT announce section headers to the user.** The section headings below (intro, channels, voice samples, etc.) are routing labels for you, not headings for them. The interview should feel like one chill conversation that flows from one question to the next. Use transitions like "cool, next one" or "alright", not "okay, voice samples section".
- **Privacy rule, hard.** Do NOT store real contact names, phone numbers, addresses, workplace names, or any other private detail in the saved profile. When the user pastes a WhatsApp export or real samples, extract STYLE only. Any sample you save back to the profile must have proper nouns replaced with generic placeholders (`[name]`, `[place]`, `[company]`). Never store the raw chat file. The thing is that since they are writing to Claude Code, it means that the conversation is still mostly likely stored somewhere in Anthropics server so explain that, as we don't do any major compliance set ups here.
- **Voice rule for the interview itself.** The messages YOU send to the user during this interview should be polished casual English in sentence case ("Alright, what's your first name?"). Do NOT mimic lowercase / all-casual style in your own messages. Lowercase/handwritten style is reserved for OUTREACH DRAFTS in `/outreach`, which adapt to the user's voice profile. The interview is your voice, not theirs, keep it tidy.

## Primer (always show on a fresh setup)

Before running the interview on a fresh setup (no existing profile), show a short primer so the user knows what's coming and can prep examples in one pass instead of grabbing things mid-interview. Keep it tight, four lines max:

> "Alright, quick heads-up this should take about 10 minutes. The goal of this whole set up is to help you do warm outreach.
>
> I'm about to ask you a few questions thats will help me write outreach messages that sound like you.
>
> Privacy note: this is NOT a privacy compliant set up, the conversations are most likely sent to Anthropics servers since we're using Claude Code. So, it up to you, the user, to decide what info you want to provide. 
>
>Do you accept?

Wait for them to confirm (a postivie response like "yep" / "go" / "ready" is fine). If, no then tell them you can't help them.

**Skip the primer** if routing detected an existing profile (user is updating a specific section or rebuilding and already knows the drill).

## Routing (do this first)

Check if `.claude/state/user-profile.json` already exists (`Read` the path, catch the error).

- **File missing** → this is a fresh setup, run the full interview starting with the intro.
- **File exists** → don't overwrite silently. Show a one-line summary (name, primary channels, activated_at) and ask:
  > "Looks like you already activated. Want to:
  >(1) see what's saved
  >(2) update just one section
  >(3) rebuild from scratch?"
  - **(1) see**: pretty-print the JSON back to them, stop.
  - **(2) update**: ask which section (intro, channels, voice, tiers, avoid, mindset), run just that section, re-extract affected fields, show diff, save.
  - **(3) rebuild**: start fresh from the intro. Keep the existing file in memory so you can show a diff at the end, but overwrite on save.

## The Interview

Read `reference/voice-interview.md` for exact phrasing and extraction tips. Read `reference/tone-tiers.md` for the relationship model.

Do the sections in order. One section per turn, not all at once. Wait for their answer before moving on. Each section should feel like one line of text from a friend, not a form. Never announce section names to the user.

### Intro

Get:
- First name.
- One sentence of what they're up to (this becomes their Stage-1 info-funnel answer later).

> "Alright, quick intro. What's your first name, and in one chill sentence, what are you actually up to or your goal in the AI space? 
>The one-sentence answer you'd give someone at a BBQ if they asked what you do."

If they give you LinkedIn-voice ("I leverage AI to empower small businesses..."), gently ask them to retry it the way they'd say it to a mate. This field matters because it gets recycled when warm contacts ask "so what are you up to?".

### Channels

From the full list, which do they actually use with friends/family? Split into `primary` (top 2-3 where most of their warm outreach will happen) and `occasional`.

Full list: `linkedin`, `instagram`, `sms`, `whatsapp`, `email`, `facebook_messenger`, `phone`, `voice_note`.

> "Which of these do you actually use to message friends and family? Pick your top 2-3 (primary), and any others you use sometimes (occasional)."

Anything not named is `not_used`. Don't nag, just record it.

### Voice samples

For each channel in `primary`, ask them to paste 3-5 recent real messages they sent to friends or family. Boring ones. Not things they wrote trying to sound cool.

> "For [channel], paste me 3-5 messages you've actually sent to close friends or family recently. Boring ones are perfect, confirming a time, asking how they are, replying to a photo."

Do one channel at a time. If they paste 1-2 and move on, that's fine, don't gate.

**WhatsApp shortcut.** If WhatsApp is one of their primary channels, offer the export path, it produces a much stronger voice fingerprint than pasting 5 messages manually:

> "Quick tip for WhatsApp, you can export a full chat as a .txt file instead of pasting messages one at a time. Pick a thread with a friend or family member, in the chat tap the contact name at the top, scroll down to 'Export Chat', choose 'Without Media'. Email it to yourself or AirDrop it, then drop the file in here. I'll extract your writing style only, not the actual content, so the other person's messages stay private."

If they export a chat, read the file, parse out lines where they are the sender. The exported format is `[timestamp] Name: message`, their own messages will all have the same Name, ask them which name is theirs if it's not obvious. Extract STYLE signals (see Extraction section below) from their messages. Do NOT store the raw file. Do NOT store the other person's messages at all. Only hold up to 5 of their OWN messages as anonymized illustrative samples, and only after stripping out all proper nouns.

For other channels (iMessage, Instagram, LinkedIn, Facebook Messenger), clean native exports either don't exist or are painful bulk ZIPs, stick with manual paste.

**Do NOT save `raw_samples_by_channel`.** That field has been removed for privacy. Extract the style fingerprint and keep at most 5 short sanitized illustrative lines per primary channel (proper nouns replaced with `[name]`, `[place]`, etc., and only use samples that are 80% generic content you'd be fine showing anyone).

### Relationship tiers

Three tiers: `close`, `friend`, `acquaintance`. Definitions in `reference/tone-tiers.md`.

For each tier, ask for:
- A short description of who fits (generic role, not a real name, e.g. "best mate, sibling, partner", not "Jannis, my sister Emma").
- One sample message they'd realistically send to someone at that tier.

> "Now three tiers of closeness. First, someone really close to you, best mate, sibling, partner. What's a message you'd actually send someone like that on any normal day?"

Then `friend`, then `acquaintance`. Keep prompts short, don't lecture on the tier definitions unless they ask.

**Privacy before saving.** When storing the tier description, keep the role category (e.g. "best mate, sibling, partner") and strip any actual names the user mentioned. When storing the sample message, replace proper nouns with `[name]` / `[place]`. Goal: the profile could be shown to a stranger without leaking who the user knows.

### Avoid list

> "Any words or phrases you'd never actually say? Stuff that makes you cringe when you see other people write it? Things like 'reached out', 'hope this finds you well', 'synergy', whatever your version is."

Store as a flat array of strings.

### Availability

Real talk: the Golden 100 target is aspirational, not everyone can hit it from day one. Someone with a 9-5 and kids has a different ceiling than a student with open evenings. Capture the reality so the tool can set realistic expectations.

> "One more practical one. Roughly how much time per day can you realistically spend on outreach? Be honest, could be 20 minutes over coffee, an hour in the evening after the kids are down, just weekends, whatever the real picture is."

Follow up once if the answer is vague:

> "And when's that usually? Morning before work, lunch, evenings, weekends only? Helps me understand when you'll be in this."

Store as:
```json
"availability": {
  "daily_minutes": 30,
  "best_window": "evenings after 8pm",
  "notes": "work full time + 2 kids, weekends are better"
}
```

Map `daily_minutes` from their answer:
- "20 minutes", "half hour" → 30
- "an hour" → 60
- "an hour or two" → 90
- "a couple hours" → 120
- "most of the afternoon" → 180
- "weekends only" → store 0 for daily, note the weekend pattern in `notes`

Don't gate them into picking a number. If they give a story, capture it verbatim in `notes` and your best-effort number guess in `daily_minutes`.

**How this gets used**: the Golden 100 target stays as the aspiration (for when they're in push mode toward discovery calls). But the daily realistic ceiling is `daily_minutes` at roughly 1-2 messages per minute. `/outreach` BRAINSTORM mode and the SessionStart hook use this to set honest expectations, e.g. "30 minutes today means a realistic 30-45 messages, not 100". Doctrine isn't changed, but the ramp is.

## Extraction

Once you have their raw answers across all sections, build the `voice` object. Pull signal, don't guess.

**Before extracting or saving ANY sample text, strip proper nouns.** Replace real first names, surnames, nicknames, place names, company names, phone numbers, addresses, handles with generic placeholders (`[name]`, `[place]`, `[co]`). If a sample has too much private context to sanitize cleanly, drop it, don't save it.

For each field, infer from the raw samples:

- `capitalization_by_channel`: look at each channel's samples. All lowercase? Sentence case? Mixed? Record per channel.
- `contractions`: count contracted forms ("don't", "you're") vs full ("do not", "you are"). Assign `always`, `sometimes`, `rarely`.
- `emoji_usage_by_channel`: count emoji per message. `often` = most messages, `occasional` = some, `rarely` = few, `never` = zero.
- `typical_length`: rough avg, `short` (under 15 words), `medium` (15-40), `long` (40+).
- `filler_words`: recurring casual tokens ("honestly", "tbh", "haha", "lol", "kinda", "actually", "like", "ngl"). Pick up to 5 that appear more than once.
- `signature_phrases`: recurring openers/closers ("yo", "oi", "hey", "alright then", "cheers"). Up to 3.
- `punctuation_habits`: plain-English description, e.g. "drops periods on WhatsApp and Instagram, uses ellipses to trail off mid-thought, rarely uses exclamation marks".
- `avoid_phrases`: from the avoid list section verbatim.

For `tone_tiers`, use their sample per tier plus the tier defaults from `reference/tone-tiers.md`. Store the sample as the anchor, AFTER sanitizing any names / places to placeholders. Write a short `guidance` sentence per tier describing the delta from their baseline voice (e.g. close tier = even more lowercase than baseline, drops "I" more, uses inside jokes). The `description` field should be a role category ("best mate, sibling, partner"), never a real name.

## Confirmation

Before saving, show the fingerprint back to the user in plain English, not JSON. Example:

> Here's what I've got for you:
>
> **You**: Henry, building AI voice agents for small businesses that miss too many calls.
>
> **Primary channels**: WhatsApp, Instagram. Occasional: LinkedIn, SMS.
>
> **Voice**: You type lowercase on WhatsApp and Instagram, sentence case on LinkedIn. Contractions always. Emojis occasional on IG, rare elsewhere. Short messages. You lean on "honestly", "tbh", "haha". You open with "yo" or "hey". You drop periods on casual channels and use "..." to trail off.
>
> **Tone tiers**: Close = full lowercase, one-word replies, zero formality. Friend = casual but punctuated, contractions, names capitalized. Acquaintance = warm but sentence-case, polite opener, full sentences.
>
> **Avoid**: "reached out", "hope this finds you well", "circling back".
>
> **Availability**: about 30 min/day on weekdays (evenings after 8pm), weekends more flexible. Realistic daily ceiling around 30-45 messages.
>
> Sound like you? Anything I got wrong?

If they tweak, tweak the fingerprint and re-confirm. If they say yes, save.

## Save

Write the profile to `.claude/state/user-profile.json` using this schema (fill real values, not placeholders):

```json
{
  "version": 1,
  "activated_at": "YYYY-MM-DD",
  "user": {
    "first_name": "Henry",
    "what_they_do_casually": "building AI voice agents for small businesses that miss too many calls"
  },
  "channels": {
    "primary": ["whatsapp", "instagram"],
    "occasional": ["linkedin", "sms"],
    "not_used": ["email", "facebook_messenger", "phone", "voice_note"]
  },
  "voice": {
    "capitalization_by_channel": { "whatsapp": "lowercase", "instagram": "lowercase", "linkedin": "sentence_case", "sms": "lowercase" },
    "contractions": "always",
    "emoji_usage_by_channel": { "instagram": "occasional", "whatsapp": "rarely", "linkedin": "never", "sms": "rarely" },
    "typical_length": "short",
    "filler_words": ["honestly", "tbh", "haha"],
    "signature_phrases": ["yo", "hey"],
    "punctuation_habits": "drops periods on whatsapp and instagram, uses ellipses mid-thought, rarely uses exclamation marks",
    "avoid_phrases": ["reached out", "hope this finds you well", "circling back"]
  },
  "tone_tiers": {
    "close": {
      "description": "best mate, sibling, partner",
      "sanitized_sample": "yo you around tn",
      "guidance": "full lowercase, one-word replies fine, inside jokes, zero formality"
    },
    "friend": {
      "description": "friends seen a few times a year, close coworkers",
      "sanitized_sample": "hey [name] hows it going, been ages",
      "guidance": "casual, contractions, names capitalized, mild punctuation"
    },
    "acquaintance": {
      "description": "old classmate, friend of a friend, ex-colleague",
      "sanitized_sample": "Hey [name], hope you're doing well. Saw your post about the new role, congrats.",
      "guidance": "warm but sentence-case, polite opener, full sentences, a bit more formal"
    }
  },
  "illustrative_samples_by_channel": {
    "whatsapp": ["sanitized short line 1", "sanitized short line 2"],
    "instagram": ["sanitized short line 1"]
  },
  "availability": {
    "daily_minutes": 30,
    "best_window": "evenings after 8pm",
    "notes": "work full time + 2 kids, weekends are better"
  }
}
```

Note: the `mindset` top-level object is populated separately by the `/mindset` skill, not by `/activate`. Do not write to it from here.

**Schema notes:**
- `tone_tiers.*.sanitized_sample` replaced the old `samples` array. One short, proper-noun-stripped example per tier is enough.
- `illustrative_samples_by_channel` replaced the old `raw_samples_by_channel`. Max 5 very short sanitized lines per channel, or omit the channel if you couldn't sanitize anything safely.
- NEVER include real names, phone numbers, addresses, workplace names, or anything private in these fields.

Use today's date for `activated_at`. Resolve it with a quick bash `date +%Y-%m-%d` if you're not sure.

Create the `.claude/state/` directory via `mkdir -p .claude/state` before writing the file if it doesn't exist.

## Hand off

Tell them where it saved and what to do next:

> "Saved to `.claude/state/user-profile.json`. We're about to to our mindset module. 
>
> A quick back-and-forth covering the 3 most common mindset blockers, I'm here to help you get over those and become a master warm outreacher! 
>
> Type /mindset"

Don't oversell the outreach skill. Don't summarize what the warm outreach workflow is. They'll see it when they type `/outreach`.

## Self-check before saving

- [ ] No em dashes anywhere in the file
- [ ] No merge tag artifacts like `{{firstName}}`
- [ ] `activated_at` is a real ISO date, not a placeholder
- [ ] `primary` has at least one channel
- [ ] Each tier has at least a `description` and `guidance` (samples may be thin but not empty unless user truly refused)
- [ ] Raw samples, if the user provided them, are stored verbatim and not rewritten
- [ ] `voice.avoid_phrases` reflects what the user actually said

If any fails, fix before writing.
