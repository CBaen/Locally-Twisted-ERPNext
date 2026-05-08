"""Controller for /private-celebrations audience landing page.

Serves birthday parents, wedding planners, baby shower hosts,
milestone families, and memorial/celebration-of-life organizers.
No named clients (privacy); proof is category-level and
anonymized per the brief.
"""
import frappe

no_cache = 1
sitemap = 1

# Celebration types — proof categories for the anonymous private market.
CELEBRATION_TYPES = [
    {
        "label": "Birthdays",
        "icon": "/assets/locally_twisted/icons/brand/balloon-cluster.svg",
        "proof": "300+ birthday installs",
        "body": (
            "From first birthdays to milestone decades, custom balloon "
            "decor sized for living rooms, backyards, and venue rental spaces."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/birthday-smurfs-arch.webp",
        "alt": "Custom Smurfs-themed birthday balloon arch and backdrop",
    },
    {
        "label": "Weddings",
        "icon": "/assets/locally_twisted/icons/brand/organic-garland.svg",
        "proof": "Wasatch Front weddings",
        "body": (
            "Organic arches, ceremony backdrops, and reception decor "
            "in coordinated palettes. Latex-free options available for "
            "allergy-sensitive ceremonies."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp",
        "alt": "Elegant organic balloon half-arch for a wedding ceremony",
    },
    {
        "label": "Baby Showers",
        "icon": "/assets/locally_twisted/icons/brand/balloon-bouquet.svg",
        "proof": "Deliveries across the valley",
        "body": (
            "Balloon bouquets, organic garlands, and full decor packages "
            "delivered to your venue — or installed on-site for larger showers."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/birthday-balloon-bouquets.webp",
        "alt": "Balloon bouquets for a baby shower celebration",
    },
    {
        "label": "Memorials",
        "icon": "/assets/locally_twisted/icons/brand/premium-private-event.svg",
        "proof": "Trusted for celebrations of life",
        "body": (
            "Celebration-of-life installations that honor a person with "
            "thoughtfulness and care. Sports themes, color tributes, and "
            "custom builds available on short notice."
        ),
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Organic decor/Organic photo opt.png",
        "alt": "Tasteful organic balloon installation for a celebration of life",
    },
]

# The KJSCOTT review — memorial/celebration-of-life proof.
# Elevated to a standalone position BEFORE the category grid.
MEMORIAL_PROOF = {
    "text": (
        "I needed a sports themed funeral stand. I told them what I "
        "needed, they captured my vision, delivered on time, very "
        "reasonable, and had many compliments. Very tasteful and "
        "meaningful."
    ),
    "attr": "— Google review, celebration of life",
}

# Testimonial excerpts — from real Google reviews, anonymized per pattern.
# Source: home.py REVIEW_QUOTES — selected for private-event relevance.
# Note: KJSCOTT memorial review is pulled into memorial_proof (pre-grid position).
TESTIMONIALS = [
    {
        "text": (
            "I have told so many people about how much we loved the balloon "
            "creations at a friend's wedding. We were seriously blown away "
            "and my kids were delighted."
        ),
        "attr": "— Google review, wedding",
    },
    {
        "text": (
            "Jeff was super nice and helpful, helped me figure out the "
            "perfect thing for our son's birthday. Prompt, accommodating, "
            "great communication and friendly!"
        ),
        "attr": "— Google review, birthday",
    },
    {
        "text": (
            "Locally Twisted has done a phenomenal job on many occasions. "
            "They are now my go-to easy decorating plan for any of my "
            "family events. I don't have to do anything, my house is "
            "festive, and I get to enjoy it too!"
        ),
        "attr": "— Google review, repeat family client",
    },
    {
        "text": (
            "Amazing balloon arrangements — we had so many compliments. "
            "Jeff was easy to work with and the setup was exactly what we "
            "had in mind. Will definitely use again for future events."
        ),
        "attr": "— Google review, milestone celebration",
    },
]

# Gallery — private event images.
GALLERY_IMAGES = [
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/birthday-smurfs-arch.webp",
        "alt": "Themed birthday balloon arch",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp",
        "alt": "Organic half arch for wedding ceremony",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/wedding-foil-heart-arch.webp",
        "alt": "Foil heart balloon arch for wedding or celebration",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/wedding-floral-half-arch.webp",
        "alt": "Floral balloon half arch for private event",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/birthday-dolphin-backdrop.webp",
        "alt": "Custom dolphin-themed birthday balloon backdrop",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/birthday-pirate-column.webp",
        "alt": "Custom pirate-themed birthday balloon column",
    },
]

# Proof pillars.
PROOF_PILLARS = [
    {
        "icon": "/assets/locally_twisted/icons/brand/premium-private-event.svg",
        "label": "Milestone-Ready",
        "body": "Designed for the moments that deserve to be remembered. Every detail considered.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/design-driven.svg",
        "label": "Design Driven",
        "body": "Custom builds matched to your theme, color, and vision — not a catalog selection.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "Delivered & Installed",
        "body": "Full delivery, setup, and optional strike so you can focus on being present.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/trusted-partner.svg",
        "label": "Personal Attention",
        "body": "Jeff and his team work directly with you. No order-and-wait experience.",
    },
]


def get_context(context):
    context.title = "Private Celebrations — Locally Twisted"
    context.metatags = {
        "description": (
            "Custom balloon decor for birthdays, weddings, baby showers, "
            "milestone celebrations, and memorial events across the Wasatch "
            "Front. 300+ birthday installs. Weddings, showers, and "
            "celebrations of life with personal attention and clean delivery."
        ),
        "og:title": "Private Celebration Balloon Decor — Locally Twisted",
        "og:description": (
            "Custom balloon decor for birthdays, weddings, baby showers, "
            "and milestone celebrations along the Wasatch Front."
        ),
        "og:type": "website",
    }
    context.celebration_types = CELEBRATION_TYPES
    context.memorial_proof = MEMORIAL_PROOF
    context.testimonials = TESTIMONIALS
    context.gallery_images = GALLERY_IMAGES
    context.proof_pillars = PROOF_PILLARS
    return context
