# Locally Twisted — Business Policies

Canonical source for Locally Twisted's business rules. These policies are platform-agnostic — they describe how the business works, not how any system implements them.

Drives:
- **Customer-facing copy** — website FAQ, refund policy page, booking confirmation emails, pricing calculator
- **Backend logic** — when deposits are collected, balance reminders, tax calculations, late fees, travel fee detection
- **Contract templates** — attorney-prepared from `legal-interview-answers.md`

## Files

| File | What it covers |
|------|---------------|
| [legal-interview-answers.md](legal-interview-answers.md) | Master document — Jeff Kimber's answers from the legal interview sessions (2026-04-22 + 2026-04-23). Contract scope, signing model, payment terms, cancellation, scope of services. **Sufficient for an attorney to draft a v1 Client Event Contract.** |
| [pricing-formula.md](pricing-formula.md) | Per-artist pricing for balloon twisting and face painting; the "no combination discount" rule and its quality-commitment framing |
| [deposits.md](deposits.md) | Deposit structure by client type and service; balance-due timing |
| [service-area.md](service-area.md) | Free service zone (Davis / Weber / Salt Lake / Utah counties); travel fee outside |
| [tax.md](tax.md) | Utah sales tax behavior — city-based, calculated at checkout, ~7.25% combined rate |
| [theme-and-character-rules.md](theme-and-character-rules.md) | "Any character, any request" — no theme limits on artist services; brand differentiator |

## Open items

- **Parts 3-7 of the legal interview were skipped** because Jeff hit his limit. Attorney has enough for a v1 draft. Revisit only if attorney flags specific gaps.
- **Travel fee rate** outside the four free counties is not yet set — currently negotiated case-by-case until Jeff sets a flat rate or per-mile.
- **Sales tax classification for SERVICES** (twisting / face painting) — open question; needs Utah Tax Commission ruling or CPA consultation before launch.
- **COI PDF** — Jeff to email his insurance agent for the certificate.
- **Cleanup rules for decor jobs** — skipped in interview Part 2D; needs a separate conversation with Jeff before contract finalization.
