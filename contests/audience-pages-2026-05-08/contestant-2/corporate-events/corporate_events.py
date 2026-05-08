"""
Controller for /corporate-events — audience page for marketing teams,
brand activations, store openings, broadcaster events, bank/credit-union
community days, and corporate parties.

Route: /corporate-events
"""
import frappe

no_cache = 1
sitemap = 1

# Named corporate clients — drawn directly from the approved roster.
# Grouped to show range of industry verticals the buyer's procurement team
# can recognize.
CORPORATE_CLIENTS = {
    "Food & Hospitality": [
        "Chick-Fil-A", "Texas Roadhouse", "Applebee's",
        "Chili's", "Honey Baked Ham", "PotBelly",
    ],
    "Media & Entertainment": [
        "KSL", "KUTV", "FOX13", "Megaplex", "Paramount",
        "FanX", "Museum of Illusion",
    ],
    "Finance & Professional": [
        "Zions Bank", "America First Credit Union",
        "Fidelity", "Morgan Stanley", "LVT",
    ],
    "Technology & Healthcare": [
        "Ancestry", "Henry Schein", "IHC",
        "Mountain Star Medical", "SeaQuest", "Clear",
    ],
    "Events & Automotive": [
        "Utah Jazz", "Alpine Events", "In the Events",
        "Young Automotive", "The Boiler Room", "Lux",
    ],
}

# Three proof-story beats for the corporate page.
CORPORATE_PROOF_STORIES = [
    {
        "client": "Weber State University / WeberStock",
        "headline": "Festival-scale photo moment",
        "body": (
            "A full custom photo-op structure built for WeberStock — "
            "sized to pull a crowd and hold detail across a full outdoor festival day. "
            "The kind of branded moment that earns its place in the event recap reel."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "image_alt": "Large branded photo-moment balloon installation at WeberStock festival",
    },
    {
        "client": "Corporate Brand Entrances",
        "headline": "On-brand. On-color.",
        "body": (
            "Balloon arches and column pairs built to spec against a brand's "
            "exact color system — Pantone-matched latex where available, "
            "custom foil for premium moments. "
            "Delivered, installed, and cleared on a schedule your ops team can build around."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "image_alt": "Corporate logo balloon arch installed at a branded business entrance",
    },
    {
        "client": "IHC / Mountain Star Medical",
        "headline": "Healthcare and professional events",
        "body": (
            "Balloon decor for hospital grand openings, staff appreciation, "
            "and community health fairs — professional in scale and tone, "
            "appropriate for institutional contexts. "
            "Invoiced to accounts payable with itemized documentation."
        ),
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Mock up IHC.png",
        "image_alt": "Balloon arch mockup for Intermountain Health Center event",
    },
]

# Service notes specific to what corporate buyers need to hear.
CORPORATE_SERVICE_NOTES = [
    {
        "label": "Color Matched to Brand Standards",
        "detail": "Latex and foil matched to your color system. Custom builds available for logo-shaped balloon art.",
        "icon": "design-driven",
    },
    {
        "label": "Invoiced Through Accounts Payable",
        "detail": "Net-30 invoicing available for established accounts. Itemized line items for your records.",
        "icon": "trusted-partner",
    },
    {
        "label": "Scalable for Any Venue",
        "detail": "From lobby ribbon cuttings to full convention-floor activations. Install crew sizes to match.",
        "icon": "event-stage",
    },
    {
        "label": "Insured and Professional",
        "detail": "COI available on request. On-time install and coordinated strike so your ops team stays on schedule.",
        "icon": "professional",
    },
]


def get_context(context):
    context.title = "Corporate Events — Locally Twisted Balloon Decor"
    context.metatags = {
        "description": (
            "Professional balloon decor for corporate events, brand activations, "
            "store openings, and company parties across Utah. Trusted by KSL, FOX13, "
            "Chick-Fil-A, Zions Bank, Fidelity, Utah Jazz, and more."
        ),
        "og:title": "Corporate Events — Locally Twisted",
        "og:description": (
            "Brand-matched balloon decor for corporate events, grand openings, "
            "and branded activations across the Wasatch Front."
        ),
        "og:type": "website",
    }
    context.corporate_clients = CORPORATE_CLIENTS
    context.corporate_proof_stories = CORPORATE_PROOF_STORIES
    context.corporate_service_notes = CORPORATE_SERVICE_NOTES
    return context
