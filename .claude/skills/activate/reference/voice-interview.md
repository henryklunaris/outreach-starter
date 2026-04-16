# Voice Interview, Detailed Script

This is the back-of-house notes for `/activate`. The main SKILL.md has the structure. This file has the exact phrasing to use and how to pull signal out of raw samples.

## Tone to hit when talking to the user

Chill. Curious. Not a form, not a quiz. Treat it like you're helping a friend set up a tool and you need 10 minutes of their time. One question per turn. Short sentences.

Bad (form-y, interrogation):
> Please provide the following information: (1) First name (2) Role description (3) Primary communication channels...

Good (chill, conversational):
> Quick intro, what's your first name and in one sentence, what are you up to these days?

## Intro phrasing options

Pick one, don't recite all:

- "Alright, quick intro. What's your first name, and in one chill sentence, what are you actually up to?"
- "Start me off with your first name and one line about what you're working on. The version you'd say at a BBQ, not the LinkedIn version."
- "Name and a one-liner on what you do. Keep it casual, this is literally the line you'll use when your contacts ask 'so what are you up to?'"

If they give LinkedIn-voice back ("I empower small businesses to leverage AI"), push once:
> "Would you actually say that to your mum? Try it again the way you'd say it out loud."

## Channels phrasing

> "Which of these do you actually use to message friends and family? Pick your top 2-3 as primary, anything else you use sometimes as occasional, and ignore the rest.
>
> LinkedIn, Instagram, SMS, WhatsApp, Email, Facebook Messenger, Phone, Voice note."

If they list 5+ as primary, gently narrow:
> "Primary is for where most of your actual outreach will happen. Pick the 2 or 3 you'd reach for first."

## Voice samples phrasing, per channel

Loop through their primary channels, one at a time.

> "Okay for WhatsApp, paste me 3-5 messages you've actually sent to friends or family recently. Boring ones are perfect. Confirming a time, asking how they are, replying to a photo. Anonymize names if you want."

If they paste 1-2 and stop, that's fine:
> "Cool, got it. Next channel, Instagram..."

If they paste messages that are clearly performative (captions, bio-style lines), ask:
> "These feel like public-facing ones. Got any from a DM or private thread where you were just being yourself?"

## Tone tiers phrasing

Three mini-prompts, one per tier. Keep each short.

**Close:**
> "Now three tiers. First, someone really close. Best mate, sibling, partner. Who's that person, and what's a message you'd actually send them on a normal day?"

**Friend:**
> "Next tier, a friend you see a few times a year, or a coworker you actually like. Who fits, and a message you'd send them?"

**Acquaintance:**
> "Last tier, someone you know but aren't close with. Old classmate, friend of a friend, ex-colleague you haven't spoken to in years. One sample message."

If they give the same tone for all three tiers, note that and ask:
> "These all read really similar, is that actually how you'd text someone you haven't spoken to in 5 years vs your best mate? No wrong answer, just checking."

## Avoid list phrasing

> "Last one. Any words or phrases you'd never actually say? Stuff that makes you cringe when you see other people write it. 'reached out', 'hope this finds you well', 'circling back', 'synergy', whatever your list is."

If they can't think of any, seed with 2-3 common ones and ask which resonate:
> "Common ones people flag: 'reached out', 'hope this finds you well', 'quick question'. Any of those? Or other ones?"

## Extraction, from raw samples to fingerprint

### Capitalization

Look at each channel's samples. Classify as:
- `lowercase`: 80%+ of messages start lowercase and only proper nouns or deliberate emphasis are capitalized
- `sentence_case`: most messages start with a capital letter and follow normal rules
- `mixed`: roughly balanced, or depends on mood

Record per channel. LinkedIn and email are almost always `sentence_case` even for users who texts lowercase everywhere. Don't force consistency.

### Contractions

Count "don't", "you're", "I'm", "it's", "can't" vs "do not", "you are", "I am", "it is", "cannot".

- `always`: 90%+ contracted
- `sometimes`: mixed, maybe more contracted than not but full forms appear
- `rarely`: uses full forms

Most casual texters are `always`. Formal users might be `sometimes`.

### Emoji usage

Count emoji per message, per channel.

- `often`: most messages have 1+ emoji
- `occasional`: some messages have emoji
- `rarely`: a few messages have emoji
- `never`: zero emoji in samples

Per channel. Don't aggregate, people text very differently on LinkedIn vs Instagram.

### Typical length

Rough word count per message, averaged across their samples.

- `short`: under 15 words
- `medium`: 15-40 words
- `long`: 40+ words

WhatsApp and SMS skew short. LinkedIn and email skew longer. Report the channel baseline.

### Filler words

Words that recur across samples and signal casual voice. Common: "honestly", "tbh", "haha", "lol", "kinda", "actually", "like", "ngl", "literally" (if they use it conversationally, not to literally mean "literally"), "mate", "dude", "man".

Pick up to 5 that appear more than once. Don't include generic connector words ("and", "but", "so").

### Signature phrases

Recurring openers and closers. Openers: "yo", "oi", "hey", "alright", "morning". Closers: "cheers", "later", "x" (a lot of Brits/Aussies sign texts with a single x), "ttyl".

Up to 3. Verbatim as they wrote them.

### Punctuation habits

Plain-English description of 2-3 patterns you noticed. Examples:

- "drops periods on WhatsApp and Instagram, keeps them on LinkedIn"
- "uses ellipses to trail off mid-thought instead of committing to a period"
- "doubles up on question marks when surprised"
- "no exclamation marks almost ever"
- "commas used as rhythm markers, not strict grammar"

Keep it descriptive, not prescriptive.

## Worked example, end to end

Raw samples from user, WhatsApp:
```
yo you around tn
haha yeah saw that
tbh its been a rough week man, you good?
cool ill be there in 10
ok nice
```

Raw samples, LinkedIn:
```
Hey Jake, congrats on the new role. Three years in and they're already moving you up, clearly doing something right.
Thanks so much for the intro, really appreciate you thinking of me.
```

Extracted voice:
```json
{
  "capitalization_by_channel": { "whatsapp": "lowercase", "linkedin": "sentence_case" },
  "contractions": "always",
  "emoji_usage_by_channel": { "whatsapp": "never", "linkedin": "never" },
  "typical_length": "short",
  "filler_words": ["yo", "haha", "tbh", "man"],
  "signature_phrases": ["yo"],
  "punctuation_habits": "drops periods on whatsapp, keeps them on linkedin, no exclamation marks, uses commas as rhythm markers"
}
```

Note how the WhatsApp style (lowercase, no periods, "yo") is clearly different from LinkedIn (sentence case, full punctuation, "Hey Jake"). Both are captured. The `/outreach` skill will pick the right one based on channel.

## When a user pushes back or resists

If the user says "can't you just generate this from my LinkedIn" or "do I really need to paste messages":

> "The whole point of this is drafts that sound like you. Without real samples, I'm guessing. Even 2 messages per channel is way better than zero."

If they refuse entirely:

- Let them skip sample-pasting, still do Blocks A, B, D (descriptions), E.
- Mark `voice.capitalization_by_channel` etc. as `unknown` rather than guessing.
- `/outreach` will fall back to the generic Handwritten Feel rules in `outreach/SKILL.md` when voice fields are `unknown`.

## When in doubt

Err on the side of fewer, higher-confidence fields over guessing. An `unknown` field is better than a wrong one. The user can always rerun `/activate` to add samples later.
