"""
Private Celebrations audience landing page — /private-celebrations

No named-client roster (it's private celebrations — privacy expected).
Proof is category-level: birthday installs, weddings, showers, memorials,
and milestone events. Uses review excerpts without full names.
"""
import frappe

no_cache = 1
sitemap = 1

# Category-level proof (no named clients — privacy is the point).
CELEBRATION_TYPES = [
    {
        "icon": "premium-private-event",
        "title": "Birthdays",
        "body": (
            "From first birthdays to milestone 50ths. Themed arches, "
            "backdrop photo moments, bouquets, and custom sculptural pieces "
            "for at-home and venue celebrations."
        ),
        "proof": "300+ birthday installs across the Wasatch Front",
    },
    {
        "icon": "organic-garland",
        "title": "Weddings",
        "body": (
            "Organic half-arches, foil heart backdrops, ceremony garlands, "
            "and reception accent decor. Palette matched to your florals."
        ),
        "proof": "Ceremonies and receptions across Utah venues",
    },
    {
        "icon": "balloon-cluster",
        "title": "Baby Showers & Gender Reveals",
        "body": (
            "Soft organic arrangements, reveal arches, and themed decor "
            "for at-home and venue showers."
        ),
        "proof": "Intimate gatherings and venue events",
    },
    {
        "icon": "balloon-bouquet",
        "title": "Milestone Celebrations",
        "body": (
            "Anniversaries, retirements, graduations, and family reunions. "
            "Custom sculptures and themed installs for one-of-a-kind moments."
        ),
        "proof": "Family milestones of every kind",
    },
    {
        "icon": "balloon-pair",
        "title": "Memorials & Celebrations of Life",
        "body": (
            "Tasteful, meaningful arrangements for celebration-of-life services. "
            "Sports themes, favorite colors, and personal tributes handled with care."
        ),
        "proof": "Verified by customer reviews",
    },
]

# Curated review excerpts (using abbreviated names from real Google reviews).
TESTIMONIALS = [
    {
        "display_name": "Sara M.",
        "event": "longtime client, family events",
        "text": (
            "Jeff has been listed in my phone for 7-ish years as 'balloon guy' "
            "and has been my go-to for that long. They make every event I plan "
            "easier and extra special."
        ),
    },
    {
        "display_name": "KJSCOTT",
        "event": "celebration of life",
        "text": (
            "I needed a sports themed funeral stand. I told them what I needed, "
            "they captured my vision, delivered on time, very reasonable, "
            "and had many complements. Very tasteful and meaningful."
        ),
    },
    {
        "display_name": "Sarah J.",
        "event": "birthday",
        "text": (
            "Jeff was super nice and helpful, helped me figure out the perfect thing "
            "for our son's birthday. Prompt, accommodating, great communication and friendly!"
        ),
    },
    {
        "display_name": "Tiffiny L.",
        "event": "family events",
        "text": (
            "They are kind, friendly, and have done some rush jobs for me. "
            "They are now my go-to easy decorating plan for any of my family events. "
            "I don't have to do anything, my house is festive, and I get to enjoy it too!"
        ),
    },
    {
        "display_name": "Alisha",
        "event": "personal",
        "text": (
            "You made this sick girl smile with this big unicorn balloon. "
            "Very professional and wanted to give me exactly what I wanted. "
            "You came through with exactly what I wanted. Thank you!"
        ),
    },
    {
        "display_name": "LuAnn K.",
        "event": "Mother's Day gift",
        "text": (
            "They went above and beyond what they needed to do for my mom's "
            "Mother's Day gift. I will definitely order again!"
        ),
    },
]

# Service notes specific to private celebration buyers.
BUYER_NOTES = [
    {
        "heading": "Same-Day Delivery Available",
        "body": (
            "Need decor quickly? Same-day balloon delivery is available "
            "for in-stock items across the Salt Lake and Ogden areas."
        ),
    },
    {
        "heading": "At-Home or Venue",
        "body": (
            "Locally Twisted delivers and installs at private residences, "
            "backyards, party venues, and event spaces across the Wasatch Front."
        ),
    },
    {
        "heading": "Custom to Your Vision",
        "body": (
            "Tell LT what you're imagining — colors, theme, scale — "
            "and the team works out the best execution for your space and budget."
        ),
    },
    {
        "heading": "Rush Orders Welcome",
        "body": (
            "Planning on short notice? The team has handled rush jobs for "
            "countless families. Reach out and ask what's possible."
        ),
    },
]


def get_context(context):
    context.title = "Private Celebrations — Locally Twisted"
    context.metatags = {
        "description": (
            "Custom balloon decor for private celebrations along the Wasatch Front: "
            "birthdays, weddings, baby showers, milestones, and celebrations of life. "
            "Same-day delivery available."
        ),
        "og:title": "Private Celebrations — Locally Twisted",
        "og:description": (
            "Birthday arches, wedding garlands, baby showers, and celebration-of-life "
            "decor for private events across Utah. Custom to your vision."
        ),
        "og:type": "website",
    }
    context.celebration_types = CELEBRATION_TYPES
    context.testimonials = TESTIMONIALS
    context.buyer_notes = BUYER_NOTES
    return context
