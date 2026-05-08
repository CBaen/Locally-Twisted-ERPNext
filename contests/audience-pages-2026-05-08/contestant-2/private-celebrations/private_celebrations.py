"""
Controller for /private-celebrations — audience page for birthday parents,
wedding planners, baby shower hosts, milestone families, and
memorial/celebration-of-life organizers.

Route: /private-celebrations
No named-client roster (buyer expects privacy). Category-level proof only.
"""
import frappe

no_cache = 1
sitemap = 1

# Category-level proof for three occasion types.
# Celebration of Life has been elevated to a standalone section (section 3)
# and is no longer a panel in this grid — it needs structural weight,
# not card-level treatment.
CELEBRATION_TYPES = [
    {
        "slug": "birthdays",
        "label": "Birthdays",
        "headline": "The party that felt like you planned it for a year.",
        "body": (
            "Custom arches, themed columns, balloon drops, and organic garlands "
            "for birthday parties that feel worth remembering. "
            "From a first birthday to a fiftieth."
        ),
        "stat": "300+",
        "stat_label": "birthday installs",
        "proof_anchor": "“Jeff was super nice and helpful, helped me figure out the perfect thing for our son's birthday.” — Sarah",
        "image": "/assets/locally_twisted/images/portfolio/optimized/birthday-smurfs-arch.webp",
        "image_alt": "Themed balloon arch for a custom birthday celebration",
    },
    {
        "slug": "weddings",
        "label": "Weddings",
        "headline": "Elegant enough for the photographs. Personal enough for the couple.",
        "body": (
            "Organic half arches, floral accents, foil heart structures, "
            "and ceremony entrance decor for weddings across the Wasatch Front. "
            "The goal is always that the balloons feel intentional, not added."
        ),
        "stat": None,
        "stat_label": None,
        "proof_anchor": "“We were seriously blown away.” — Mark, wedding guest",
        "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp",
        "image_alt": "Organic balloon half arch at a wedding ceremony",
    },
    {
        "slug": "showers",
        "label": "Baby & Bridal Showers",
        "headline": "A room that earns its own photos.",
        "body": (
            "Organic garlands, balloon walls, centerpieces, and custom photo "
            "backdrops for showers that go beyond balloons-and-streamers. "
            "Palette-matched to the shower's color story."
        ),
        "stat": None,
        "stat_label": None,
        "proof_anchor": "“They are now my go-to easy decorating plan for any of my family events.” — Tiffiny",
        "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-floral-half-arch.webp",
        "image_alt": "Floral and balloon organic arch for a bridal or baby shower",
    },
]

# Customer voice — selected quotes from verified Google reviews that speak
# to private celebration buyers. No last names per the privacy standard.
PRIVATE_REVIEWS = [
    {
        "text": (
            "Jeff was super nice and helpful, helped me figure out the perfect "
            "thing for our son's birthday. Prompt, accommodating, great "
            "communication and friendly!"
        ),
        "attr": "Sarah, birthday party",
    },
    {
        "text": (
            "I needed a sports themed funeral stand. I reached out to Locally Twisted. "
            "I told them what I needed, they captured my vision, delivered on time, "
            "very reasonable, and had many complements. Very tasteful and meaningful."
        ),
        "attr": "KJ, celebration of life",
    },
    {
        "text": (
            "I have told so many people about how much we loved the balloon creations "
            "at a friend's wedding. We were seriously blown away and my kids were "
            "delighted."
        ),
        "attr": "Mark, wedding guest",
    },
    {
        "text": (
            "Locally Twisted has done a phenomenal job on many occasions. "
            "They are now my go-to easy decorating plan for any of my family events. "
            "I don't have to do anything, my house is festive, and I get to enjoy it too!"
        ),
        "attr": "Tiffiny, longtime client",
    },
]

# Simple service capability notes.
PRIVATE_SERVICE_NOTES = [
    {
        "icon": "premium-private-event",
        "label": "Custom Design for Every Event",
        "detail": "No template packages. Every celebration is designed from scratch around your vision and palette.",
    },
    {
        "icon": "organic-garland",
        "label": "Organic & Premium Builds",
        "detail": "Organic garlands, floral accents, foil structures, and custom sculptures. The full range.",
    },
    {
        "icon": "delivery-install",
        "label": "Delivered and Installed",
        "detail": "Delivery, setup, and optional teardown included. You don't touch the balloons.",
    },
    {
        "icon": "trusted-partner",
        "label": "Personal, Start to Finish",
        "detail": "Direct conversation with the team from first quote to install. No middleman, no form letter.",
    },
]


def get_context(context):
    context.title = "Private Celebrations — Locally Twisted Balloon Decor"
    context.metatags = {
        "description": (
            "Custom balloon decor for birthdays, weddings, baby showers, "
            "and celebrations of life across the Wasatch Front. "
            "Designed from scratch for every event."
        ),
        "og:title": "Private Celebrations — Locally Twisted",
        "og:description": (
            "Custom balloon arches, organic garlands, and milestone decor "
            "for birthdays, weddings, showers, and celebrations of life."
        ),
        "og:type": "website",
    }
    context.celebration_types = CELEBRATION_TYPES
    context.private_reviews = PRIVATE_REVIEWS
    context.private_service_notes = PRIVATE_SERVICE_NOTES
    return context
