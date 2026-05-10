# Decision Brief — Accessibility Statement

**Status:** Awaiting GL decision before Phase 1 Slice 6 (accessibility page build).

## The question

GL flagged: "I've heard that having an accessibility statement can be a bad idea sometimes because people will use that against small companies in lawsuits. I don't know the definitive answer on that."

## The legal landscape (as of 2026)

**ADA Title III applies to "places of public accommodation,"** which courts have repeatedly held includes the websites of businesses with physical locations (LT has a storefront at 8969 S 2700 W, West Jordan, UT — so this applies).

**The duty exists whether or not LT publishes a statement.** Skipping the statement does not remove the obligation; it removes a *signal* of the obligation.

**The plaintiff-side pattern most active against small businesses:**
- Scrape websites for accessibility statements that promise specific WCAG conformance ("we are AA compliant," "this site meets WCAG 2.1 Level AA")
- Test the site for any conformance gap
- File a demand letter or lawsuit using the gap as the cause of action — the *promise* in the statement creates a contract / warranty claim that's easier to prove than the underlying ADA claim

**The mistake the pattern preys on** is publishing a specific conformance promise without actually maintaining conformance. The promise itself becomes the liability.

## Three options

### Option A — Publish a detailed AA conformance claim

Example: "This site conforms to WCAG 2.1 Level AA. We test against [specific tools]…"

Pros:
- Sounds professional
- Clear commitment customers can rely on

Cons:
- **Creates a warranty / contract claim** if any AA criterion fails
- Requires ongoing audit + remediation infrastructure
- Conformance can drift silently with every CMS update — promise becomes false without anyone noticing
- This is the option plaintiff-side firms specifically target

### Option B — Publish a brief, intent-only statement with a working contact (recommended)

Example structure:
- One paragraph naming LT's commitment to keeping the site usable for everyone
- A working accessibility contact (email + phone) for reporting barriers
- A note that we welcome feedback and will address issues
- **NO specific WCAG conformance promise. NO "AA compliant" badge.**

Pros:
- Demonstrates good faith without creating a warranty claim
- The working contact channel is itself defensive — courts and demand letters look favorably on businesses that have an accessible remediation path
- Matches the brand voice ("Quiet Confidence" — invite, don't push)
- Maintenance burden is low: keep the contact channel working
- Compatible with actually meeting WCAG 2.1 AA (which is the right thing to do regardless)

Cons:
- Less impressive-sounding than Option A
- Requires monitoring the accessibility contact channel

### Option C — Skip the published statement entirely

Pros:
- Simplest

Cons:
- **Skipping the statement does NOT remove the legal obligation** — that's a misconception
- Skipping signals indifference; some courts and plaintiff-side firms read the absence of any statement as worse than a brief one
- LT has a public-facing physical location; the duty applies regardless
- Some accessibility software (NVDA, JAWS) flag pages that lack standard remediation links — affects user experience for users with disabilities

## Claude's strong recommendation

**Option B + actually meet WCAG 2.1 AA on the live site.**

The combination is real protection:
- The brief intent-only statement creates no warranty claim
- The working contact channel is documented good faith
- Actual WCAG 2.1 AA conformance means there's nothing to sue over anyway

The style guide already targets WCAG 2.1 AA throughout (color contrast tables, focus indicators, touch targets, motion preferences, semantic structure). Building Phase 1 to actually conform is a small additional discipline at design time — much cheaper than retrofitting later.

**Critical:** this is general guidance from public-information patterns, not legal advice. **Before Phase 6 cutover, run the chosen statement past an actual Utah small-business attorney** for sign-off. Cheap insurance.

## Suggested statement text (if GL picks Option B)

> **Accessibility at Locally Twisted**
>
> We work to keep our website usable for everyone, including people who navigate with screen readers, keyboard-only input, voice controls, or other assistive technology.
>
> If you run into a barrier on this site — anything that gets in the way of finding what you need or getting in touch — please let us know. We want to hear from you.
>
> Reach us at **legal@locallytwisted.com** or **(801) 285-0860**, and we'll work with you to provide what you need and to fix the barrier for the next person.

(Email needs to be set up and monitored. Phone is the existing business line.)

## What this affects in Phase 1

- **Slice 6 (Accessibility + Refund + FAQ pages):** the accessibility page text depends on this decision.
- **Slice 1 (Brand foundation) + every other slice:** WCAG 2.1 AA conformance baked in regardless of which statement option, per style guide. This is non-negotiable design discipline.

## What I need from GL

Pick A, B, or C. (Strong recommendation: B.)

If B, I'll draft the statement using the suggested text above and we'll review together.
