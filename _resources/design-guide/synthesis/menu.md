# Menu & IA — Synthesis Design

## IA Principle

This site is 95% inquiry, 5% shop. The navigation foregrounds *Work* (look book → inquiry engine) and gives *Services* its own door (D3's key insight: balloon twisting customers are a different audience from large-event decor customers — they shouldn't have to navigate the look book to find it). *Shop* is findable, not foregrounded.

---

## Information Architecture Tree

```
TOP-LEVEL NAV (sticky horizontal top nav — NOT D5's left-rail)
├── Work              ← Look Book + mood configurator
├── Services          ← Balloon Twisting + Face Painting
├── Shop              ← Take-home items (5–20 SKUs)
└── Contact           ← Inquiry form + phone + location

ON-PAGE (not in nav bar)
├── Brand story       ← Section on landing page (not a separate /about)
└── Delivery area     ← Footer link + /delivery-area static page

FOOTER ONLY
├── FAQ
├── Delivery area
├── Accessibility
├── Privacy
└── Instagram

NOT IN NAV
├── /inquire          ← Reached via "Tell us what you're imagining" CTAs
│                        and configurator submit — never in nav
├── /cart             ← Reached via Shop; not a nav item
└── /checkout         ← Pure checkout flow, no nav competition
```

### Why this IA

**Work is first.** The look book drives 95% of revenue via inquiry. Everything points there.

**Services is second, not buried.** Birthday parents and corporate HR managers planning a company picnic are looking for a balloon twisting entertainer — they should not have to scan "Look Book" to find it. Giving it a top-level position means every visitor type has a clear door.

**Shop is third.** Findable, not competing. The customers who want bouquets and centerpieces know to look for it. The customers who want a full event installation are steered toward inquiry by the "Custom event? Start a conversation" cross-link on the shop page.

**Contact is fourth.** Not hidden, not promoted. The phone number does more work than a "Contact" page — it lives persistently in the nav right, visible at all times.

---

## Desktop Nav Bar

```
┌────────────────────────────────────────────────────────────────────────┐
│  Locally Twisted          Work   Services   Shop        (801) 285-0860 │
│  Est. 1998 · Wasatch Front                          [ Tell us about yours ] │
└────────────────────────────────────────────────────────────────────────┘
```

**Design notes:**
- Wordmark: DM Serif Display, Near Black — not all-caps, not italic. LT brand.
- Sub-caption "Est. 1998 · Wasatch Front": Raleway 600, 0.10em tracking, uppercase, Soft Gray. Hidden on mobile (<992px), visible on desktop.
- Nav links: Raleway 600, 0.06em tracking, uppercase, Near Black. Bottom-border underline on active/hover.
- Phone: Raleway 500, Soft Gray. Visible from 640px+.
- "Tell us about yours" CTA: Teal fill button (the only teal element in the nav). DM Serif Display or Raleway 600, White text.
- Hamburger: visible below 768px, hidden at 768px+.
- Sticky on scroll. Gains box-shadow at scroll > 60px (starts flat on fresh load).
- Background stays White — no transparency-to-opaque transition needed since ground is white.

---

## Mobile Menu Structure

**Collapsed (hamburger visible):**
```
┌────────────────────────────────┐
│ Locally Twisted            ≡   │
└────────────────────────────────┘
```

**Expanded (full-screen drawer, slides in from right):**
```
┌────────────────────────────────┐
│                         Close ✕│
│                                │
│  Work                          │
│  Services                      │
│  Shop                          │
│  Contact                       │
│                                │
│  ─────────────────────────     │
│                                │
│  (801) 285-0860                │
│  [ Tell us about yours    ]    │
│                                │
│  Est. 1998 · Wasatch Front     │
└────────────────────────────────┘
```

**Mobile menu notes:**
- Full-screen overlay, White background, Near Black type — consistent with LT's light-ground system (NOT D3's near-black drawer)
- Nav links: DM Serif Display at 2.5rem — large enough to be unmistakable on phone, editorial register
- Phone: Raleway 600, large, full-width tap target (minHeight 44px)
- "Tell us about yours" CTA: Teal fill button, full-width
- Provenance: Raleway 600, 0.10em tracking, Soft Gray, bottom of drawer
- Slides in with `transform: translateX(100%) → translateX(0)`, respects `prefers-reduced-motion`

---

## Footer Organization

Footer background: Soft Blue (`#C3DCF3`) per STYLE-GUIDE.md

```
┌──────────────────────────────────────────────────────────────┐
│  Locally Twisted              Work         Services    Shop   │
│  Custom balloon decor,        Look Book    Twisting    Bouqts │
│  Wasatch Front.               Weddings     Face Paint  Cups   │
│  In the work since 1998.      Corporate    Get a quote Ready  │
│                               Birthdays                       │
│  ────────────────────────────────────────────────────────     │
│  © 2026 Locally Twisted    Instagram  Delivery  Accessibility  │
│                                        area       Privacy     │
└──────────────────────────────────────────────────────────────┘
```

**Footer notes:**
- Column heads: Raleway 600, uppercase, Near Black
- Links: Raleway 400, Near Black (for contrast on Soft Blue)
- Brand name: DM Serif Display, larger, Near Black
- Social links: min-height 44px, open in new tab with screen-reader hint
- "Accessibility" in copyright bar: required by STYLE-GUIDE.md

---

## The Phone Number Rule (from D3, carried forward)

`(801) 285-0860` is in the nav always. It is the most important single UI element for birthday parents and corporate coordinators — the people most likely to call rather than fill a form. A persistent phone number in the top-right nav:

- Serves mobile users who want to tap-to-call without navigating
- Signals that a real person is reachable
- Removes the "I wonder if they're actually responsive" objection before it forms

It should not be in a footer. It should not be behind a "Contact" click. It should be visible on every page, at all screen sizes where space allows (640px+).
