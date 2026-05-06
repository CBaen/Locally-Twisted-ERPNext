"""Portfolio page controller for `/portfolio`.

The portfolio intentionally breaks out of card-grid behavior. It keeps the
Frappe website shell, but the page body is a full-bleed photo reel using real
installed-work photos.
"""

import json

import frappe

no_cache = 1
sitemap = 1


EVENT_TYPES = [
    {"slug": "corporate", "name": "Corporate"},
    {"slug": "schools", "name": "Schools"},
    {"slug": "civic-community", "name": "Civic & Community"},
    {"slug": "venues-public", "name": "Venues & Public Installs"},
    {"slug": "private-events", "name": "Private Events"},
]

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


GALLERY_ITEMS = [
    {
        "slug": "corporate-logo-arch",
        "title": "School Entrance Arch",
        "client": "School event",
        "category": "balloon-arches",
        "event_type": "schools",
        "year": "2024",
        "image": "corporate-logo-arch.png",
        "alt": "Custom corporate brand logo balloon arch installed at a company event entrance",
    },
    {
        "slug": "corporate-weberstock-photo-opt",
        "title": "Weberstock Festival Photo Backdrop",
        "client": "Weber State University",
        "category": "picture-perfect-backdrops",
        "event_type": "corporate",
        "year": "2025",
        "image": "corporate-weberstock-photo-opt.png",
        "alt": "Large balloon photo backdrop with festival branding for the Weberstock corporate event",
    },
    {
        "slug": "corporate-wsu-arch-bouquets",
        "title": "WSU Welcome Bouquets",
        "client": "Weber State University",
        "category": "balloon-bouquets",
        "event_type": "corporate",
        "year": "2024",
        "image": "corporate-wsu-arch-bouquets.png",
        "alt": "Helium balloon bouquets and an arch styled in Weber State University colors at a campus event",
    },
    {
        "slug": "wedding-floral-half-arch",
        "title": "Floral Half-Arch with White Blooms",
        "client": "Private event",
        "category": "picture-perfect-backdrops",
        "event_type": "private-events",
        "year": "2024",
        "image": "wedding-floral-half-arch.png",
        "alt": "Wedding ceremony half-arch combining balloons and white floral arrangements",
    },
    {
        "slug": "wedding-foil-heart-arch",
        "title": "Foil Heart Wedding Arch",
        "client": "Private event",
        "category": "balloon-arches",
        "event_type": "private-events",
        "year": "2024",
        "image": "wedding-foil-heart-arch.png",
        "alt": "Wedding arch composed of foil heart balloons in soft metallic tones",
    },
    {
        "slug": "wedding-organic-half-arch",
        "title": "Intermountain Health Photo Moment",
        "client": "Intermountain Health",
        "category": "garlands",
        "event_type": "corporate",
        "year": "2025",
        "image": "wedding-organic-half-arch.png",
        "alt": "Soft organic balloon garland forming a half-arch with white flower accents at a wedding ceremony",
    },
    {
        "slug": "birthday-smurfs-arch",
        "title": "Smurfs Birthday Arch",
        "client": "Private event",
        "category": "balloon-arches",
        "event_type": "private-events",
        "year": "2024",
        "image": "birthday-smurfs-arch.png",
        "alt": "Smurfs-themed balloon arch in blue and white at a child's birthday party",
    },
    {
        "slug": "birthday-pirate-column",
        "title": "Pirate-Themed Balloon Column",
        "client": "Private event",
        "category": "columns",
        "event_type": "private-events",
        "year": "2023",
        "image": "birthday-pirate-column.jpg",
        "alt": "Custom pirate-themed balloon column at a children's birthday party",
    },
    {
        "slug": "birthday-dolphin-backdrop",
        "title": "Under-the-Sea Dolphin Backdrop",
        "client": "Private event",
        "category": "picture-perfect-backdrops",
        "event_type": "private-events",
        "year": "2024",
        "image": "birthday-dolphin-backdrop.png",
        "alt": "Ocean-themed birthday photo backdrop featuring a balloon dolphin",
    },
    {
        "slug": "birthday-balloon-bouquets",
        "title": "Birthday Helium Bouquets",
        "client": "Private event",
        "category": "balloon-bouquets",
        "event_type": "private-events",
        "year": "2025",
        "image": "birthday-balloon-bouquets.png",
        "alt": "Five-balloon helium bouquets in birthday colors arranged for a party table",
    },
    {
        "slug": "school-back-to-school-stage",
        "title": "Back-to-School Stage Display",
        "client": "School event",
        "category": "picture-perfect-backdrops",
        "event_type": "schools",
        "year": "2024",
        "image": "school-back-to-school-stage.png",
        "alt": "Large balloon stage display for a school back-to-school assembly",
    },
    {
        "slug": "school-grad-garland",
        "title": "Graduation Organic Garland",
        "client": "School event",
        "category": "garlands",
        "event_type": "schools",
        "year": "2025",
        "image": "school-grad-garland.png",
        "alt": "Organic balloon garland in graduation colors framing a school ceremony stage",
    },
    {
        "slug": "seasonal-easter-rabbit-arch",
        "title": "Easter Rabbit-Ears Arch",
        "client": "Community event",
        "category": "balloon-arches",
        "event_type": "civic-community",
        "year": "2024",
        "image": "seasonal-easter-rabbit-arch.png",
        "alt": "Twenty-foot Easter balloon arch with sculpted rabbit ears at the top",
    },
    {
        "slug": "seasonal-halloween-tombstone",
        "title": "Halloween Tombstone Backdrop",
        "client": "Venue install",
        "category": "picture-perfect-backdrops",
        "event_type": "venues-public",
        "year": "2024",
        "image": "seasonal-halloween-tombstone.png",
        "alt": "Halloween balloon backdrop styled as a graveyard with sculpted tombstones",
    },
    {
        "slug": "seasonal-pride-columns",
        "title": "Pride Rainbow Columns",
        "client": "Gallivan Center",
        "category": "columns",
        "event_type": "civic-community",
        "year": "2024",
        "image": "seasonal-pride-columns.png",
        "alt": "Pair of rainbow balloon columns for a Pride event entrance",
    },
]


# The reel depends on mixed scales and an edge/center rhythm. Keep center
# placements frequent enough that desktop scroll states feel balanced.
APPROVED_COLLAGE_SLOTS = [
    {"side": "left", "scale": 0.70, "w": 4, "h": 5},
    {"side": "right", "scale": 0.84, "w": 3, "h": 2},
    {"side": "center", "scale": 1.02, "w": 16, "h": 10},
    {"side": "left", "scale": 0.66, "w": 2, "h": 3},
    {"side": "right", "scale": 0.72, "w": 3, "h": 4},
    {"side": "center", "scale": 0.98, "w": 16, "h": 9},
    {"side": "left", "scale": 0.78, "w": 5, "h": 4},
    {"side": "right", "scale": 0.66, "w": 3, "h": 4},
    {"side": "center", "scale": 1.00, "w": 16, "h": 10},
    {"side": "left", "scale": 0.72, "w": 4, "h": 5},
    {"side": "right", "scale": 0.84, "w": 3, "h": 2},
    {"side": "center", "scale": 0.96, "w": 16, "h": 9},
    {"side": "left", "scale": 0.70, "w": 4, "h": 5},
    {"side": "right", "scale": 0.74, "w": 3, "h": 4},
    {"side": "center", "scale": 0.98, "w": 16, "h": 10},
    {"side": "left", "scale": 0.66, "w": 2, "h": 3},
    {"side": "right", "scale": 0.70, "w": 3, "h": 4},
    {"side": "center", "scale": 0.96, "w": 16, "h": 9},
    {"side": "left", "scale": 0.72, "w": 4, "h": 5},
    {"side": "right", "scale": 0.86, "w": 3, "h": 2},
]

PORTFOLIO_DISPLAY_ORDER = [
    "wedding-organic-half-arch",
    "corporate-weberstock-photo-opt",
    "seasonal-halloween-tombstone",
    "corporate-logo-arch",
    "seasonal-pride-columns",
    "corporate-wsu-arch-bouquets",
    "school-back-to-school-stage",
    "school-grad-garland",
    "birthday-dolphin-backdrop",
    "wedding-floral-half-arch",
    "wedding-foil-heart-arch",
    "birthday-smurfs-arch",
    "seasonal-easter-rabbit-arch",
    "birthday-balloon-bouquets",
    "birthday-pirate-column",
]

PORTFOLIO_REEL_META = {
    "wedding-organic-half-arch": {"w": 1500, "h": 2000},
    "corporate-weberstock-photo-opt": {"w": 2000, "h": 1500},
    "birthday-pirate-column": {"w": 1440, "h": 1800},
    "birthday-dolphin-backdrop": {"w": 2000, "h": 1500},
    "seasonal-halloween-tombstone": {"w": 1284, "h": 1595},
    "wedding-floral-half-arch": {"w": 2000, "h": 1500},
    "corporate-logo-arch": {"w": 2000, "h": 1500},
    "seasonal-pride-columns": {"w": 2000, "h": 1500},
    "school-grad-garland": {"w": 2000, "h": 1500},
    "wedding-foil-heart-arch": {"w": 2000, "h": 1500},
    "birthday-smurfs-arch": {"w": 2000, "h": 1500},
    "corporate-wsu-arch-bouquets": {"w": 2000, "h": 1500},
    "seasonal-easter-rabbit-arch": {"w": 2000, "h": 1500},
    "birthday-balloon-bouquets": {"w": 2000, "h": 1500},
    "school-back-to-school-stage": {"w": 746, "h": 573},
}

_portfolio_order = {slug: index for index, slug in enumerate(PORTFOLIO_DISPLAY_ORDER)}
GALLERY_ITEMS.sort(key=lambda item: _portfolio_order.get(item["slug"], len(_portfolio_order)))
for index, item in enumerate(GALLERY_ITEMS):
    slot = APPROVED_COLLAGE_SLOTS[index % len(APPROVED_COLLAGE_SLOTS)]
    item.update(slot)


def _known_slug(slug, options):
    if not slug:
        return None
    allowed = {option["slug"] for option in options}
    return slug if slug in allowed else None


def _filter_label(event_slug=None, category_slug=None):
    event_name = next((item["name"] for item in EVENT_TYPES if item["slug"] == event_slug), None)
    category_name = next((item["name"] for item in CATEGORIES if item["slug"] == category_slug), None)
    if event_name and category_name:
        return f"{event_name} {category_name}"
    return event_name or category_name or ""


def _filtered_items(items, event_slug=None, category_slug=None):
    return [
        item
        for item in items
        if (not event_slug or item["event_type"] == event_slug)
        and (not category_slug or item["category"] == category_slug)
    ]


def _optimized_url(filename):
    stem = filename.rsplit(".", 1)[0]
    return f"/assets/locally_twisted/images/portfolio/optimized/{stem}.webp"


def _source_url(filename):
    return f"/assets/locally_twisted/images/portfolio/{filename}"


def _photo_payload(items):
    payload = []
    for index, item in enumerate(items):
        payload.append(
            {
                "id": item["slug"],
                "title": item["title"],
                "client": item.get("client", "Locally Twisted"),
                "alt": item["alt"],
                "category": item["category"],
                "event_type": item["event_type"],
                "year": item["year"],
                "w": item.get("w", 2000),
                "h": item.get("h", 1500),
                "side": item.get("side") or ("right" if index % 2 else "left"),
                "scale": item.get("scale", 0.9),
                "image_url": _optimized_url(item["image"]),
                "source_url": _source_url(item["image"]),
            }
        )
    return payload


def _display_items(items):
    return [
        {
            **item,
            "optimized_url": _optimized_url(item["image"]),
            "source_url": _source_url(item["image"]),
        }
        for item in items
    ]


def _build_itemlist_jsonld(items):
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Locally Twisted Portfolio",
        "description": "Custom balloon decor installations across Utah's Wasatch Front.",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index + 1,
                "name": item["title"],
                "image": _optimized_url(item["image"]),
                "url": f"/portfolio?category={item['category']}",
            }
            for index, item in enumerate(items)
        ],
    }


def get_context(context):
    event_slug = _known_slug((frappe.form_dict.get("event") or "").strip().lower(), EVENT_TYPES)
    category_slug = _known_slug((frappe.form_dict.get("category") or "").strip().lower(), CATEGORIES)
    label = _filter_label(event_slug, category_slug)
    gallery_items = _filtered_items(GALLERY_ITEMS, event_slug, category_slug)
    display_items = _display_items(gallery_items)

    if label:
        context.title = f"{label} - Locally Twisted Portfolio"
        context.portfolio_eyebrow = f"{label} portfolio"
        context.portfolio_intro = f"Utah {label.lower()} balloon decor for events, schools, venues, and company celebrations."
    else:
        context.title = "Utah Balloon Decor Portfolio - Locally Twisted"
        context.portfolio_eyebrow = "Utah balloon decor portfolio"
        context.portfolio_intro = "Utah balloon decor for corporate events, schools, photo backdrops, and private celebrations."

    description = "See Locally Twisted's Utah balloon decor portfolio for corporate events, schools, community celebrations, photo backdrops, and private parties."
    if label:
        description = f"Browse Locally Twisted's {label.lower()} balloon decor portfolio across Utah."

    context.metatags = {
        "description": description,
        "og:title": context.title,
        "og:description": description,
        "og:type": "website",
    }

    context.gallery_items = display_items
    context.portfolio_count = len(gallery_items)
    context.portfolio_photos_json = json.dumps(_photo_payload(gallery_items))
    context.itemlist_jsonld = json.dumps(_build_itemlist_jsonld(gallery_items))

    return context
