# /corporate-events — Design Notes

## Audience

Marketing teams, brand managers, event coordinators at corporations, franchise operators, and AP contacts who need to invoice a professional vendor. Buyer posture: brand-safe, on-color, repeatable, professional.

Key concern for this buyer: "Will this vendor embarrass me in front of my team / my brand / my boss?" The page must answer that without being defensive about it.

## Structural Decision

8 sections:
1. Hero — fullbleed, corporate logo arch photo
2. Proof bar — slate blue, 4 pillars (horizontal layout at tablet+, left-aligned icon+text at mobile)
3. Case intro — warm-white, editorial heading
4. Case cards — 3-up, each anchored to a real named-client cluster
5. Gallery strip — visual-field, 6 images
6. Client roster — stone, 30 chip list
7. Services — two-column, text + bulleted service types
8. CTA — ink/dark, with AP-specific framing

## Why Slate Blue for the Proof Bar

Slate Blue (#2F3A4A) is the corporate secondary dark — defined in the style guide for "corporate secondary dark, cards, filters, muted UI panels." This is the right surface for a corporate proof bar: serious but not ink-heavy. Avoids two adjacent dark sections (Authority band at ink → Proof bar at slate blue creates visual step-down, not repetition).

## Hero

- Background: `corporate-logo-arch.webp` — a branded arch is exactly what a corporate buyer is imagining
- Lede addresses the three corporate buyer concerns in order: brand colors, professionalism, invoiceability
- CTA: `/contact?intent=corporate` — prefills corporate context
- Mobile hero text is readable: gradient covers left side heavily

## Proof Bar

The four pillars are designed for a procurement-minded reader:
- "Brand-Safe" → color accuracy, not aesthetic opinion
- "Trusted Partner" → repeat engagements = reliability
- "Professional" → invoice-ready + insurance docs = vendor management
- "Clean Install" → no surprises on event day = not a liability

Pillar layout: stacked icon+text at mobile; side-by-side at tablet (matching home.py's responsive pattern for similar grids).

## Case Studies

Three cases cover the three biggest corporate segments in the roster:
1. Broadcast media (KSL, KUTV, FOX13) — timing-critical, on-air visible
2. Financial institutions (Zions, AFCU, Morgan Stanley, Fidelity) — conservative brand, professional context
3. National restaurant chains (Chick-Fil-A, Texas Roadhouse, Applebee's, Chili's) — franchise standards, repeatable

Each case body hits a specific pain point for that segment.

## Gallery

6 images covering corporate work:
- 3 from optimized portfolio (logo arch, weberstock photo op, WSU arch)
- 3 from Odoo source: Logo arch (themed decor), IHC latex-free columns (healthcare relevant), Weberstock organic garland

The Odoo-source images need full-path references — implementation phase handles copy.

## Service Note

Two-column at desktop (copy left, service grid right) — efficient use of space, professional layout.
Service list grid is 2-column — matches balanced-collections guidance (8 items = 4+4 or 2×4).
"Latex-free options available" is a specific, meaningful differentiator for IHC, Mountain Star Medical, and any healthcare corporate buyer.

## Client Roster

30 clients in chips. Conservative chip styling (white/55% opacity on stone, brass border) — feels like a vendor credential table, not a celebration.

## CTA

Ink ground (#0A0A0B) — darkest surface, used for closing authority.
"A free quote includes the install scope, color confirmation, and pricing — enough for a purchase order or budget approval." — This is the most corporate-buyer-specific CTA copy on any of the four pages. It names AP language directly.

## Accessibility

- One H1 per page
- Headings: H1 → H2 (proof bar, labeled via `id`) → H2 (cases intro) → H3 (case cards) → H2 (clients) → H2 (services) → H2 (CTA)
- Decorative icons: `aria-hidden="true"`
- Gallery: `aria-label`
- Client list: `aria-label`
- Service list: `aria-label`
- CTAs: min 48px height
- Focus-visible states on all interactive elements
