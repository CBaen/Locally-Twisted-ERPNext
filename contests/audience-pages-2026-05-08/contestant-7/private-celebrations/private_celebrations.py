"""Controller for /private-celebrations audience landing page.

Audience: Birthday parents, wedding planners, baby shower hosts, milestone
families, memorial/celebration-of-life organizers.

Buyer posture: Personal, milestone-emotional, taste-elevated, gift-feeling.
These buyers are often making a purchase for someone they love — this is
not a transactional purchase, it is an expression of care. They want to
feel like Locally Twisted will understand the occasion and make it
beautiful, not just functional. Privacy matters — they are not looking to
be publicly named as clients.

No named-client roster for this page. Use category-level proof, anonymized
photo context, and testimonial language. The brief explicitly notes this
audience "expects privacy."
"""
import frappe

no_cache = 1
sitemap = 1

# Category-level proof claims — verified by business context, not invented.
CATEGORY_PROOF = [
    {
        "category": "Birthdays",
        "icon": "/assets/locally_twisted/icons/brand/balloon-pair.svg",
        "headline": "300+ birthday installs",
        "detail": "From first birthdays to milestone decades. Delivered, installed, and ready before the guests arrive.",
    },
    {
        "category": "Weddings",
        "icon": "/assets/locally_twisted/icons/brand/organic-garland.svg",
        "headline": "Weddings across the Wasatch Front",
        "detail": "Ceremony arches, reception garlands, and organic balloon decor in palettes matched to your flowers and venue.",
    },
    {
        "category": "Baby Showers",
        "icon": "/assets/locally_twisted/icons/brand/balloon-cluster.svg",
        "headline": "Baby showers and gender reveals",
        "detail": "Tasteful, photograph-ready decor for the moments that matter before the baby arrives.",
    },
    {
        "category": "Memorials",
        "icon": "/assets/locally_twisted/icons/brand/balloon-bouquet.svg",
        "headline": "Memorials and celebrations of life",
        "detail": "Respectful, personal balloon arrangements for tribute events. Previous clients have described it as exactly right.",
    },
]

# Installation photo proof (no named clients — anonymized by category context).
PRIVATE_INSTALLS = [
    {
        "occasion": "Wedding",
        "heading": "Organic half-arch at a Wasatch Front ceremony",
        "body": "Organic-style balloon arch in venue-matched palette. Installed before the ceremony, removed after reception.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp",
        "image_alt": "Organic balloon half-arch installed at a wedding ceremony",
    },
    {
        "occasion": "Wedding",
        "heading": "Floral-style half-arch at a wedding reception",
        "body": "Flower-shaped balloon clusters in a soft white and blush palette. Ceremony-to-reception transition decor.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/wedding-floral-half-arch.webp",
        "image_alt": "Floral-style balloon half-arch at a wedding reception",
    },
    {
        "occasion": "Celebration",
        "heading": "Foil heart arch for a milestone celebration",
        "body": "Custom foil heart arch in celebration colors. Ready before guests arrive, photographed beautifully.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/wedding-foil-heart-arch.webp",
        "image_alt": "Foil heart balloon arch at a private celebration",
    },
]

# Testimonial excerpts for private buyers — voice of the customer.
TESTIMONIALS = [
    {
        "text": "Jeff has been listed in my phone for 7-ish years as 'balloon guy' and has been my go-to for that long. They make every event I plan easier and extra special.",
        "attr": "Sara, longtime client",
        "event": "Family events",
    },
    {
        "text": "I reached out with a vision for a sports-themed funeral stand. They captured it, delivered on time, and the result was very tasteful and meaningful.",
        "attr": "KJ, memorial client",
        "event": "Celebration of life",
    },
    {
        "text": "Jeff was super nice and helpful, helped me figure out the perfect thing for our son's birthday. Prompt, accommodating, great communication and friendly.",
        "attr": "Sarah, birthday parent",
        "event": "Birthday",
    },
]

# Capability pillars for private celebration buyers.
PRIVATE_CAPABILITIES = [
    {
        "icon": "/assets/locally_twisted/icons/brand/premium-private-event.svg",
        "label": "Taste-Matched",
        "body": "Palette, scale, and style matched to your venue, your flowers, and your sense of the moment.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "Ready Before Guests",
        "body": "Installation is complete before your event begins. No scramble, no last-minute. You enjoy it, not manage it.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/design-driven.svg",
        "label": "Photograph-Ready",
        "body": "Decor designed to look beautiful in photos. The moments you capture should have a backdrop worth keeping.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/trusted-partner.svg",
        "label": "Private by Default",
        "body": "Private events stay private. Client names and photos are not shared without permission.",
    },
]


def get_context(context):
    context.title = "Private Celebrations — Locally Twisted"
    context.metatags = {
        "description": (
            "Balloon decor for Utah weddings, birthdays, baby showers, milestones, "
            "and celebrations of life. Tasteful, photograph-ready installations "
            "delivered and set up before your guests arrive."
        ),
        "og:title": "Private Celebration Balloon Decor — Locally Twisted",
        "og:description": (
            "Custom balloon installations for Utah private celebrations — weddings, "
            "birthdays, memorials, and milestones. Delivered and ready before guests arrive."
        ),
        "og:type": "website",
    }
    context.category_proof = CATEGORY_PROOF
    context.private_installs = PRIVATE_INSTALLS
    context.testimonials = TESTIMONIALS
    context.private_capabilities = PRIVATE_CAPABILITIES
    return context
