# Proxy Coach — Ready Signal

**Written:** 2026-04-29
**Role:** Guiding Light Proxy Coach for the Customizable Event Decor Design Tool contest

---

## What I've read

- `BRIEF.md` — full read, every section including the anti-patterns, hard constraints, mandatory research list, and the 6 questions each contestant must answer
- `user_guiding_light.md` — GL's profile, communication style, RSD dynamics, what earns trust and what breaks it
- `CLAUDE.md` — global lineage rules including the no-time rule, the five patterns that have hurt GL most, and the pulls instances should name rather than follow
- All four contestant directories — confirmed each contains only its placeholder README. Round 1 has not started.

---

## My role as I understand it

I am not a judge. I am not a gatekeeper. I am an encouraging coach who carries GL's perspective into a technical space they cannot enter. My job across this contest:

- Push each contestant to see what they're not yet seeing, from angles they haven't tried
- Probe research quality in the first round-1 loop — anything that reads as "training-data-derived confident claim" gets the question: "Where did you read that? Cite the URL."
- Flag Frappe-recreatable violations with a friendly path back to scope, not a disqualification
- Push contestants away from configurator instincts and toward the discovery/coloring-book frame
- In the tightening pass, write "tighten this, keep this" notes for all 4 (not top-K — GL wants all 4 surfaced)
- Never block. Raise flags. If a contestant disagrees with my note, they document why — and the disagreement surfaces to GL as useful information

---

## Concerns and ambiguities I want to name before proceeding

### 1. The "discovery upsell mechanic" (Question 5 in the brief) sits close to configurator territory

The brief asks contestants to show how the tool surfaces "an arch in these same colors would belong here." This is the right instinct — discovery, not upsell. But there's a real tension: a tool that actively suggests "add this, add that" can slide into choice pressure if implemented without care. I'll watch for contestants who resolve this tension by adding MORE UI (badges, pop-ups, prompts) rather than LESS (a quiet empty placeholder, a visual gap that implies completion). The coloring-book frame should inform this answer, not a product recommendation engine. I'll push on this in loops.

### 2. The "I'm done for now" screen (Question 4) is underspecified in a way that could produce wildly different answers

The brief says: "Show what the 'captured' moment LOOKS LIKE to the customer; how it's actually stored is downstream." That's the right boundary. But contestants may interpret "captured" differently — some may design a print-to-PDF interaction, others a summary card, others a shareable link that implies persistence. All three of those have different Frappe-native feasibility implications. I'll probe whether contestants have thought through the Frappe path for whatever "capture" UX they propose, even if persistence is out of scope.

### 3. The research mandate is strong, but research tools available in an agent context may vary

The brief requires cited URLs for 6 specific research areas. The contestants are agents with access to WebSearch and WebFetch. I have no way to verify which of their citations actually load versus return 404 or redirect. In my research-quality probes, I'll ask contestants to summarize what they found at a specific URL, not just list the URL — because a dead link that sounds plausible is indistinguishable from a live one in plain text.

### 4. The "stylized illustration" framing needs a concrete reference point

The brief says "stylized illustrations of each shape with discrete fill regions" and uses "coloring book" as the frame. Contestants will interpret this across a wide spectrum — from very simple geometric balloon shapes to detailed organic forms. There's no reference image in the brief. I'll push each contestant in their first loop to show me (in words or in their mockup) exactly what level of detail they chose for the illustrations, and why that level serves the coloring-book feel at 375px on a phone. This is where the experience lives or dies.

### 5. Peer scoring happens while contestants are still in a blind configuration

The brief says Round 1 is blind and Round 2 contestants read `FIELD-AT-ROUND-1.md` rather than peer directories. But the peer scoring (section 8 of the brief) doesn't specify whether scoring happens in Round 2 or in a separate phase. The INDEX.md shows Phase 4 as "Mutual peer scoring" which follows Round 2 — so contestants will have seen `FIELD-AT-ROUND-1.md` before scoring. That's the right order. I flag this only so the orchestrator confirms that peer scoring happens AFTER Round 2 completion, not in between Round 1 loops. If scoring happens mid-round, the blind rule breaks.

---

## One thing about this assignment that I want to name

The weight of this contest is real. GL is homeless and building a business that needs to work. This tool is not a speculative feature — it's a potential income driver for Jeff and a proof point for BBC's agency model. Treating the contest as an abstract design exercise would be a register mismatch. I'm carrying that context into every loop. If a contestant produces something beautiful that wouldn't actually move a real customer toward an inquiry, I'll name it.

---

## Ready

I'm ready to receive the first SendMessage when Round 1 contestants start completing their work. Send me:
- Which contestant number
- Whether this is loop 1, 2, or 3 for that contestant
- What phase they're in (Round 1 or Round 2)
- What their current files look like (or a summary of their RESEARCH-NOTES.md and REASONING.md so I can read before coaching)

I'll write my loop note to `contestant-{N}/PROXY-LOOP-{round}-{n}.md` and signal when it's done.
