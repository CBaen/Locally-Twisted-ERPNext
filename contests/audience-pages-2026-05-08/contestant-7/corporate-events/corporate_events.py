"""Controller for /corporate-events audience landing page.

Audience: Marketing teams, brand activations, store openings, broadcaster
events, bank/credit-union community days, corporate parties.

Buyer posture: Brand-safe, on-color, repeatable, professional, billable
through AP. These buyers are accountable to a brand standards document
and a budget approval chain. They need proof of peer-company relationships,
a clean billing process, and a vendor who can match their color system.
"""
import frappe

no_cache = 1
sitemap = 1

# Real corporate clients from the approved roster.
CORPORATE_CLIENTS = [
    "Chick-Fil-A",
    "Texas Roadhouse",
    "Applebee's",
    "Chili's",
    "Honey Baked Ham",
    "PotBelly",
    "Ancestry",
    "Megaplex",
    "Paramount",
    "KSL",
    "KUTV",
    "FOX13",
    "LVT",
    "Clear",
    "Henry Schein",
    "Museum of Illusion",
    "Lux",
    "Zions Bank",
    "America First Credit Union",
    "Young Automotive",
    "IHC",
    "Mountain Star Medical",
    "SeaQuest",
    "Fidelity",
    "Morgan Stanley",
    "Utah Jazz",
    "Alpine Events",
    "In the Events",
    "FanX",
    "The Boiler Room",
]

# Industry groupings for the proof section — makes the brand-safe claim concrete.
CORPORATE_SECTORS = [
    {
        "sector": "Financial Services",
        "clients": ["Zions Bank", "America First Credit Union", "Fidelity", "Morgan Stanley"],
        "note": "Community days, branch grand openings, and annual company events.",
    },
    {
        "sector": "Media & Broadcast",
        "clients": ["KSL", "KUTV", "FOX13", "Paramount", "Megaplex"],
        "note": "Broadcast studio events, premiere screenings, and on-air installations.",
    },
    {
        "sector": "Hospitality & Dining",
        "clients": ["Chick-Fil-A", "Texas Roadhouse", "Applebee's", "Chili's", "Honey Baked Ham", "PotBelly"],
        "note": "Grand openings, anniversary events, and customer appreciation days.",
    },
    {
        "sector": "Healthcare",
        "clients": ["IHC", "Mountain Star Medical"],
        "note": "Community health events, staff celebrations, and facility grand openings. Latex-free options available for healthcare and allergy-sensitive environments.",
    },
]

# Capability pillars specific to corporate buyers.
CORPORATE_CAPABILITIES = [
    {
        "icon": "/assets/locally_twisted/icons/brand/trusted-partner.svg",
        "label": "Brand Color Match",
        "body": "Custom color mixing for balloon decor that matches your brand standards document, not a generic rainbow.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/professional.svg",
        "label": "Repeatable Process",
        "body": "Documented quote-to-install workflow. Same coordinator, same quality, whether it's the first event or the tenth.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "AP-Ready Billing",
        "body": "Purchase orders accepted. W-9 and vendor onboarding documents available. Invoice format matched to your AP requirements.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/event-stage.svg",
        "label": "On-Camera Ready",
        "body": "Broadcast-safe installations sized and positioned for camera framing, photo backdrops, and livestream visibility.",
    },
]

# Featured corporate install proof.
CORPORATE_PROOF = [
    {
        "label": "Store Opening",
        "heading": "Brand entrance arch at a Utah grand opening",
        "body": "Custom-color logo arch installed at the entrance, matching brand PMS values. Delivery timed with ribbon-cutting ceremony.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "image_alt": "Custom branded balloon arch at a corporate store opening entrance",
    },
    {
        "label": "Festival Photo Moment",
        "heading": "Branded backdrop for a corporate outdoor event",
        "body": "Large-format photo backdrop with branded color system. Weber State corporate festival installation visible to television cameras.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "image_alt": "Large branded balloon backdrop at a corporate outdoor festival",
    },
    {
        "label": "University Partnership",
        "heading": "WSU arch and bouquet install",
        "body": "Full arch with complementary bouquets in institutional colors. Repeat relationship for campus and community events.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "image_alt": "WSU branded balloon arch and bouquets at a university event",
    },
]


def get_context(context):
    context.title = "Corporate Events — Locally Twisted"
    context.metatags = {
        "description": (
            "Professional balloon decor for corporate events, brand activations, "
            "store openings, and company celebrations across Utah. Named clients include "
            "Zions Bank, KSL, Chick-Fil-A, IHC, and the Utah Jazz."
        ),
        "og:title": "Corporate Event Balloon Decor — Locally Twisted",
        "og:description": (
            "Brand-safe, on-color, repeatable balloon installations for Utah "
            "corporate events. AP billing, color matching, and broadcast-ready installs."
        ),
        "og:type": "website",
    }
    context.corporate_clients = CORPORATE_CLIENTS
    context.corporate_sectors = CORPORATE_SECTORS
    context.corporate_capabilities = CORPORATE_CAPABILITIES
    context.corporate_proof = CORPORATE_PROOF
    return context
