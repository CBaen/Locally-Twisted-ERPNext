"""Portfolio controller — `/portfolio` route.

Slice 7 of Phase 1 — the visual heart of the site. Per
`.planning/decisions/site-shape.md`, the portfolio is the primary "browse"
surface — full portfolio organized by event type, with a secondary product-type
filter for visitors thinking about a specific kind of decor.

Architecture:
- Hero band -> sandstone divider -> filter row (dual-axis: event x product)
  -> floating photo reel -> closing CTA. Mirrors the homepage's full-bleed
  band pattern while letting the portfolio intentionally break out of boxed
  page-card behavior.
- Photos are the product proof on this route. The reel preserves full source
  aspect ratios, uses left/right/center placement metadata, and avoids captions
  or card text covering the work.
- Filter logic is client-side JS only (no whitelisted endpoint, no AJAX).
  Reads `data-event-type` and `data-category` on each card; AND-logic
  intersection between axes; "All" = no filter on that axis.
- URL state via query strings: `/portfolio?event=weddings&category=balloon-arches`.
  Server-readable so per-filter <title> + meta description vary; crawlable;
  share-able. Backward-compat with hash fragments (`/portfolio#balloon-arches`)
  from the homepage's Custom Creations tile links.
- Schema markup: page-level ItemList JSON-LD, emitted from get_context as a
  Python dict and json.dumps'd in the template.

Out of scope for this slice (deferred):
- The "Build your palette" 4-step configurator from the synthesis mockup —
  that's the future Design Studio (post-Phase-1 per site-shape.md).
- Sub-routes like `/portfolio/<slug>` for full case-study pages — Slice 8.
- Custom DocType for Portfolio Items — overkill at this data volume.
"""
import json

import frappe

no_cache = 1
sitemap = 1


# Event-type filter pills (the primary axis per site-shape.md and PLAN.md).
# "All" is rendered first by the template; not in this list.
EVENT_TYPES = [
    {"slug": "corporate", "name": "Corporate"},
    {"slug": "schools", "name": "Schools"},
    {"slug": "civic-community", "name": "Civic & Community"},
    {"slug": "venues-public", "name": "Venues & Public Installs"},
    {"slug": "private-events", "name": "Private Events"},
]


# Product-type filter dropdown (the secondary axis). Slugs MUST match the
# homepage's CUSTOM_CATEGORIES (home.py) so the homepage's tile links
# resolve to the correct filtered view. Eight categories per GL 2026-04-28
# (Centerpieces + Custom Sculptures added; Garlands replaces Organic Garlands).
# Centerpieces and Custom Sculptures have no photos yet — filtering to
# them will render the empty state until Jeff's archive surfaces examples.
CATEGORIES = [
    {"slug": "balloon-arches", "name": "Balloon Arches"},
    {"slug": "columns", "name": "Columns"},
    {"slug": "garlands", "name": "Garlands"},
    {"slug": "picture-perfect-backdrops", "name": "Picture Perfect Backdrops"},
    {"slug": "balloon-drops", "name": "Balloon Drops"},
    {"slug": "balloon-bouquets", "name": "Balloon Bouquets"},
    {"slug": "centerpieces", "name": "Centerpieces"},
    {"slug": "custom-sculptures", "name": "Custom Sculptures"},
]


# The gallery. Each item is dual-axis-tagged (event_type + category) to drive
# the client-side filter. Filenames map to /assets/locally_twisted/images/portfolio/.
# Adding items = appending dicts; restart backend (Python module cache).
#
# This 15-item cohort hits 5 of 6 categories × all 5 event types as a coverage
# demo. The 6th category (Balloon Drops) is intentionally empty here so the
# empty-state UX is provable — filter to "Balloon Drops" and confirm the
# empty message renders. Will populate as Jeff's archive surfaces drop photos.
GALLERY_ITEMS = [
    {
        "slug": "corporate-logo-arch",
        "title": "Corporate Brand Logo Arch",
        "category": "balloon-arches",
        "event_type": "schools",
        "year": "2024",
        "image": "corporate-logo-arch.png",
        "alt": "Custom corporate brand logo balloon arch installed at a company event entrance",
    },
    {
        "slug": "corporate-weberstock-photo-opt",
        "title": "Weberstock Festival Photo Backdrop",
        "category": "picture-perfect-backdrops",
        "event_type": "corporate",
        "year": "2025",
        "image": "corporate-weberstock-photo-opt.png",
        "alt": "Large balloon photo backdrop with festival branding for the Weberstock corporate event",
    },
    {
        "slug": "corporate-wsu-arch-bouquets",
        "title": "WSU Welcome Bouquets",
        "category": "balloon-bouquets",
        "event_type": "corporate",
        "year": "2024",
        "image": "corporate-wsu-arch-bouquets.png",
        "alt": "Helium balloon bouquets and an arch styled in Weber State University colors at a campus event",
    },
    {
        "slug": "wedding-floral-half-arch",
        "title": "Floral Half-Arch with White Blooms",
        "category": "picture-perfect-backdrops",
        "event_type": "private-events",
        "year": "2024",
        "image": "wedding-floral-half-arch.png",
        "alt": "Wedding ceremony half-arch combining balloons and white floral arrangements",
    },
    {
        "slug": "wedding-foil-heart-arch",
        "title": "Foil Heart Wedding Arch",
        "category": "balloon-arches",
        "event_type": "private-events",
        "year": "2024",
        "image": "wedding-foil-heart-arch.png",
        "alt": "Wedding arch composed of foil heart balloons in soft metallic tones",
    },
    {
        "slug": "wedding-organic-half-arch",
        "title": "Organic White Floral Half-Arch",
        "category": "garlands",
        "event_type": "private-events",
        "year": "2025",
        "image": "wedding-organic-half-arch.png",
        "alt": "Soft organic balloon garland forming a half-arch with white flower accents at a wedding ceremony",
    },
    {
        "slug": "birthday-smurfs-arch",
        "title": "Smurfs Birthday Arch",
        "category": "balloon-arches",
        "event_type": "private-events",
        "year": "2024",
        "image": "birthday-smurfs-arch.png",
        "alt": "Smurfs-themed balloon arch in blue and white at a child's birthday party",
    },
    {
        "slug": "birthday-pirate-column",
        "title": "Pirate-Themed Balloon Column",
        "category": "columns",
        "event_type": "private-events",
        "year": "2023",
        "image": "birthday-pirate-column.jpg",
        "alt": "Custom pirate-themed balloon column at a children's birthday party",
    },
    {
        "slug": "birthday-dolphin-backdrop",
        "title": "Under-the-Sea Dolphin Backdrop",
        "category": "picture-perfect-backdrops",
        "event_type": "private-events",
        "year": "2024",
        "image": "birthday-dolphin-backdrop.png",
        "alt": "Ocean-themed birthday photo backdrop featuring a balloon dolphin",
    },
    {
        "slug": "birthday-balloon-bouquets",
        "title": "Birthday Helium Bouquets",
        "category": "balloon-bouquets",
        "event_type": "private-events",
        "year": "2025",
        "image": "birthday-balloon-bouquets.png",
        "alt": "Five-balloon helium bouquets in birthday colors arranged for a party table",
    },
    {
        "slug": "school-back-to-school-stage",
        "title": "Back-to-School Stage Display",
        "category": "picture-perfect-backdrops",
        "event_type": "schools",
        "year": "2024",
        "image": "school-back-to-school-stage.png",
        "alt": "Large balloon stage display for a school back-to-school assembly",
    },
    {
        "slug": "school-grad-garland",
        "title": "Graduation Organic Garland",
        "category": "garlands",
        "event_type": "schools",
        "year": "2025",
        "image": "school-grad-garland.png",
        "alt": "Organic balloon garland in graduation colors framing a school ceremony stage",
    },
    {
        "slug": "seasonal-easter-rabbit-arch",
        "title": "Easter Rabbit-Ears Arch",
        "category": "balloon-arches",
        "event_type": "civic-community",
        "year": "2024",
        "image": "seasonal-easter-rabbit-arch.png",
        "alt": "Twenty-foot Easter balloon arch with sculpted rabbit ears at the top",
    },
    {
        "slug": "seasonal-halloween-tombstone",
        "title": "Halloween Tombstone Backdrop",
        "category": "picture-perfect-backdrops",
        "event_type": "venues-public",
        "year": "2024",
        "image": "seasonal-halloween-tombstone.png",
        "alt": "Halloween balloon backdrop styled as a graveyard with sculpted tombstones",
    },
    {
        "slug": "seasonal-pride-columns",
        "title": "Pride Rainbow Columns",
        "category": "balloon-arches",  # rainbow columns are paired arch-y; could also be columns
        "event_type": "civic-community",
        "year": "2024",
        "image": "seasonal-pride-columns.png",
        "alt": "Pair of rainbow balloon columns for a Pride event entrance",
    },
]
# Re-tag the Pride one to columns category (more accurate).
GALLERY_ITEMS[14]["category"] = "columns"


PORTFOLIO_DISPLAY_ORDER = [
    "corporate-logo-arch",
    "corporate-wsu-arch-bouquets",
    "wedding-floral-half-arch",
    "birthday-dolphin-backdrop",
    "corporate-weberstock-photo-opt",
    "wedding-foil-heart-arch",
    "wedding-organic-half-arch",
    "birthday-smurfs-arch",
    "seasonal-easter-rabbit-arch",
    "school-grad-garland",
    "seasonal-pride-columns",
    "birthday-pirate-column",
    "seasonal-halloween-tombstone",
    "birthday-balloon-bouquets",
    "school-back-to-school-stage",
]
_portfolio_order = {slug: index for index, slug in enumerate(PORTFOLIO_DISPLAY_ORDER)}
GALLERY_ITEMS.sort(key=lambda item: _portfolio_order.get(item["slug"], len(_portfolio_order)))


# Portfolio photo-reel metadata. This translates the approved reference's
# left / right / center floating-photo reel into deterministic Frappe data.
# Dimensions are the real source asset dimensions, used to preserve natural
# aspect ratio and prevent the old cropped-card behavior.
PORTFOLIO_REEL_META = {
    "corporate-logo-arch": {"w": 4032, "h": 3024, "side": "left", "scale": 0.96},
    "corporate-wsu-arch-bouquets": {"w": 4032, "h": 3024, "side": "right", "scale": 0.92},
    "wedding-floral-half-arch": {"w": 4032, "h": 3024, "side": "left", "scale": 0.88},
    "birthday-dolphin-backdrop": {"w": 4032, "h": 3024, "side": "right", "scale": 0.96},
    "corporate-weberstock-photo-opt": {"w": 4032, "h": 3024, "side": "center", "scale": 1.0},
    "wedding-foil-heart-arch": {"w": 4032, "h": 3024, "side": "left", "scale": 0.9},
    "wedding-organic-half-arch": {"w": 3024, "h": 4032, "side": "right", "scale": 0.74},
    "birthday-smurfs-arch": {"w": 4032, "h": 3024, "side": "left", "scale": 0.92},
    "seasonal-easter-rabbit-arch": {"w": 4032, "h": 3024, "side": "right", "scale": 0.96},
    "school-grad-garland": {"w": 4032, "h": 3024, "side": "center", "scale": 1.0},
    "seasonal-pride-columns": {"w": 4032, "h": 3024, "side": "left", "scale": 0.9},
    "birthday-pirate-column": {"w": 1440, "h": 1800, "side": "right", "scale": 0.72},
    "seasonal-halloween-tombstone": {"w": 1284, "h": 1595, "side": "left", "scale": 0.72},
    "birthday-balloon-bouquets": {"w": 4032, "h": 3024, "side": "right", "scale": 0.84},
    "school-back-to-school-stage": {"w": 746, "h": 573, "side": "left", "scale": 0.78},
}

for item in GALLERY_ITEMS:
    item.update(PORTFOLIO_REEL_META.get(item["slug"], {}))


def _filter_label(items, event_slug, category_slug):
    """Build a human-readable label for the page title + meta description."""
    event_name = next((e["name"] for e in EVENT_TYPES if e["slug"] == event_slug), None)
    category_name = next((c["name"] for c in CATEGORIES if c["slug"] == category_slug), None)
    if event_name and category_name:
        return f"{event_name} {category_name}"
    return event_name or category_name or ""


def _build_itemlist_jsonld(items):
    """Page-level ItemList schema for SEO. Validates against schema.org."""
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Locally Twisted Portfolio",
        "description": "Custom balloon decor installations across Utah's Wasatch Front.",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": item["title"],
                "image": f"/assets/locally_twisted/images/portfolio/{item['image']}",
                "url": f"/portfolio?category={item['category']}",
            }
            for idx, item in enumerate(items)
        ],
    }


PAGE_CSS = """
/* ======================================================================
 * PORTFOLIO — /portfolio — Slice 7
 * BEM blocks: lt-portfolio-hero, lt-portfolio-filter, lt-portfolio-grid,
 *             lt-portfolio-card, lt-portfolio-empty
 * Reuses from lt-theme.css: --lt-* color tokens, .lt-band--sandstone,
 * .lt-divider, .lt-cta, and the .lt-fullbleed primitive (defined inline
 * here too for self-containment per the homepage pattern).
 * ====================================================================== */

/* --- Visually hidden (screen-reader only) --------------------------- */
.visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* --- Full-bleed helper (mirrors homepage) --------------------------- */
.lt-fullbleed {
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
}

/* --- Hero band ------------------------------------------------------- */
.lt-portfolio-hero {
    background-color: var(--lt-warm-tint);
    padding: 4rem 1.5rem 3.5rem;
}
.lt-portfolio-hero__inner {
    max-width: 1100px;
    margin: 0 auto;
    text-align: left;
}
.lt-portfolio-hero__eyebrow {
    font-family: 'Lato', sans-serif;
    font-size: 0.8125rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
    margin: 0 0 1rem;
}
.lt-portfolio-hero__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 2.75rem;
    line-height: 1.05;
    color: var(--lt-near-black);
    margin: 0 0 1.25rem;
}
@media (min-width: 768px) {
    .lt-portfolio-hero__title { font-size: 3.5rem; }
}
@media (min-width: 1200px) {
    .lt-portfolio-hero__title { font-size: 4rem; }
}
.lt-portfolio-hero__body {
    font-family: 'Lato', sans-serif;
    font-size: 1.0625rem;
    line-height: 1.55;
    color: var(--lt-near-black);
    max-width: 580px;
    margin: 0;
}

/* --- Sandstone divider (between hero and filter) ------------------ */
/* Saturated sandstone (#F4DFD7), structural separator at the same
 * weight as the homepage's 3-dot dividers in their respective bands. */
.lt-portfolio-ribbon {
    height: 28px;
    background-color: var(--lt-sandstone-accent);
}

/* --- Filter row ------------------------------------------------------ */
.lt-portfolio-filter {
    background-color: var(--lt-white);
    padding: 1.5rem 1rem 1.25rem;
    border-bottom: 1px solid #f0f0f0;
}
.lt-portfolio-filter__inner {
    max-width: 1300px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
@media (min-width: 992px) {
    .lt-portfolio-filter__inner {
        flex-direction: row;
        align-items: center;
        gap: 1.5rem;
    }
}

/* Pill chips: horizontal-scroll on mobile, inline on desktop. */
.lt-portfolio-filter__pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    overflow-x: visible;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    scroll-snap-type: none;
    padding: 0.25rem 0;
    margin: 0;
    list-style: none;
}
.lt-portfolio-filter__pills::-webkit-scrollbar { display: none; }
.lt-portfolio-filter__pill {
    flex: 0 0 auto;
    scroll-snap-align: start;
}
.lt-portfolio-filter__pill button {
    appearance: none;
    background: transparent;
    border: 1px solid #d6d6d6;
    border-radius: 999px;
    padding: 0.5rem 1rem;
    font-family: 'Lato', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--lt-near-black);
    cursor: pointer;
    white-space: normal;
    min-height: 40px;
    transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}
.lt-portfolio-filter__pill button:hover {
    border-color: var(--lt-near-black);
}
.lt-portfolio-filter__pill button:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-portfolio-filter__pill button[aria-pressed="true"] {
    background-color: var(--lt-near-black);
    border-color: var(--lt-near-black);
    color: var(--lt-white);
}

/* Category dropdown */
.lt-portfolio-filter__dropdown {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    flex: 0 0 auto;
}
.lt-portfolio-filter__dropdown label {
    font-family: 'Lato', sans-serif;
    font-size: 0.8125rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
    margin: 0;
}
.lt-portfolio-filter__dropdown select {
    appearance: none;
    -webkit-appearance: none;
    background-color: var(--lt-white);
    border: 1px solid #d6d6d6;
    border-radius: 0.375rem;
    padding: 0.5rem 2rem 0.5rem 0.875rem;
    font-family: 'Lato', sans-serif;
    font-size: 0.875rem;
    color: var(--lt-near-black);
    cursor: pointer;
    min-height: 40px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' fill='none' stroke='%23222' stroke-width='1.6'%3E%3Cpath d='M2 4 L6 8 L10 4'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.625rem center;
    background-size: 12px;
}
.lt-portfolio-filter__dropdown select:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}

/* Count + clear */
.lt-portfolio-filter__meta {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.lt-portfolio-filter__count {
    font-family: 'Lato', sans-serif;
    font-size: 0.8125rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
}
.lt-portfolio-filter__clear {
    appearance: none;
    background: transparent;
    border: none;
    padding: 0.25rem 0.5rem;
    font-family: 'Lato', sans-serif;
    font-size: 0.8125rem;
    color: var(--lt-near-black);
    text-decoration: underline;
    cursor: pointer;
    visibility: hidden;
}
.lt-portfolio-filter__clear:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-portfolio-filter[data-filtered="true"] .lt-portfolio-filter__clear {
    visibility: visible;
}

/* --- Gallery grid --------------------------------------------------- */
.lt-portfolio-grid {
    background-color: var(--lt-near-white);
    padding: 3rem 1rem 4rem;
}
.lt-portfolio-grid__inner {
    max-width: 1300px;
    margin: 0 auto;
}
.lt-portfolio-grid__cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}
@media (min-width: 768px) {
    .lt-portfolio-grid__cards {
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
    }
}
@media (min-width: 1400px) {
    .lt-portfolio-grid__cards {
        grid-template-columns: repeat(4, 1fr);
        gap: 1.75rem;
    }
}

/* --- Portfolio card (button — opens lightbox modal on click) -------- */
.lt-portfolio-card {
    /* Button reset (cards are <button> elements that open the modal) */
    appearance: none;
    -webkit-appearance: none;
    border: none;
    padding: 0;
    margin: 0;
    font: inherit;
    color: inherit;
    text-align: left;
    width: 100%;
    cursor: pointer;
    /* Card visual */
    background-color: var(--lt-white);
    border-radius: 0.5rem;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: block;
}
.lt-portfolio-card:hover,
.lt-portfolio-card:focus-visible {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
    outline: none;
}
.lt-portfolio-card:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-portfolio-card[hidden] { display: none !important; }

/* Inner spans need display:block since the card is a <button> wrapping spans
 * (HTML spec: <button> can only contain phrasing content). */
.lt-portfolio-card__image,
.lt-portfolio-card__body,
.lt-portfolio-card__category,
.lt-portfolio-card__title { display: block; }

.lt-portfolio-card__image {
    width: 100%;
    aspect-ratio: 4 / 5;
    background-color: var(--lt-warm-tint);
    background-size: cover;
    background-position: center;
}
.lt-portfolio-card__body {
    padding: 1rem 1.125rem 1.25rem;
}
@media (min-width: 768px) {
    .lt-portfolio-card__body { padding: 1.125rem 1.375rem 1.5rem; }
}
.lt-portfolio-card__category {
    font-family: 'Lato', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--lt-soft-gray);
    margin: 0 0 0.375rem;
}
.lt-portfolio-card__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.125rem;
    color: var(--lt-near-black);
    margin: 0;
    line-height: 1.25;
}
@media (min-width: 768px) {
    .lt-portfolio-card__title { font-size: 1.25rem; }
}

/* --- Empty state ---------------------------------------------------- */
.lt-portfolio-empty {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3.5rem 1rem;
    display: none;
}
.lt-portfolio-grid[data-empty="true"] .lt-portfolio-empty { display: block; }
.lt-portfolio-empty__heading {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.75rem;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
}
.lt-portfolio-empty__body {
    font-family: 'Lato', sans-serif;
    color: var(--lt-soft-gray);
    margin: 0 0 1.5rem;
    font-size: 1rem;
}
.lt-portfolio-empty__cta {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background-color: var(--lt-teal);
    color: var(--lt-white);
    text-decoration: none;
    border-radius: 0.375rem;
    font-family: 'Lato', sans-serif;
    font-weight: 600;
    font-size: 0.9375rem;
    min-height: 44px;
}
.lt-portfolio-empty__cta:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}

/* --- Closing CTA (mirrors homepage .lt-cta) ------------------------- */
.lt-cta {
    background-color: var(--lt-stone-accent, var(--lt-stone-tint));
    padding: 4rem 1rem 4.5rem;
    text-align: center;
}
.lt-cta__inner { max-width: 1200px; margin: 0 auto; }
.lt-cta__heading {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 2.5rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.15;
}
.lt-cta__body {
    font-family: 'Lato', sans-serif;
    font-size: 1.125rem;
    color: var(--lt-near-black);
    max-width: 620px;
    margin: 0 auto 1.75rem;
    line-height: 1.55;
}
.lt-cta__button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.95rem 2rem;
    background-color: var(--lt-teal);
    color: var(--lt-white);
    text-decoration: none;
    border-radius: 0.375rem;
    font-family: 'Lato', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    min-height: 48px;
}
.lt-cta__button:hover,
.lt-cta__button:focus-visible {
    background-color: #006666;
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
@media (min-width: 768px) { .lt-cta__heading { font-size: 3rem; } }

/* --- Lightbox modal -------------------------------------------------- */
.lt-portfolio-modal[hidden] { display: none !important; }
.lt-portfolio-modal {
    position: fixed;
    inset: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    animation: lt-portfolio-modal-fade 0.18s ease-out;
}
.lt-portfolio-modal__backdrop {
    position: absolute;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.85);
    cursor: zoom-out;
}
.lt-portfolio-modal__panel {
    position: relative;
    z-index: 1;
    max-width: min(94vw, 1200px);
    max-height: 92vh;
    background-color: var(--lt-white);
    border-radius: 0.5rem;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}
.lt-portfolio-modal__close {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    z-index: 2;
    appearance: none;
    -webkit-appearance: none;
    background-color: rgba(0, 0, 0, 0.55);
    color: var(--lt-white);
    border: none;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.5rem;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.15s ease;
}
.lt-portfolio-modal__close:hover {
    background-color: rgba(0, 0, 0, 0.85);
}
.lt-portfolio-modal__close:focus-visible {
    outline: 2px solid var(--lt-white);
    outline-offset: 2px;
    background-color: rgba(0, 0, 0, 0.85);
}
.lt-portfolio-modal__image {
    display: block;
    max-width: 100%;
    max-height: calc(92vh - 110px);
    object-fit: contain;
    background-color: var(--lt-near-white);
    margin: 0 auto;
}
.lt-portfolio-modal__caption {
    padding: 1rem 1.5rem 1.25rem;
    border-top: 1px solid #f0f0f0;
    background-color: var(--lt-white);
}
.lt-portfolio-modal__category {
    font-family: 'Lato', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--lt-soft-gray);
    margin: 0 0 0.375rem;
}
.lt-portfolio-modal__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.5rem;
    color: var(--lt-near-black);
    margin: 0;
    line-height: 1.2;
}
@keyframes lt-portfolio-modal-fade {
    from { opacity: 0; }
    to { opacity: 1; }
}
/* Body scroll lock while modal is open */
body.lt-modal-open { overflow: hidden; }

/* --- Reduced-motion: disable card hover-lift + modal fade ----------- */
@media (prefers-reduced-motion: reduce) {
    .lt-portfolio-card { transition: none; }
    .lt-portfolio-card:hover,
    .lt-portfolio-card:focus-visible { transform: none; }
    .lt-portfolio-modal { animation: none; }
    .lt-portfolio-modal__close { transition: none; }
}

/* Civic Celebration redesign for secondary editorial pages. */
.lt-portfolio-hero {
    background: linear-gradient(135deg, #0e2240 0%, #0a0a0b 100%);
    border-bottom: 10px solid #b31b34;
}
.lt-portfolio-hero__eyebrow,
.lt-portfolio-hero__title,
.lt-portfolio-hero__body {
    color: #faf7f2;
}
.lt-portfolio-hero__eyebrow,
.lt-portfolio-card__category,
.lt-portfolio-modal__category,
.lt-portfolio-filter__dropdown label,
.lt-portfolio-filter__count {
    color: #b31b34;
    font-weight: 800;
    letter-spacing: 0.14em;
}
.lt-portfolio-ribbon {
    background-color: #b31b34;
}
.lt-portfolio-filter {
    background-color: #faf7f2;
    border-bottom-color: rgba(14, 34, 64, 0.16);
}
.lt-portfolio-filter__pill button,
.lt-portfolio-filter__dropdown select {
    background-color: #fffdf9;
    border-color: rgba(14, 34, 64, 0.24);
    color: #0a0a0b;
    border-radius: 0.25rem;
}
.lt-portfolio-filter__pill button:hover,
.lt-portfolio-filter__dropdown select:hover {
    border-color: #0e2240;
}
.lt-portfolio-filter__pill button[aria-pressed="true"] {
    background-color: #0e2240;
    border-color: #0e2240;
    color: #faf7f2;
}
.lt-portfolio-filter__clear,
.lt-portfolio-card__title,
.lt-portfolio-empty__heading,
.lt-portfolio-modal__title,
.lt-cta__heading {
    color: #0e2240;
}
.lt-portfolio-grid {
    background-color: #f1e8dc;
}
.lt-portfolio-card,
.lt-portfolio-modal__panel {
    background-color: #fffdf9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-radius: 0.375rem;
    box-shadow: 0 16px 42px rgba(14, 34, 64, 0.1);
}
.lt-portfolio-card:hover,
.lt-portfolio-card:focus-visible {
    box-shadow: 0 22px 52px rgba(14, 34, 64, 0.18);
}
.lt-portfolio-card__image,
.lt-portfolio-modal__image {
    background-color: #d9c7b3;
}
.lt-portfolio-empty__body,
.lt-cta__body {
    color: rgba(10, 10, 11, 0.72);
}
.lt-portfolio-empty__cta,
.lt-cta__button {
    background-color: #b31b34;
    color: #faf7f2;
    border: 1px solid #b31b34;
    border-radius: 0.25rem;
}
.lt-portfolio-empty__cta:hover,
.lt-portfolio-empty__cta:focus-visible,
.lt-cta__button:hover,
.lt-cta__button:focus-visible {
    background-color: #0e2240;
    border-color: #0e2240;
    color: #faf7f2;
}
.lt-cta {
    background-color: #d9c7b3;
}
.lt-portfolio-modal__backdrop {
    background-color: rgba(10, 10, 11, 0.88);
}
.lt-portfolio-modal__caption {
    border-top-color: rgba(14, 34, 64, 0.14);
}
.lt-portfolio-modal__close {
    background-color: #0e2240;
}

/* --- Floating photo reel ------------------------------------------- */
.lt-portfolio-hero {
    background: #f8f4ed;
    border-bottom: 0;
    padding: clamp(4.5rem, 11vw, 9rem) clamp(1.25rem, 5vw, 5rem) clamp(3rem, 7vw, 6rem);
}
.lt-portfolio-hero__inner {
    max-width: 1180px;
}
.lt-portfolio-hero__eyebrow {
    color: #b31b34;
    margin-bottom: 1.5rem;
}
.lt-portfolio-hero__title {
    max-width: 920px;
    color: #151515;
    font-size: clamp(4rem, 10vw, 9.5rem);
    font-weight: 300;
    line-height: 0.86;
    letter-spacing: 0;
}
.lt-portfolio-hero__body {
    max-width: 640px;
    color: rgba(21, 21, 21, 0.68);
    font-size: clamp(1.05rem, 1.8vw, 1.35rem);
}
.lt-portfolio-ribbon {
    height: 1px;
    background: rgba(184, 154, 91, 0.38);
}
.lt-portfolio-filter {
    position: sticky;
    top: 0;
    z-index: 18;
    background: rgba(248, 244, 237, 0.94);
    border-top: 1px solid rgba(184, 154, 91, 0.24);
    border-bottom: 1px solid rgba(184, 154, 91, 0.3);
    padding: 0.85rem clamp(1rem, 4vw, 4rem);
    backdrop-filter: blur(18px);
}
.lt-portfolio-filter__inner {
    width: 100%;
    max-width: none;
    gap: 1rem;
}
.lt-portfolio-filter__pill button,
.lt-portfolio-filter__dropdown select {
    min-height: 44px;
    border-radius: 0;
    border-color: rgba(14, 34, 64, 0.24);
    background: #fffdf9;
    color: #0e2240;
    font-size: 0.75rem;
    font-weight: 900;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.lt-portfolio-filter__clear {
    align-items: center;
    display: inline-flex;
    min-height: 44px;
}
.lt-portfolio-grid {
    overflow: hidden;
    background: #f8f4ed;
    padding: 0;
}
.lt-portfolio-grid.lt-fullbleed {
    padding-left: 0;
    padding-right: 0;
}
.lt-portfolio-grid .lt-portfolio-grid__inner {
    width: 100%;
    max-width: none;
    margin: 0;
}
.lt-portfolio-grid__intro {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: clamp(1.5rem, 4vw, 4rem) clamp(1.25rem, 5vw, 5rem) 0;
    color: rgba(21, 21, 21, 0.56);
    font-family: 'Lato', sans-serif;
    font-size: 0.72rem;
    font-weight: 900;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}
.lt-portfolio-grid__cards {
    position: relative;
    display: block;
    width: 100%;
    min-height: 100vh;
    padding: 3rem 0 8rem;
}
.lt-portfolio-card {
    appearance: none;
    -webkit-appearance: none;
    position: absolute;
    display: block;
    width: var(--reel-width, 640px);
    height: var(--reel-height, 480px);
    left: var(--reel-left, 0);
    top: var(--reel-top, 0);
    border: 0;
    border-radius: 0;
    margin: 0;
    padding: 0;
    background: transparent;
    box-shadow: none;
    color: inherit;
    cursor: zoom-in;
    opacity: 0;
    overflow: visible;
    text-align: left;
    transform: translate3d(var(--reel-enter-x, 0), 64px, 0);
    transform-origin: center center;
    transition: opacity 0.18s linear, filter 0.2s ease, box-shadow 0.2s ease;
    will-change: transform, opacity;
}
.lt-portfolio-card:hover,
.lt-portfolio-card:focus-visible {
    box-shadow: none;
    outline: none;
}
.lt-portfolio-card:focus-visible .lt-portfolio-card__image img {
    outline: 3px solid #b31b34;
    outline-offset: 8px;
}
.lt-portfolio-card[hidden] {
    display: none !important;
}
.lt-portfolio-card__image {
    display: block;
    width: 100%;
    height: 100%;
    aspect-ratio: auto;
    background: transparent;
}
.lt-portfolio-card__image img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: transparent;
    box-shadow:
        0 1px 0 rgba(40, 30, 20, 0.04),
        0 34px 68px -34px rgba(40, 30, 20, 0.24),
        0 80px 140px -80px rgba(40, 30, 20, 0.18);
}
.lt-portfolio-card:hover .lt-portfolio-card__image img {
    filter: brightness(1.035);
}
.lt-portfolio-empty {
    position: relative;
    width: min(720px, calc(100% - 2rem));
    margin: 0 auto;
    color: #151515;
    background: #fffdf9;
    border: 1px solid rgba(14, 34, 64, 0.16);
}
.lt-portfolio-grid[data-empty="true"] .lt-portfolio-grid__cards {
    min-height: auto;
    padding: 4rem 0;
}
.lt-cta {
    background: #d9c7b3;
}
@media (max-width: 768px) {
    .lt-portfolio-hero {
        padding: 4rem 1.25rem 3rem;
    }
    .lt-portfolio-hero__title {
        font-size: clamp(3.25rem, 18vw, 5.75rem);
    }
    .lt-portfolio-filter {
        position: static;
        padding: 0.9rem 1rem;
    }
    .lt-portfolio-filter__inner {
        align-items: stretch;
    }
    .lt-portfolio-filter__pills {
        flex-wrap: nowrap;
        overflow-x: auto;
    }
    .lt-portfolio-filter__dropdown,
    .lt-portfolio-filter__meta {
        margin-left: 0;
    }
    .lt-portfolio-filter__dropdown {
        align-items: stretch;
        flex-direction: column;
        width: 100%;
        gap: 0.35rem;
    }
    .lt-portfolio-filter__dropdown select {
        width: 100%;
        min-width: 0;
    }
    .lt-portfolio-filter__meta {
        justify-content: space-between;
        width: 100%;
    }
    .lt-portfolio-grid__intro {
        align-items: flex-start;
        flex-direction: column;
        padding: 1.5rem 1.25rem 0;
    }
    .lt-portfolio-grid__cards {
        display: flex;
        flex-direction: column;
        gap: 3.5rem;
        height: auto !important;
        min-height: auto;
        padding: 2rem 0 4rem;
    }
    .lt-portfolio-card {
        position: relative;
        inset: auto;
        width: 100vw !important;
        max-width: 100vw;
        margin-left: calc(-1 * max(var(--lt-page-gutter), env(safe-area-inset-left)));
        height: auto !important;
        aspect-ratio: var(--reel-aspect, 4 / 3);
        opacity: 1 !important;
        transform: none !important;
    }
}
@media (prefers-reduced-motion: reduce) {
    .lt-portfolio-card {
        transition: none;
        opacity: 1;
        transform: none;
    }
}
"""


PAGE_JS = """
/* Portfolio filter — client-side only.
 * Reads ?event= and ?category= from URL on load (and falls back to
 * #hash for legacy homepage links). Updates active pill / dropdown,
 * hides non-matching cards, updates count via aria-live, syncs URL
 * via history.replaceState. AND-logic between the two axes.
 */
(function () {
    'use strict';

    const ALL = 'all';
    const filterRoot = document.querySelector('[data-portfolio-filter]');
    const grid = document.querySelector('[data-portfolio-grid]');
    if (!filterRoot || !grid) return;

    const pillButtons = Array.from(filterRoot.querySelectorAll('[data-event-pill]'));
    const dropdown = filterRoot.querySelector('[data-category-select]');
    const countLabel = filterRoot.querySelector('[data-portfolio-count]');
    const clearBtn = filterRoot.querySelector('[data-portfolio-clear]');
    const cards = Array.from(grid.querySelectorAll('[data-portfolio-card]'));

    let currentEvent = ALL;
    let currentCategory = ALL;

    function readInitialState() {
        const params = new URLSearchParams(window.location.search);
        let event = params.get('event') || ALL;
        let category = params.get('category') || ALL;

        // Legacy hash-fragment support: /portfolio#balloon-arches → category.
        if (category === ALL && window.location.hash) {
            const hash = window.location.hash.slice(1);
            if (hash) category = hash;
        }
        return { event, category };
    }

    function isKnown(value, source) {
        return value === ALL || source.some((opt) => opt === value);
    }

    function applyFilter(event, category) {
        currentEvent = event;
        currentCategory = category;

        let visibleCount = 0;
        cards.forEach((card) => {
            const cardEvent = card.getAttribute('data-event-type');
            const cardCategory = card.getAttribute('data-category');
            const matchEvent = event === ALL || cardEvent === event;
            const matchCategory = category === ALL || cardCategory === category;
            const visible = matchEvent && matchCategory;
            if (visible) {
                card.removeAttribute('hidden');
                visibleCount += 1;
            } else {
                card.setAttribute('hidden', '');
            }
        });

        // Update active pill
        pillButtons.forEach((btn) => {
            const slug = btn.getAttribute('data-event-pill');
            btn.setAttribute('aria-pressed', String(slug === event));
        });

        // Update dropdown
        if (dropdown && dropdown.value !== category) {
            dropdown.value = category;
        }

        // Count label (aria-live announces this update)
        if (countLabel) {
            const word = visibleCount === 1 ? 'piece' : 'pieces';
            countLabel.textContent = visibleCount + ' ' + word;
        }

        // Empty-state toggle
        grid.setAttribute('data-empty', String(visibleCount === 0));

        // Clear-button visibility (CSS handles via [data-filtered])
        const filtered = event !== ALL || category !== ALL;
        filterRoot.setAttribute('data-filtered', String(filtered));

        // Sync URL via replaceState (no history pollution)
        const params = new URLSearchParams();
        if (event !== ALL) params.set('event', event);
        if (category !== ALL) params.set('category', category);
        const qs = params.toString();
        const newUrl = window.location.pathname + (qs ? '?' + qs : '');
        try {
            window.history.replaceState({}, '', newUrl);
        } catch (e) { /* noop on file:// or similar */ }

        // Clean up any legacy hash fragment so it doesn't fight query params
        if (window.location.hash) {
            try {
                window.history.replaceState({}, '', newUrl);
            } catch (e) { /* noop */ }
        }

        window.dispatchEvent(new CustomEvent('lt:portfolio-filtered', {
            detail: { visibleCount: visibleCount }
        }));
    }

    // Wire pill clicks
    pillButtons.forEach((btn) => {
        btn.addEventListener('click', function () {
            const slug = btn.getAttribute('data-event-pill');
            applyFilter(slug, currentCategory);
        });
    });

    // Wire dropdown change
    if (dropdown) {
        dropdown.addEventListener('change', function () {
            applyFilter(currentEvent, dropdown.value);
        });
    }

    // Wire clear
    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            applyFilter(ALL, ALL);
        });
    }

    // Esc key clears all filters
    document.addEventListener('keydown', function (ev) {
        if (ev.key === 'Escape') {
            const filtered = currentEvent !== ALL || currentCategory !== ALL;
            if (filtered) applyFilter(ALL, ALL);
        }
    });

    // Initial render
    const initial = readInitialState();
    applyFilter(initial.event, initial.category);
})();


/* Floating photo reel.
 * Desktop uses left / right / center tracks with natural-ratio images.
 * Mobile falls back to a single full-width stream in source order.
 */
(function () {
    'use strict';

    const reel = document.querySelector('[data-portfolio-reel]');
    if (!reel) return;

    const cards = Array.from(reel.querySelectorAll('[data-portfolio-card]'));
    if (!cards.length) return;

    const mobileQuery = window.matchMedia('(max-width: 768px)');
    let raf = 0;
    let layoutRaf = 0;

    function numberAttr(el, name, fallback) {
        const raw = parseFloat(el.getAttribute(name));
        return Number.isFinite(raw) ? raw : fallback;
    }

    function visibleCards() {
        return cards.filter((card) => !card.hasAttribute('hidden'));
    }

    function clearDesktopStyles() {
        reel.style.height = '';
        cards.forEach((card) => {
            card.style.removeProperty('--reel-width');
            card.style.removeProperty('--reel-height');
            card.style.removeProperty('--reel-left');
            card.style.removeProperty('--reel-top');
            card.style.removeProperty('--reel-enter-x');
            card.style.removeProperty('--reel-aspect');
            card.style.transform = '';
            card.style.opacity = '';
        });
    }

    function layout() {
        window.cancelAnimationFrame(layoutRaf);
        layoutRaf = window.requestAnimationFrame(function () {
            if (mobileQuery.matches) {
                clearDesktopStyles();
                return;
            }

            const active = visibleCards();
            const vw = Math.max(reel.clientWidth, window.innerWidth);
            const baseUnit = Math.max(540, Math.min(760, vw * 0.5));
            const sideGutter = Math.max(28, vw * 0.035);
            const verticalSpacing = Math.max(96, Math.min(132, vw * 0.075));
            const overlap = 0.78;
            const centerBreath = Math.max(140, Math.min(220, vw * 0.12));

            let leftY = 0;
            let rightY = 90;
            let maxBottom = 0;

            active.forEach((card, index) => {
                const side = card.getAttribute('data-reel-side') || (index % 2 ? 'right' : 'left');
                const scale = numberAttr(card, 'data-reel-scale', 0.88);
                const aspect = numberAttr(card, 'data-reel-aspect', 4 / 3);
                const maxWidth = side === 'center' ? vw * 0.78 : vw * 0.56;
                const minWidth = Math.min(vw - sideGutter * 2, side === 'center' ? 650 : 510);
                const width = Math.max(Math.min(baseUnit * scale, maxWidth), Math.min(minWidth, maxWidth));
                const height = width / aspect;
                let top;
                let left;

                if (side === 'center') {
                    top = Math.max(leftY, rightY) + centerBreath;
                    left = (vw - width) / 2;
                    const nextY = top + height + centerBreath;
                    leftY = nextY;
                    rightY = nextY;
                } else if (side === 'right') {
                    top = rightY;
                    left = vw - width - sideGutter - ((index * 37) % 88);
                    rightY = top + height * overlap + verticalSpacing;
                } else {
                    top = leftY;
                    left = sideGutter + ((index * 43) % 92);
                    leftY = top + height * overlap + verticalSpacing;
                }

                maxBottom = Math.max(maxBottom, top + height);
                card.style.setProperty('--reel-width', width + 'px');
                card.style.setProperty('--reel-height', height + 'px');
                card.style.setProperty('--reel-left', Math.max(16, left) + 'px');
                card.style.setProperty('--reel-top', top + 'px');
                card.style.setProperty('--reel-enter-x', side === 'center' ? '0px' : (side === 'left' ? '-240px' : '240px'));
                card.style.setProperty('--reel-aspect', aspect);
            });

            reel.style.height = Math.ceil(maxBottom + 220) + 'px';
            updateScrollState();
        });
    }

    function updateScrollState() {
        if (mobileQuery.matches) return;
        const viewportHeight = window.innerHeight || 900;
        visibleCards().forEach((card) => {
            const rect = card.getBoundingClientRect();
            const center = rect.top + rect.height / 2;
            const progress = Math.max(0, Math.min(1, (viewportHeight - center) / viewportHeight * 1.45 + 0.22));
            const side = card.getAttribute('data-reel-side') || 'left';
            const entryX = side === 'center' ? 0 : (side === 'left' ? -240 : 240);
            const x = entryX * (1 - progress);
            const y = 64 * (1 - progress);
            const opacity = progress <= 0.02 ? 0 : 1;
            card.style.transform = 'translate3d(' + x + 'px, ' + y + 'px, 0)';
            card.style.opacity = opacity;
        });
    }

    function onScroll() {
        window.cancelAnimationFrame(raf);
        raf = window.requestAnimationFrame(updateScrollState);
    }

    window.addEventListener('resize', layout, { passive: true });
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('lt:portfolio-filtered', layout);
    if (mobileQuery.addEventListener) {
        mobileQuery.addEventListener('change', layout);
    }

    cards.forEach((card) => {
        const img = card.querySelector('img');
        if (img && !img.complete) {
            img.addEventListener('load', layout, { once: true });
        }
    });

    layout();
})();


/* Lightbox modal — opens the full photo when a card is clicked.
 * Single modal element reused across all cards. Reads card data attrs
 * (data-modal-image / data-modal-title / data-modal-category-label / data-modal-alt)
 * to populate the panel. Handles ESC, backdrop click, close button,
 * focus management, body scroll lock, and prefers-reduced-motion.
 */
(function () {
    'use strict';

    const modal = document.querySelector('[data-portfolio-modal]');
    if (!modal) return;
    const modalImage = modal.querySelector('[data-modal-image]');
    const modalTitle = modal.querySelector('[data-modal-title]');
    const modalCategory = modal.querySelector('[data-modal-category]');
    const closeTriggers = Array.from(modal.querySelectorAll('[data-modal-close]'));
    const cards = Array.from(document.querySelectorAll('[data-portfolio-card]'));

    let lastFocused = null;

    function openModal(card) {
        const image = card.getAttribute('data-modal-image') || '';
        const alt = card.getAttribute('data-modal-alt') || '';
        const title = card.getAttribute('data-modal-title') || '';
        const category = card.getAttribute('data-modal-category-label') || '';

        modalImage.setAttribute('src', image);
        modalImage.setAttribute('alt', alt);
        modalTitle.textContent = title;
        modalCategory.textContent = category;

        lastFocused = card;
        modal.removeAttribute('hidden');
        document.body.classList.add('lt-modal-open');

        // Move focus to close button on next tick (after display swap settles)
        const closeBtn = modal.querySelector('.lt-portfolio-modal__close');
        if (closeBtn) {
            window.setTimeout(function () { closeBtn.focus(); }, 0);
        }
    }

    function closeModal() {
        if (modal.hasAttribute('hidden')) return;
        modal.setAttribute('hidden', '');
        document.body.classList.remove('lt-modal-open');
        // Free the loaded image so memory doesn't grow with each open
        modalImage.setAttribute('src', '');
        modalImage.setAttribute('alt', '');
        if (lastFocused && typeof lastFocused.focus === 'function') {
            lastFocused.focus();
        }
        lastFocused = null;
    }

    function isOpen() {
        return !modal.hasAttribute('hidden');
    }

    // Wire each card to open the modal on click
    cards.forEach(function (card) {
        card.addEventListener('click', function () { openModal(card); });
    });

    // Wire close triggers (close button + backdrop)
    closeTriggers.forEach(function (el) {
        el.addEventListener('click', function () { closeModal(); });
    });

    // Keyboard: ESC closes modal (capture phase so the filter's ESC handler
    // doesn't also fire and clear filters when modal is open).
    document.addEventListener('keydown', function (ev) {
        if (!isOpen()) return;
        if (ev.key === 'Escape') {
            ev.stopImmediatePropagation();
            closeModal();
            return;
        }
        // Focus trap inside modal
        if (ev.key === 'Tab') {
            const focusable = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            if (focusable.length === 0) return;
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (ev.shiftKey && document.activeElement === first) {
                ev.preventDefault();
                last.focus();
            } else if (!ev.shiftKey && document.activeElement === last) {
                ev.preventDefault();
                first.focus();
            }
        }
    }, true);
})();
"""


def get_context(context):
    event_slug = (frappe.form_dict.get("event") or "").strip().lower() or None
    category_slug = (frappe.form_dict.get("category") or "").strip().lower() or None

    label = _filter_label(items=GALLERY_ITEMS, event_slug=event_slug, category_slug=category_slug)

    if label:
        context.title = f"{label} Balloon Decor - Locally Twisted Portfolio"
    else:
        context.title = "Portfolio - Locally Twisted Event Balloon Proof"

    description = (
        "Browse Locally Twisted's proof gallery for Utah corporate, school, civic, "
        "community, venue, public, and supporting private event balloon work."
    )
    if label:
        description = (
            f"Browse Locally Twisted's {label.lower()} balloon decor portfolio "
            "across Utah's Wasatch Front. Quote-led installations for event clients."
        )

    context.metatags = {
        "description": description,
        "og:title": context.title,
        "og:description": description,
        "og:type": "website",
    }

    context.event_types = EVENT_TYPES
    context.categories = CATEGORIES
    context.gallery_items = GALLERY_ITEMS
    context.initial_event = event_slug or "all"
    context.initial_category = category_slug or "all"
    context.itemlist_jsonld = json.dumps(_build_itemlist_jsonld(GALLERY_ITEMS))
    context.colocated_css = PAGE_CSS
    context.colocated_js = PAGE_JS

    return context
