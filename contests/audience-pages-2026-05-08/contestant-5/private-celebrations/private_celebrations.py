"""Controller for /private-celebrations audience landing page.

Private Celebrations: birthday parents, wedding planners, baby shower hosts,
milestone families, memorial/celebration-of-life organizers. Buyer posture:
personal, milestone-emotional, taste-elevated, gift-feeling. No named clients.
"""

no_cache = 1
sitemap = 1

# Category-level proof for private celebrations.
# No named clients — privacy expectation for personal events.
PROOF_CATEGORIES = [
    {
        "label": "Birthdays",
        "detail": "300+ installs across all ages — milestone birthdays, children's parties, surprise celebrations, and multi-generational family events.",
        "icon": "balloon-cluster",
    },
    {
        "label": "Weddings",
        "detail": "Arch installations, ceremony backdrops, reception garlands, and entrance columns across Wasatch Front venues.",
        "icon": "organic-garland",
    },
    {
        "label": "Baby Showers & Gender Reveals",
        "detail": "Organic garlands, ceiling installations, and themed photo backdrops for the events before the arrival.",
        "icon": "balloon-bouquet",
    },
    {
        "label": "Memorial & Celebration of Life",
        "detail": "Tasteful, restrained, and meaningful balloon decor for honoring someone. Handled with the same care as the occasion deserves.",
        "icon": "balloon-pair",
    },
    {
        "label": "Anniversary & Milestone Events",
        "detail": "30th, 50th, 60th, and beyond. The decor matches the occasion's weight — not a child's party aesthetic applied to a 50-year marriage.",
        "icon": "organic-garland",
    },
    {
        "label": "Graduations & Personal Milestones",
        "detail": "Individual family celebrations for graduates, promotions, retirements, and personal achievements.",
        "icon": "balloon-arch",
    },
]

# Installed work proof — photo references for the visual proof section.
# Captions are category/context only — no client names.
PROOF_PHOTOS = [
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp",
        "alt": "Organic balloon half-arch with floral accents for a wedding ceremony",
        "caption": "Organic half-arch — wedding ceremony",
    },
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/wedding-floral-half-arch.webp",
        "alt": "Floral balloon half-arch installation for an upscale wedding",
        "caption": "Floral arch — wedding reception",
    },
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/birthday-smurfs-arch.webp",
        "alt": "Custom themed balloon arch for a children's birthday party",
        "caption": "Themed arch — children's birthday install",
    },
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/birthday-dolphin-backdrop.webp",
        "alt": "Custom dolphin themed balloon backdrop for a birthday celebration",
        "caption": "Custom backdrop — milestone birthday",
    },
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/wedding-foil-heart-arch.webp",
        "alt": "Foil heart balloon arch for a wedding or celebration event",
        "caption": "Foil heart arch — celebration install",
    },
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/birthday-balloon-bouquets.webp",
        "alt": "Elegant balloon bouquets for a birthday or milestone celebration",
        "caption": "Bouquet arrangement — birthday delivery",
    },
]

# Customer review excerpts relevant to private celebrations (subset from home.py).
TESTIMONIALS = [
    {
        "text": "Jeff and the team are amazing. I am not local to the area so I really needed their assistance and they were simply brilliant. They provided an amazing product and went above and beyond. Top service.",
        "attr": "Out-of-town client",
        "stars": 5,
    },
    {
        "text": "You made this sick girl smile with this big unicorn balloon. Very professional and wanted to give me exactly what I wanted. We spent a few days texting back and forth and you came through with exactly what I wanted.",
        "attr": "Personal celebration",
        "stars": 5,
    },
    {
        "text": "I needed a sports themed funeral stand. I told them what I needed, they captured my vision, delivered on time, very reasonable, and had many compliments. Very tasteful and meaningful.",
        "attr": "Memorial service",
        "stars": 5,
    },
    {
        "text": "Jeff was super nice and helpful, helped me figure out the perfect thing for our son's birthday. Prompt, accommodating, great communication and friendly!",
        "attr": "Children's birthday",
        "stars": 5,
    },
]

# Icon proof bar
PROOF_ICONS = [
    {
        "svg": "premium-private-event",
        "label": "Premium Private Events",
        "note": "Weddings, showers, milestone birthdays, and personal celebrations with elevated aesthetic",
    },
    {
        "svg": "design-driven",
        "label": "Design Driven",
        "note": "Every installation is custom. Color palettes, themes, and scale are your choices, not catalog defaults",
    },
    {
        "svg": "balloon-bouquet",
        "label": "300+ Birthday Installs",
        "note": "From children's themed parties to milestone 50th and 60th celebrations",
    },
    {
        "svg": "delivery-install",
        "label": "Delivered Cleanly",
        "note": "Setup completed before guests arrive. Teardown included — host doesn't spend the morning managing vendors",
    },
]


def get_context(context):
    context.title = "Private Celebration Balloon Decor — Locally Twisted Utah"
    context.metatags = {
        "description": (
            "Custom balloon decor for birthdays, weddings, baby showers, and milestone celebrations "
            "across the Wasatch Front. 300+ birthday installs. Wedding arches, ceremony backdrops, "
            "and personal milestone decor."
        ),
        "og:title": "Private Celebration Balloon Decor — Locally Twisted",
        "og:description": (
            "Balloon decor for life's personal milestones. Birthdays, weddings, baby showers, "
            "graduations, and celebration-of-life events across Utah's Wasatch Front."
        ),
        "og:type": "website",
    }
    context.proof_categories = PROOF_CATEGORIES
    context.proof_photos = PROOF_PHOTOS
    context.testimonials = TESTIMONIALS
    context.proof_icons = PROOF_ICONS
    return context
