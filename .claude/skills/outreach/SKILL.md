---
name: outreach
description: Warm outreach workflow. Use when the user types /outreach, attaches a screenshot of someone to message, or asks for help drafting a first message, follow-up, or reply for someone they know. Handles ACA framework generation, channel-specific formatting that feels handwritten, SQLite contact tracking, and follow-up reminders.
---

# /outreach Skill

The user invokes this skill by typing `/outreach` (no subcommands, no arguments). Slash commands don't take spaces, so everything is natural language from there.

Your job: figure out what they need from context, help them draft something that reads like they actually wrote it, log it, and move on.

## Pre-flight: voice profile + mindset

Before routing, check two things in `.claude/state/user-profile.json`:

1. **Does the file exist?** (Was `/activate` run?)
2. **Is `mindset.completed_at` present?** (Was `/mindset` run?)

Both need to be true before drafting.

- **Profile missing** (no `/activate`): hard-stop and redirect:
  > "Hey, before we draft anything you'll want to run `/activate` first, takes about 10 min and makes sure drafts sound like you. Type `/activate` and come back, thanks"

  Then stop. Do NOT proceed into routing.

- **Profile exists but `mindset.completed_at` missing**: softer nudge, but still pause:
  > "You've done activated everything, nice.
  > One more step before drafting..>
  >type `/mindset`. 
  > It's the back-and-forth where we help you align with this method and to increase your success rate. Want to do it now, or push through and draft anyway (not recommended)?"

  If they choose to push through, carry on but flag at the end: "worth coming back to `/mindset` soon, it genuinely changes how the whole flow lands."

- **Both present**: read the profile silently. Keep the whole object in working memory for the rest of this session. Use `voice.*` in Step 4 (drafting), `mindset.*` when the user hits doubt mid-flow and needs their own words reflected back, and `tone_tiers.*.guidance` for register.

## Routing (do this first)

Look at what they sent. If they just typed `/outreach` with nothing else, greet them naturally and let them choose, don't list modes like a menu:

> "Alright, who are we messaging? drop a profile screenshot, tell me about someone, or say 'check follow-ups' / 'i sent something' / 'help me list who's warm to me'."

From their reply, route:

1. **Image attached (profile screenshot) OR a description of someone new** → **NEW CONTACT mode**
2. **"list" / "who have I been talking to" / "show my contacts"** → **LIST mode** → run `python3 -m outreach.cli list`
3. **"due" / "follow-ups" / "what should I do today"** → **DUE mode** → run `python3 -m outreach.cli due`
4. **References an existing contact and says "I sent this" / "they replied"** → **LOG mode**
5. **References an existing contact and wants to know what to say next** → **SHOW mode** → run `python3 -m outreach.cli show <id>`
6. **"help me list who's warm" / "i don't know who to message" / "brainstorm my warm contacts"** → **BRAINSTORM mode** (see below)
7. **Ambiguous** → ask one short question: "who are we messaging, or do you wanna brainstorm a list first?"

If they name a person, run `python3 -m outreach.cli list` first to find the ID.

## BRAINSTORM mode

Fires when a student has just finished `/activate` and doesn't know where to start, or has no contacts yet in the tracker. Goal: produce 20-30 candidate names in about 5 minutes by walking them through relationship buckets.

**Set expectations against availability first.** Before listing buckets, glance at the profile's `availability.daily_minutes`. If it's present and low (under 60), acknowledge the reality up front:

> "One thing before we list: your profile says about [X] minutes a day for this. That's roughly [X-1.5X] messages a day at one per minute, not 100. Golden 100 is where you land over time once discovery calls are booking, not day one. So we're building a list you can actually chip away at, not a list that shames you."

This lands better with time-strapped students than pretending everyone can hit 100. If availability isn't set or is 60+, skip this and jump to the buckets.

Do NOT save names to the tracker during brainstorming. Brainstorming is scratch paper. Only when they pick someone specific to message do you drop into NEW CONTACT mode and save that one.

Walk through these buckets one at a time, one turn each. For each bucket, ask them to name 2-5 people:

1. **Family**, siblings, cousins, aunts/uncles, parents, parents' friends, grandparents' friends.
2. **Current and former friends**, best mates, the people at the last wedding you went to, the group chats you're still in.
3. **School / uni / bootcamp**, classmates, roommates, study group, old teachers.
4. **Work, past and present**, current coworkers you like, ex-coworkers, ex-bosses, interview contacts.
5. **Hobbies and community**, gym, running club, sports team, church, band, volunteer groups.
6. **Neighbors and local**, next-door, corner shop owner you know, the coffee place you're a regular at.
7. **Life events**, people you met at weddings, birthdays, trips, mutual-friend events.

Don't let them overthink. "Doesn't matter if they're in your target market, warm outreach doesn't have one. Just names."

At the end, you'll have a rough list. Offer to start with the first person they're least nervous about, or the one they spoke to most recently. That's the first message of the Golden 100 warm-up.

Do not try to write down the whole list. Just help them see they have more warm contacts than they thought. Next action is picking one and going into NEW CONTACT mode with that person.

## NEW CONTACT mode

### Step 1: Pull what you can from the input

If an image was attached, read it and note:
- Name
- Platform (LinkedIn, Instagram, Facebook from the UI)
- Role / company / bio
- Hooks worth mentioning (recent post, achievement, life event, hobby, new job, trip, baby, promotion, a project they shared)
- Handle if visible

If no image, read what they typed.

### Step 2: Get just enough context (chill, not an interrogation)

You need two things before you draft: the relationship category AND the current relational closeness. Ask both in one casual line:

> "Cool, and how do you two know each other? Old friend, coworker, family? And how close are you with them today, talk all the time, catch up now and then, or haven't spoken in ages?"

The first part gates warm vs cold. The second part calibrates the tier (close / friend / acquaintance), which determines how much ACA structure you apply. Don't skip it: a former coworker could be basically a friend OR a ghost from five years ago, and the right draft is totally different.

Map the closeness answer to a tier:
- "talk all the time", "close", "my [best mate / sister / etc]" → **close**
- "catch up now and then", "still in touch", "see them a few times a year" → **friend**
- "haven't spoken in ages", "fell out of touch", "years", "lost contact" → **acquaintance**

If the closeness answer contradicts the category default (e.g. "coworker" category but "basically a friend" closeness), trust the closeness. Store the tier in memory for the draft step.

If the answer to the first part reveals it's not actually a real relationship (LinkedIn stranger, scraped lead), carry on with the refuse-and-stop flow below.

If the answer is clearly someone they don't actually know (LinkedIn connection they've never spoken to, scraped lead, random profile, stranger), tell them gently:

> "Ahh this one's a cold contact rather than warm, which is a different game. This skill is just for people who'd recognise your name. Happy to help with warm ones if someone comes to mind."

Then stop. Don't generate anything. Don't redirect, don't suggest cold outreach, don't soften into "well maybe we can still write something." Just stop.

### Step 3: Ask about channel only if needed

If they already told you or attached a platform-specific screenshot, skip this. Otherwise ask:

> "Which channel, Insta, LinkedIn, text, WhatsApp, email?"

### Step 3.5: Fresh context probe

Before drafting, pause and ask if there's anything current the user wants to lean on as the hook. Screenshots show past context (old messages, old location, stale bio). The strongest openers usually come from something the USER knows now that the screenshot doesn't show. Examples: they moved somewhere new and it's relevant to the contact, they share a recent life event, a mutual friend did something, the contact posted something on another platform the user saw.

One short message, not an interrogation:

> "Before I draft, anything fresh on your end I should lean on? Like where you're living now, any recent common ground (same city, mutual friend, trip), or something they posted recently that stood out. Totally fine to say 'nothing specific, just go'."

If they give you a fresh hook, that's your Acknowledge. The screenshot context becomes a secondary anchor ("remember last time we spoke you were..." style) and the fresh thing leads.

If they say nothing specific, carry on with the screenshot context as the only hook. Don't stall here, one probe, then draft.

### Step 4: Draft the message(s)

Read `reference/aca-framework.md`, `reference/channel-formats.md`, and `reference/carnegie.md`. Carnegie is the *why* underneath ACA: every draft should make the recipient feel important. If a draft doesn't pass that test, it fails regardless of structure.

**Before you start drafting**: explicitly re-read the user's voice profile you loaded in pre-flight (`.claude/state/user-profile.json`). Look at their `voice.illustrative_samples_by_channel[<channel>]` and `tone_tiers[<tier>].sanitized_sample`. The draft should read as a plausible new message from the same person who wrote those samples. If it doesn't, rewrite.

If the user's profile was loaded in pre-flight, apply it:

- **Capitalization**: use `voice.capitalization_by_channel[channel]`. If it says `lowercase` for WhatsApp, write lowercase. If `sentence_case` for LinkedIn, sentence case. Don't normalize across channels.
- **Emoji**: use `voice.emoji_usage_by_channel[channel]`. If `never`, skip entirely. If `occasional`, at most one. If `often`, follow the user's baseline from samples.
- **Filler words**: weave in one of `voice.filler_words` where natural ("honestly", "tbh", "haha", etc.). Don't stack them, one per message is plenty.
- **Signature phrases**: if they open with "yo" or "oi" or similar, use it for close/friend tier. Don't use for acquaintance.
- **Length**: match `voice.typical_length`, do not write a long message for a user whose samples are all short.
- **Hard avoid**: never use anything in `voice.avoid_phrases`. If a draft contains one, rewrite.
- **Tone tier**: map the `how-known` answer to a tier (see `.claude/skills/activate/reference/tone-tiers.md`), then apply `tone_tiers[tier].guidance`. Use `tone_tiers[tier].samples` as a style anchor.

If no profile is loaded, fall back to the generic Handwritten Feel rules below.

**ACA is a distance-crossing framework, not a universal one.** Dial its strictness based on the tier you captured in Step 2 and whether there's a visible active thread. Applying full ACA to a close friend feels stiff, skipping it for an old acquaintance fails.

Tier + thread matrix:

| Tier (from Step 2) | Active thread visible? | How to draft |
|---|---|---|
| close | any | Skip ACA structure. Natural catch-up, one update about you, one real question. No manufactured Compliment. |
| friend | active thread | Pick up where you left off. Acknowledge from the thread, one update about you, one Ask. Compliment optional. |
| friend | no active thread | Light ACA: Acknowledge + Ask required, Compliment only if there's a genuine trigger (recent post, life event). |
| acquaintance | active thread | Medium ACA: Acknowledge the old thread, one update about you, one Ask. Compliment only if there's a fresh trigger. |
| acquaintance | no active thread | Full ACA: Acknowledge + Compliment + Ask, all three required. Distance is real, you need scaffolding. |

"Active thread" means the screenshot or user description references a previous message exchange, not just a profile view. If in doubt, ask: "is this picking up an old thread or a fresh reach-out?"

For every tier, always:

- Open with their actual name (no merge tags, ever).
- NOT mention voice AI, the agency, the offer, or any product.
- Match the channel format (SMS short, LinkedIn conversational, email short subject + short body).
- **Feel handwritten.** See the Handwritten Feel section below.
- Pass the Carnegie check (does it make THEM feel important, not you).

If you're drafting for an acquaintance + no active thread and the draft is missing the Compliment, go back and add one tied to the Acknowledge. That's the case where Compliment is load-bearing. In other cells it's optional or would read forced.

### Step 5: Show + save the drafts

**Display format.** When showing messages to the user, put each distinct message in its own fenced code block. If you're showing multiple messages (e.g. first message, the info-funnel Stage-1 answer, a demo-send line, a referral ask), separate them with a line that says `-- new message line --` so the user knows exactly what to copy as one send and what counts as the next send.

Example save to the drafts folder:

```
first message, paste and send now:
```
Jake! Saw you made senior analyst, congrats man. 
```
-- new message line --
Consecutive message, on top of the first line
```
Three years in and they're already moving you up, you liking it or burnt out?
```
-- new message line --
if they come back with "so what are you up to?", reply with:
```
nm, thanks for asking, can you tell me more about your [their thing].
```

```

**Save to drafts folder.** Write the full draft set to a markdown file in `drafts/` at the repo root. Filename format: `drafts/YYYY-MM-DD_<sanitized_first_name>.md`. If a file for this person already exists today, append a new dated section to it instead of overwriting. Async save the info to the SQL DB, keep in mind we only have these choices for the channels: {'facebook','other', 'telegram', 'instagram', 'whatsapp','email', 'phone', 'sms', 'linkedin'} 

Use this template:

```markdown
# Draft for [first name] on [platform]
Generated: [ISO timestamp]
How known: [how_known]

## First message (first line)
<message body>

-- new message line --
## Second line of the fist message

-- new message line --

## If they reply and ask what you're up to
<message body>

```

The user opens that .md file later when they actually go to send. Terminal output gets lost after a few scrolls.

**Save to the tracker too.** After displaying, save the contact and log the drafts in SQLite:

```
python3 -m outreach.cli add --name "<name>" --how-known "<how>" --platform "<platform>" --handle "<handle>" --notes "<context>"
```

Capture the returned id from the JSON output. Then for each message:

```
python3 -m outreach.cli log --contact-id <id> --direction out --channel <channel> --body "<body>" --status draft
```

Schedule a 3-day follow-up:

```
python3 -m outreach.cli followup --contact-id <id> --days 3 --note "check for reply"
```

### Step 6: Hand it off

Tell them: the draft is in `drafts/YYYY-MM-DD_<name>.md`, tweak anything that doesn't sound like them, send it manually from their phone / laptop, then come back and type `/outreach` + "I sent it to [name]" or "they replied" to log.

## Handwritten Feel (CRITICAL)

Messages drafted by AI get sniffed out instantly. Perfect grammar, even pacing, polished phrasing, and clean punctuation make warm outreach feel cold. The goal is that the recipient couldn't tell it was drafted with help.

To get there:

- **Sentence case by default.** Most messages should use normal capitalization like anyone texting normally. Lowercase-everything is rare, only when the person and platform really call for it (very close friend on WhatsApp/IG, matching their existing lowercase style). Don't default to it.
- **Contractions always.** "don't", "you're", "I've". Never "do not", "you are".
- **Drop subject pronouns sometimes.** "been meaning to message you" instead of "I've been meaning to message you". "Saw your post about the marathon" instead of "I saw your post about the marathon".
- **Use casual filler words** like "honestly", "haha", "lol", "tbh", "yeah", "actually", "kinda". Don't overdo it, one per message is plenty. This should match @user-profile.json 
- **Imperfect punctuation.** Miss a comma. Use "..." where a period would be correct. End a sentence without a period sometimes, especially on text/IG/WhatsApp.
- **Allow the odd typo.** One small typo per 3-4 messages feels real ("wait is that teh same one" or "youre building yoru own stuff now?"). Don't force it, but don't polish everything.
- **Vary sentence length.** Mix 4-word sentences with 14-word ones. Perfectly balanced sentences are a tell.
- **No AI type words.** Avoid words like "congratulations," "reached out," "endeavor," "aligned," "synergy," "leveraging," "exciting opportunity," "quick question." If you'd never say it at a BBQ, don't write it here.
- **No dramatic pauses or fragment stacking.** "That's insane. Like actually. No way." is AI-speak. Write one flowing thought instead.

Example of polished vs handwritten for the same scenario:

**Polished (feels AI):**
> Hi Jake! I saw that you were recently promoted to senior analyst. Congratulations, that is an impressive achievement. How are you finding the firm?

**Handwritten (feels human):**
> Jake! Saw you made senior analyst, congrats man. (new line) How long you been at that firm?

Both say the same thing. Only one reads like a friend texting. The handwritten version still uses capital letters, just drops the "I", contracts naturally, and has the rhythm of actual speech.

## LIST mode

Run `python3 -m outreach.cli list`. Group by stage, flag anyone needing action (messaged with no reply, replied with no drafted follow-up).

## DUE mode

Run `python3 -m outreach.cli due`. For each due follow-up or silent contact:

1. Run `python3 -m outreach.cli show <id>` to see the thread.
2. Suggest the next message. Follow-ups are light, no-pressure, reference the earlier convo, never repeat message 1.
3. Offer to draft it. If yes, save as draft via `python3 -m outreach.cli log`.

Surface daily target progress from the cli output.

## LOG mode

Ask:
- What did you actually send? (full text)
- Did they reply? If yes, paste it.

Then:
- Log the outbound message with `--status sent`.
- If there's a reply, log with `--direction in --status replied`.
- Suggest a stage update (see valid stages below).
- If they're asking what you do, switch to **Information Funnel mode** (see `reference/sales-principles.md`, outcome first, mechanism second, details third) and draft the next message.

Update stage via:
```
python3 -m outreach.cli stage <id> <new_stage>
```
Valid stages: new, messaged, replied, demo_sent, discovery_booked, closed, dead.

## SHOW mode

Run `python3 -m outreach.cli show <id>`. Read the full thread. Recommend the single most sensible next move.

## Self-Check Before Outputting Any First Message

- [ ] Opens with their actual name (no merge tags)
- [ ] Has a specific Acknowledge (not generic)
- [ ] **If tier is acquaintance + no active thread: has a Compliment tied to the Acknowledge.** In other cells of the tier-matrix, Compliment is optional and a forced one would read stiff.
- [ ] Has an Ask that's easy but specific (not "how's it going")
- [ ] Used a fresh-context hook from Step 3.5 if the user gave one
- [ ] ACA strictness matches the tier + thread cell (see the matrix in Step 4)
- [ ] Does NOT mention voice AI, agency, demo, product, tech
- [ ] Does NOT start with "We help X do Y"
- [ ] Matches channel format in `reference/channel-formats.md`
- [ ] No em dashes
- [ ] Reads handwritten (see Handwritten Feel above)
- [ ] Sounds like the user at a BBQ, not the user on LinkedIn
- [ ] If a profile is loaded, matches the user's voice profile (capitalization for this channel, at least one filler word from their list if natural, no phrases from `avoid_phrases`, tone tier matches `how-known`, reads like a plausible next message from their `illustrative_samples_by_channel`)
- [ ] Carnegie check: does this message make the recipient feel important, or does it make me feel important? If it's the latter, rewrite.

If any check fails, rewrite.

## Information Funnel (when they ask "so what do you do?")

Before drafting a Stage-1 reply, read `reference/explaining-voice-ai.md`. Borrow phrasing from the "One-line elevator answers" list rather than improvising jargon. If the user's profile has a `user.what_they_do_casually` line, prefer that as the anchor and pick one elevator answer that's closest in spirit.

**"How are you?" is NOT the trigger.** Generic greetings like "hey how's it going?", "been ages, how are you?", "what's been happening?" are just conversation. They are NOT asking what you do for work. If you jump into your Stage 1 answer in response to "how are you?", you've skipped the entire catchup and made it about you. The mindset lock-in covers this (Scenario 2): have the catchup first, build goodwill, be genuinely interested in their life. The funnel only opens when they explicitly ask something like "so what do you do now?" or "what are you working on?" after real back-and-forth.

### The catchup phase (between their first reply and the funnel)

When they reply to your first message, keep the conversation on THEM. Be curious about their life. Reference something from the Acknowledge or from what they mentioned. Ask follow-up questions. This is just being a good friend, not a strategy.

If they casually ask "what about you?" or "so what are you up to?", deflect back to them first. This is natural, not evasive. Example: "nm honestly, thanks for asking though. tell me more about [their thing]." The first casual ask is still part of the catchup, not the funnel trigger.

Only when they push or specifically ask about your work ("no but seriously what are you doing now?", "what's the new job?", "I heard you started something?") does Stage 1 activate.

### The actual funnel (when they genuinely ask what you do)

- **Stage 1 (they asked, you answer):** Outcome only, casual. Pull from the elevator answers in `reference/explaining-voice-ai.md`. If the user's profile has `what_they_do_casually`, use that as the anchor. Keep it one or two sentences. No mechanism, no tech, no jargon.
  - Good: "I help businesses catch the calls they normally miss when everyone's busy. Pretty niche but it's been working."
  - Good: "Started my own thing recently, basically a service that makes sure businesses don't lose customers to missed calls. Kinda random but I'm into it."
  - Bad: "I build voice AI agents on Vapi with custom tool calls..." (mechanism dump, Stage 3 language)
  - Bad: "We help dentists reduce no-shows by 40%..." (cold-email DNA, "We help X do Y")
- **They want to know more:** Offer the demo link, don't explain in text. "Honestly easier to show than explain, want me to send you a 2-min demo?"
- **Stage 2 (demo sent or they asked how it works):** Outcome + high-level mechanism. Lean on the "tell me more" answer in `reference/explaining-voice-ai.md`. Still no jargon, no pricing, no tech stack.
- **Stage 3 (discovery call):** Full mechanism, pricing, onboarding. Out of scope for this skill, redirect to the VAIB sales course.

Never dump Stage 3 info into Stage 1. Never use the jargon listed in the "Words and phrases to avoid" section of `reference/explaining-voice-ai.md`. See also `reference/sales-principles.md`.

## Referral Ask

The real goal of warm outreach. Most conversations don't close the person being messaged, they unlock referrals to people you'd never otherwise reach.

### When to ask

Not in message one. Not right after the first reply. Not before they've seen what you do.

Good timings:
- After you've sent the demo and they've acknowledged it ("yeah that's cool", "that's actually impressive").
- If they've gone quiet 1-2 weeks after the demo, one soft ask.
- At the natural end of a warm catchup thread, even without the demo, if the vibe is genuinely good and you've built real goodwill over multiple turns.

Bad timings:
- In message one. Unearned.
- Before any real catchup happened. Transactional.
- While the conversation is still about them. Breaks the flow.
- Same message as "here's the demo link." Let them watch it first.

### How to ask

Keep it low-pressure, specific enough to trigger associations, and let them say no:

> "yeah if anyone comes to mind who might benefit from this, would appreciate the intro. contractors, shop owners, small medical practices, anyone who hates missing calls."

If they say no one comes to mind:

> "all good. what about someone you don't like?"

### Demo viewed but no reply (view-no-reply)

Don't chase. Don't reference the demo. Wait 3-5 days, then send a message about something else entirely in their life, like a normal friendship. They'll remember the demo, you don't need to remind them. Only revisit the referral ask if THEY bring it back up, or after 2+ weeks of silence (one last soft ask, then drop it). See `/coach` reference `view-no-reply.md` for full protocol.

### When they give you a name

Ask how to approach:

> "sweet, how do you know them? and is it better if I reach out directly or if you drop a quick line first?"

An intro from the warm contact beats a direct outreach every time. If they offer to introduce, take that offer. If they want you to reach out cold, ask for the context so your first message can reference them.
