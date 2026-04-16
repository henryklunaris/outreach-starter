# Relationship Tone Tiers

How close you are to someone changes how you text them. This is the 3-tier model `/activate` captures and `/outreach` uses to shape drafts.

## The three tiers

### Close

Who fits: best mates, siblings, partner, parents you text often, cousin you grew up with, childhood friend who's still in your daily life.

How the user typically writes at this tier:
- Often full lowercase
- One-word replies are fine
- Inside jokes, callbacks to old conversations
- Zero formality, no "hope you're well"
- Might open with a meme reaction or just dive straight in
- Emoji usage depends on the person but usually natural and frequent on IG/WhatsApp

Example message (friend texting their best mate):
> yo free sun? bbq at mine

### Friend

Who fits: friends they see a few times a year, close coworkers they genuinely like, gym buddies, old flatmates, teammates from a sport.

How the user typically writes at this tier:
- Sentence case usually, but still casual
- Contractions always
- Names capitalized, questions end with a question mark (usually)
- Warm, uses their actual name
- Might reference shared context ("how'd that trip go?")

Example:
> Hey mate, been ages. Saw you were in Lisbon last month, how was it?

### Acquaintance

Who fits: old classmate from uni they haven't spoken to in 3+ years, friend-of-a-friend they met once, ex-colleague from an old job, someone's cousin they were introduced to at a wedding, parent of a school friend.

How the user typically writes at this tier:
- Sentence case, full punctuation
- A bit more formal opener ("Hey Sarah, hope you're doing well" is okay here, not at other tiers)
- Full sentences, no fragments
- Still warm, still personal, just with more care because the bridge is thinner
- Emoji usually none or very rare

Example:
> Hey Sarah, been a while. Saw on LinkedIn you moved to Sydney, congrats on the big move. How's it been settling in?

## Why this matters

Two things change across tiers: the register (how casual/lowercase/punctuated the writing is), and the amount of ACA structure needed.

### Register

The same ACA content reads completely differently across tiers. Hitting a close friend with sentence-case formality feels cold. Hitting an acquaintance with lowercase one-liners feels invasive or weird.

### ACA structure per tier

ACA is scaffolding for crossing distance. The closer the contact, the less you need.

- **close**: skip ACA. Just text them naturally. Manufactured Compliment reads like you're talking to a stranger.
- **friend**: light ACA. Acknowledge + Ask required, Compliment optional (only if there's a genuine trigger).
- **acquaintance**: full ACA. A + C + A, all three. This is what ACA is designed for.

If there's an active thread (old messages visible), all tiers dial down one step: the thread does some of the Acknowledge work, and Compliment can feel forced when you're picking up mid-conversation.

`/outreach` picks the tier from the user's closeness answer in Step 2. `/activate` captures the user's specific flavor of each tier so drafts aren't generic.

## Mapping `how-known` answers to tiers

When `/outreach` asks "how do you two know each other?", the answer usually lands on one of these. Here's the rough map:

| `how-known` answer | Default tier |
|---|---|
| best mate, best friend, brother, sister, partner, mum, dad | close |
| childhood friend, grew up together, lived together | close |
| uni friend, college friend, close friend | friend |
| coworker (current), teammate, gym buddy | friend |
| hobby friend (climbing, running club, etc.) | friend |
| old coworker, ex-colleague | acquaintance (unless they stayed close) |
| uni classmate I haven't seen in years | acquaintance |
| friend of a friend, met at a wedding/party | acquaintance |
| old client, ex-client | acquaintance |
| neighbor (nodding terms) | acquaintance |
| parent's friend, friend's parent | acquaintance |

Edge cases:
- "Uni friend but we haven't spoken in 5 years" → bump down to acquaintance.
- "Coworker but we also hang out every weekend" → bump up to close.
- "Family but we're not close" → treat as acquaintance.

Ask one clarifying question if the answer is genuinely ambiguous. Don't interrogate.

## How the same ACA reads at each tier

Scenario: user wants to reach out to someone who just got promoted.

**Close (best mate):**
> yo saw the promo, congrats man. drinks soon?

**Friend (uni friend they still see):**
> Jake! Saw you made senior analyst, congrats. Three years in and they're already moving you up, you loving it or burnt out?

**Acquaintance (old coworker from years ago):**
> Hey Jake, been a while. Saw on LinkedIn you made senior analyst at the firm, congrats on that. How's finance been treating you these days?

Same ACA, same intent, three different registers. This is what the tier system exists to produce.

## What NOT to do

- Don't write "Hey [Name]" at the close tier. That's formal.
- Don't write "yo" at the acquaintance tier. That's presumptuous.
- Don't use the same opener ("Saw your post about X") verbatim across all three, vary the register.
- Don't skip the tier check. If `/outreach` hasn't confirmed a tier via `how-known`, ask.
