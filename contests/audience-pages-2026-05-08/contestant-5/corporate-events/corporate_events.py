"""Controller for /corporate-events audience landing page.

Corporate Events: marketing teams, brand activations, store openings,
broadcaster events, bank/credit-union community days, corporate parties.
Buyer posture: brand-safe, on-color, repeatable, professional, billable through AP.
"""

no_cache = 1
sitemap = 1

# Named corporate clients from the approved roster, grouped for display.
CORPORATE_CLIENTS = [
    # Food & hospitality
    {"name": "Chick-Fil-A", "sector": "Food & Hospitality"},
    {"name": "Texas Roadhouse", "sector": "Food & Hospitality"},
    {"name": "Applebee's", "sector": "Food & Hospitality"},
    {"name": "Chili's", "sector": "Food & Hospitality"},
    {"name": "Honey Baked Ham", "sector": "Food & Hospitality"},
    {"name": "PotBelly", "sector": "Food & Hospitality"},
    # Media & entertainment
    {"name": "KSL", "sector": "Broadcast Media"},
    {"name": "KUTV", "sector": "Broadcast Media"},
    {"name": "FOX13", "sector": "Broadcast Media"},
    {"name": "Megaplex", "sector": "Entertainment"},
    {"name": "Paramount", "sector": "Entertainment"},
    {"name": "Museum of Illusion", "sector": "Entertainment"},
    {"name": "FanX", "sector": "Entertainment"},
    # Financial
    {"name": "Zions Bank", "sector": "Banking & Finance"},
    {"name": "America First Credit Union", "sector": "Banking & Finance"},
    {"name": "Fidelity", "sector": "Banking & Finance"},
    {"name": "Morgan Stanley", "sector": "Banking & Finance"},
    # Technology & services
    {"name": "Ancestry", "sector": "Technology"},
    {"name": "LVT", "sector": "Technology"},
    {"name": "Clear", "sector": "Technology"},
    {"name": "Henry Schein", "sector": "Healthcare Services"},
    # Medical
    {"name": "IHC", "sector": "Healthcare"},
    {"name": "Mountain Star Medical", "sector": "Healthcare"},
    # Recreation & retail
    {"name": "SeaQuest", "sector": "Recreation"},
    {"name": "Utah Jazz", "sector": "Sports & Recreation"},
    {"name": "Young Automotive", "sector": "Automotive"},
    {"name": "Lux", "sector": "Events & Venue"},
    {"name": "Alpine Events", "sector": "Events & Venue"},
    {"name": "In the Events", "sector": "Events & Venue"},
    {"name": "The Boiler Room", "sector": "Venue"},
]

# Installed work proof — photo references for the visual proof section.
PROOF_PHOTOS = [
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "alt": "Corporate branded balloon arch installed at a company event entrance",
        "caption": "Brand entrance arch — corporate event",
    },
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "alt": "Large event balloon photo backdrop for a branded corporate festival",
        "caption": "Photo backdrop — branded festival install",
    },
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "Balloon arch and bouquets for a Weber State corporate partnership event",
        "caption": "Arch with bouquets — partnership event",
    },
    {
        "path": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Mock up IHC.png",
        "alt": "Balloon decor mockup for Intermountain Healthcare event",
        "caption": "Healthcare brand event — IHC install",
    },
]

# Icon proof bar
PROOF_ICONS = [
    {
        "svg": "corporate-entrance",
        "label": "Corporate Entrance Ready",
        "note": "Brand-safe arches, columns, and installations for lobbies, stage entrances, and activation zones",
    },
    {
        "svg": "trusted-partner",
        "label": "Trusted Partner",
        "note": "Named clients across broadcast, banking, healthcare, technology, and entertainment sectors",
    },
    {
        "svg": "professional",
        "label": "Professional",
        "note": "Insured, on-brand, and punctual. Invoiceable through AP with standard vendor documentation",
    },
    {
        "svg": "delivery-install",
        "label": "Delivered Cleanly",
        "note": "Setup and strike included. The install is done before guests arrive and gone before venue close",
    },
]


def get_context(context):
    context.title = "Corporate Event Balloon Decor — Locally Twisted Utah"
    context.metatags = {
        "description": (
            "Custom balloon decor for brand activations, corporate events, store openings, "
            "broadcaster events, and company gatherings. Serving Utah's professional event market "
            "with named clients in broadcast, banking, healthcare, and entertainment."
        ),
        "og:title": "Corporate Event Balloon Decor — Locally Twisted",
        "og:description": (
            "Brand-safe balloon installations for professional events. Named clients include "
            "KSL, KUTV, FOX13, Zions Bank, America First CU, Ancestry, IHC, Utah Jazz, and more."
        ),
        "og:type": "website",
    }
    context.corporate_clients = CORPORATE_CLIENTS
    context.proof_photos = PROOF_PHOTOS
    context.proof_icons = PROOF_ICONS
    return context
