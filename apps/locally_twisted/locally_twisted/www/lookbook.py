"""Lookbook controller — `/lookbook` route.

Slice 7 of Phase 1 — the visual heart of the site. Per
`.planning/decisions/site-shape.md`, the lookbook is the primary "browse"
surface — full portfolio organized by event type, with a secondary product-type
filter for visitors thinking about a specific kind of decor.

Architecture:
- Hero band → blush ribbon divider → filter row (dual-axis: event × product)
  → gallery grid → closing CTA. Mirrors the homepage's full-bleed band pattern.
- Photos are SCAFFOLDING for the architecture — what's being designed is the
  surface, the dual-axis filter behavior, the empty state, the URL state, and
  the responsive grid. Photos will rotate as Jeff's archive is curated.
- Filter logic is client-side JS only (no whitelisted endpoint, no AJAX).
  Reads `data-event-type` and `data-category` on each card; AND-logic
  intersection between axes; "All" = no filter on that axis.
- URL state via query strings: `/lookbook?event=weddings&category=balloon-arches`.
  Server-readable so per-filter <title> + meta description vary; crawlable;
  share-able. Backward-compat with hash fragments (`/lookbook#balloon-arches`)
  from the homepage's Custom Creations tile links.
- Schema markup: page-level ItemList JSON-LD, emitted from get_context as a
  Python dict and json.dumps'd in the template.

Out of scope for this slice (deferred):
- The "Build your palette" 4-step configurator from the synthesis mockup —
  that's the future Design Studio (post-Phase-1 per site-shape.md).
- Sub-routes like `/lookbook/<slug>` for full case-study pages — Slice 8.
- Custom DocType for Lookbook Items — overkill at this data volume.
"""
import json

import frappe

no_cache = 1
sitemap = 1


# Event-type filter pills (the primary axis per site-shape.md and PLAN.md).
# "All" is rendered first by the template; not in this list.
EVENT_TYPES = [
    {"slug": "corporate", "name": "Corporate"},
    {"slug": "weddings", "name": "Weddings"},
    {"slug": "birthdays", "name": "Birthdays"},
    {"slug": "schools", "name": "Schools"},
    {"slug": "seasonal", "name": "Seasonal"},
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
# the client-side filter. Filenames map to /assets/locally_twisted/images/lookbook/.
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
        "event_type": "corporate",
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
        "event_type": "weddings",
        "year": "2024",
        "image": "wedding-floral-half-arch.png",
        "alt": "Wedding ceremony half-arch combining balloons and white floral arrangements",
    },
    {
        "slug": "wedding-foil-heart-arch",
        "title": "Foil Heart Wedding Arch",
        "category": "balloon-arches",
        "event_type": "weddings",
        "year": "2024",
        "image": "wedding-foil-heart-arch.png",
        "alt": "Wedding arch composed of foil heart balloons in soft metallic tones",
    },
    {
        "slug": "wedding-organic-half-arch",
        "title": "Organic White Floral Half-Arch",
        "category": "garlands",
        "event_type": "weddings",
        "year": "2025",
        "image": "wedding-organic-half-arch.png",
        "alt": "Soft organic balloon garland forming a half-arch with white flower accents at a wedding ceremony",
    },
    {
        "slug": "birthday-smurfs-arch",
        "title": "Smurfs Birthday Arch",
        "category": "balloon-arches",
        "event_type": "birthdays",
        "year": "2024",
        "image": "birthday-smurfs-arch.png",
        "alt": "Smurfs-themed balloon arch in blue and white at a child's birthday party",
    },
    {
        "slug": "birthday-pirate-column",
        "title": "Pirate-Themed Balloon Column",
        "category": "columns",
        "event_type": "birthdays",
        "year": "2023",
        "image": "birthday-pirate-column.jpg",
        "alt": "Custom pirate-themed balloon column at a children's birthday party",
    },
    {
        "slug": "birthday-dolphin-backdrop",
        "title": "Under-the-Sea Dolphin Backdrop",
        "category": "picture-perfect-backdrops",
        "event_type": "birthdays",
        "year": "2024",
        "image": "birthday-dolphin-backdrop.png",
        "alt": "Ocean-themed birthday photo backdrop featuring a balloon dolphin",
    },
    {
        "slug": "birthday-balloon-bouquets",
        "title": "Birthday Helium Bouquets",
        "category": "balloon-bouquets",
        "event_type": "birthdays",
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
        "event_type": "seasonal",
        "year": "2024",
        "image": "seasonal-easter-rabbit-arch.png",
        "alt": "Twenty-foot Easter balloon arch with sculpted rabbit ears at the top",
    },
    {
        "slug": "seasonal-halloween-tombstone",
        "title": "Halloween Tombstone Backdrop",
        "category": "picture-perfect-backdrops",
        "event_type": "seasonal",
        "year": "2024",
        "image": "seasonal-halloween-tombstone.png",
        "alt": "Halloween balloon backdrop styled as a graveyard with sculpted tombstones",
    },
    {
        "slug": "seasonal-pride-columns",
        "title": "Pride Rainbow Columns",
        "category": "balloon-arches",  # rainbow columns are paired arch-y; could also be columns
        "event_type": "seasonal",
        "year": "2024",
        "image": "seasonal-pride-columns.png",
        "alt": "Pair of rainbow balloon columns for a Pride event entrance",
    },
]
# Re-tag the Pride one to columns category (more accurate).
GALLERY_ITEMS[14]["category"] = "columns"


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
                "image": f"/assets/locally_twisted/images/lookbook/{item['image']}",
                "url": f"/lookbook?category={item['category']}",
            }
            for idx, item in enumerate(items)
        ],
    }


PAGE_CSS = """
/* ======================================================================
 * LOOKBOOK — /lookbook — Slice 7
 * BEM blocks: lt-lookbook-hero, lt-lookbook-filter, lt-lookbook-grid,
 *             lt-lookbook-card, lt-lookbook-empty
 * Reuses from lt-theme.css: --lt-* color tokens, .lt-band--blush,
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
.lt-lookbook-hero {
    background-color: var(--lt-blush-tint);
    padding: 4rem 1.5rem 3.5rem;
}
.lt-lookbook-hero__inner {
    max-width: 1100px;
    margin: 0 auto;
    text-align: left;
}
.lt-lookbook-hero__eyebrow {
    font-family: 'Raleway', sans-serif;
    font-size: 0.8125rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
    margin: 0 0 1rem;
}
.lt-lookbook-hero__title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.75rem;
    line-height: 1.05;
    color: var(--lt-near-black);
    margin: 0 0 1.25rem;
}
@media (min-width: 768px) {
    .lt-lookbook-hero__title { font-size: 3.5rem; }
}
@media (min-width: 1200px) {
    .lt-lookbook-hero__title { font-size: 4rem; }
}
.lt-lookbook-hero__body {
    font-family: 'Raleway', sans-serif;
    font-size: 1.0625rem;
    line-height: 1.55;
    color: var(--lt-near-black);
    max-width: 580px;
    margin: 0;
}

/* --- Pink ribbon divider (between hero and filter) ------------------ */
/* Saturated brand blush (#F4DFD7), structural separator at the same
 * weight as the homepage's 3-dot dividers in their respective bands. */
.lt-lookbook-ribbon {
    height: 28px;
    background-color: var(--lt-blush);
}

/* --- Filter row ------------------------------------------------------ */
.lt-lookbook-filter {
    background-color: var(--lt-white);
    padding: 1.5rem 1rem 1.25rem;
    border-bottom: 1px solid #f0f0f0;
}
.lt-lookbook-filter__inner {
    max-width: 1300px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
@media (min-width: 992px) {
    .lt-lookbook-filter__inner {
        flex-direction: row;
        align-items: center;
        gap: 1.5rem;
    }
}

/* Pill chips: horizontal-scroll on mobile, inline on desktop. */
.lt-lookbook-filter__pills {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    scroll-snap-type: x mandatory;
    padding: 0.25rem 0;
    margin: 0;
    list-style: none;
}
.lt-lookbook-filter__pills::-webkit-scrollbar { display: none; }
.lt-lookbook-filter__pill {
    flex: 0 0 auto;
    scroll-snap-align: start;
}
.lt-lookbook-filter__pill button {
    appearance: none;
    background: transparent;
    border: 1px solid #d6d6d6;
    border-radius: 999px;
    padding: 0.5rem 1rem;
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--lt-near-black);
    cursor: pointer;
    white-space: nowrap;
    min-height: 40px;
    transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}
.lt-lookbook-filter__pill button:hover {
    border-color: var(--lt-near-black);
}
.lt-lookbook-filter__pill button:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-lookbook-filter__pill button[aria-pressed="true"] {
    background-color: var(--lt-near-black);
    border-color: var(--lt-near-black);
    color: var(--lt-white);
}

/* Category dropdown */
.lt-lookbook-filter__dropdown {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    flex: 0 0 auto;
}
.lt-lookbook-filter__dropdown label {
    font-family: 'Raleway', sans-serif;
    font-size: 0.8125rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
    margin: 0;
}
.lt-lookbook-filter__dropdown select {
    appearance: none;
    -webkit-appearance: none;
    background-color: var(--lt-white);
    border: 1px solid #d6d6d6;
    border-radius: 0.375rem;
    padding: 0.5rem 2rem 0.5rem 0.875rem;
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    color: var(--lt-near-black);
    cursor: pointer;
    min-height: 40px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' fill='none' stroke='%23222' stroke-width='1.6'%3E%3Cpath d='M2 4 L6 8 L10 4'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.625rem center;
    background-size: 12px;
}
.lt-lookbook-filter__dropdown select:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}

/* Count + clear */
.lt-lookbook-filter__meta {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.lt-lookbook-filter__count {
    font-family: 'Raleway', sans-serif;
    font-size: 0.8125rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
}
.lt-lookbook-filter__clear {
    appearance: none;
    background: transparent;
    border: none;
    padding: 0.25rem 0.5rem;
    font-family: 'Raleway', sans-serif;
    font-size: 0.8125rem;
    color: var(--lt-near-black);
    text-decoration: underline;
    cursor: pointer;
    visibility: hidden;
}
.lt-lookbook-filter__clear:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-lookbook-filter[data-filtered="true"] .lt-lookbook-filter__clear {
    visibility: visible;
}

/* --- Gallery grid --------------------------------------------------- */
.lt-lookbook-grid {
    background-color: var(--lt-near-white);
    padding: 3rem 1rem 4rem;
}
.lt-lookbook-grid__inner {
    max-width: 1300px;
    margin: 0 auto;
}
.lt-lookbook-grid__cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}
@media (min-width: 768px) {
    .lt-lookbook-grid__cards {
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
    }
}
@media (min-width: 1400px) {
    .lt-lookbook-grid__cards {
        grid-template-columns: repeat(4, 1fr);
        gap: 1.75rem;
    }
}

/* --- Lookbook card (mirrors .lt-featured__card from homepage) ------- */
.lt-lookbook-card {
    background-color: var(--lt-white);
    border-radius: 0.5rem;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: block;
}
.lt-lookbook-card:hover,
.lt-lookbook-card:focus-visible {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
    outline: none;
}
.lt-lookbook-card:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-lookbook-card[hidden] { display: none !important; }

.lt-lookbook-card__image {
    width: 100%;
    aspect-ratio: 4 / 5;
    background-color: var(--lt-blush-tint);
    background-size: cover;
    background-position: center;
}
.lt-lookbook-card__body {
    padding: 1rem 1.125rem 1.25rem;
}
@media (min-width: 768px) {
    .lt-lookbook-card__body { padding: 1.125rem 1.375rem 1.5rem; }
}
.lt-lookbook-card__category {
    font-family: 'Raleway', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--lt-soft-gray);
    margin: 0 0 0.375rem;
}
.lt-lookbook-card__title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.125rem;
    color: var(--lt-near-black);
    margin: 0;
    line-height: 1.25;
}
@media (min-width: 768px) {
    .lt-lookbook-card__title { font-size: 1.25rem; }
}

/* --- Empty state ---------------------------------------------------- */
.lt-lookbook-empty {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3.5rem 1rem;
    display: none;
}
.lt-lookbook-grid[data-empty="true"] .lt-lookbook-empty { display: block; }
.lt-lookbook-empty__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.75rem;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
}
.lt-lookbook-empty__body {
    font-family: 'Raleway', sans-serif;
    color: var(--lt-soft-gray);
    margin: 0 0 1.5rem;
    font-size: 1rem;
}
.lt-lookbook-empty__cta {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background-color: var(--lt-teal);
    color: var(--lt-white);
    text-decoration: none;
    border-radius: 0.375rem;
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    font-size: 0.9375rem;
    min-height: 44px;
}
.lt-lookbook-empty__cta:focus-visible {
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}

/* --- Closing CTA (mirrors homepage .lt-cta) ------------------------- */
.lt-cta {
    background-color: var(--lt-soft-blue, var(--lt-blue-tint));
    padding: 4rem 1rem 4.5rem;
    text-align: center;
}
.lt-cta__inner { max-width: 1200px; margin: 0 auto; }
.lt-cta__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.5rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.15;
}
.lt-cta__body {
    font-family: 'Raleway', sans-serif;
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
    font-family: 'Raleway', sans-serif;
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

/* --- Reduced-motion: disable card hover-lift transitions ------------ */
@media (prefers-reduced-motion: reduce) {
    .lt-lookbook-card { transition: none; }
    .lt-lookbook-card:hover,
    .lt-lookbook-card:focus-visible { transform: none; }
}
"""


PAGE_JS = """
/* Lookbook filter — client-side only.
 * Reads ?event= and ?category= from URL on load (and falls back to
 * #hash for legacy homepage links). Updates active pill / dropdown,
 * hides non-matching cards, updates count via aria-live, syncs URL
 * via history.replaceState. AND-logic between the two axes.
 */
(function () {
    'use strict';

    const ALL = 'all';
    const filterRoot = document.querySelector('[data-lookbook-filter]');
    const grid = document.querySelector('[data-lookbook-grid]');
    if (!filterRoot || !grid) return;

    const pillButtons = Array.from(filterRoot.querySelectorAll('[data-event-pill]'));
    const dropdown = filterRoot.querySelector('[data-category-select]');
    const countLabel = filterRoot.querySelector('[data-lookbook-count]');
    const clearBtn = filterRoot.querySelector('[data-lookbook-clear]');
    const cards = Array.from(grid.querySelectorAll('[data-lookbook-card]'));

    let currentEvent = ALL;
    let currentCategory = ALL;

    function readInitialState() {
        const params = new URLSearchParams(window.location.search);
        let event = params.get('event') || ALL;
        let category = params.get('category') || ALL;

        // Legacy hash-fragment support: /lookbook#balloon-arches → category.
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
"""


def get_context(context):
    event_slug = (frappe.form_dict.get("event") or "").strip().lower() or None
    category_slug = (frappe.form_dict.get("category") or "").strip().lower() or None

    label = _filter_label(items=GALLERY_ITEMS, event_slug=event_slug, category_slug=category_slug)

    if label:
        context.title = f"{label} Balloon Decor — Locally Twisted Look Book"
    else:
        context.title = "Look Book — Locally Twisted Custom Balloon Decor"

    description = (
        "Browse Locally Twisted's portfolio of custom balloon decor — "
        "weddings, corporate events, birthdays, and milestone celebrations "
        "across Utah's Wasatch Front. Inquire for your event."
    )
    if label:
        description = (
            f"Browse Locally Twisted's {label.lower()} balloon decor portfolio "
            "across Utah's Wasatch Front. Custom installations for every event."
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
