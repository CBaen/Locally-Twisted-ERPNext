"""Controller for /corporate-events audience landing page.

Serves marketing teams, brand activations, store openings,
broadcaster events, bank/credit-union community days, and
corporate parties. Buyer posture: brand-safe, on-color, repeatable,
professional, billable through AP.
"""
import frappe

no_cache = 1
sitemap = 1

# Corporate client roster — from the approved brief.
CORPORATE_CLIENTS = [
    "Chick-Fil-A", "Texas Roadhouse", "Applebee's", "Chili's",
    "Honey Baked Ham", "PotBelly", "Ancestry", "Megaplex", "Paramount",
    "KSL", "KUTV", "FOX13", "LVT", "Clear", "Henry Schein",
    "Museum of Illusion", "Lux", "Zions Bank", "America First Credit Union",
    "Young Automotive", "IHC", "Mountain Star Medical", "SeaQuest",
    "Fidelity", "Morgan Stanley", "Utah Jazz", "Alpine Events",
    "In the Events", "FanX", "The Boiler Room",
]

# Case studies — anchored to real client work.
CASE_STUDIES = [
    {
        "client": "KSL / KUTV / FOX13",
        "headline": "On-Brand for Broadcasters",
        "body": (
            "Utah's top broadcast networks turn to Locally Twisted for "
            "on-air event decor, studio activations, and viewer-facing "
            "installations. Color matching, brand-safe balloon palettes, "
            "and tight install windows around broadcast schedules."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "alt": "Corporate logo balloon arch installed at a branded event entrance",
        "tag": "Broadcast & Media",
    },
    {
        "client": "Zions Bank / America First Credit Union / Morgan Stanley / Fidelity",
        "headline": "Financial Institutions and Community Days",
        "body": (
            "Financial brands need decor that says 'celebration' without "
            "saying 'party supply store.' Locally Twisted produces grand "
            "opening arches, branch anniversaries, and community day "
            "activations for Utah's major financial institutions — "
            "professional, on-brand, and clean."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "Corporate balloon arch and bouquets at a professional event",
        "tag": "Financial & Professional",
    },
    {
        "client": "Chick-Fil-A / Texas Roadhouse / Applebee's / Chili's",
        "headline": "Restaurant Grand Openings and Activations",
        "body": (
            "National restaurant groups trust Locally Twisted for Utah "
            "grand openings, anniversary events, and drive-thru activations. "
            "Corporate brand standards, franchise-approved color palettes, "
            "and repeatable install formats across multiple locations."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "alt": "Large branded balloon installation at a corporate event",
        "tag": "Restaurant & Retail",
    },
]

# Proof pillars.
PROOF_PILLARS = [
    {
        "icon": "/assets/locally_twisted/icons/brand/corporate-entrance.svg",
        "label": "Brand-Safe",
        "body": "Balloon palettes matched to corporate brand standards. Color-accurate, AP-ready.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/trusted-partner.svg",
        "label": "Trusted Partner",
        "body": "30+ corporate and franchise clients across Utah. Repeat engagements the norm, not the exception.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/professional.svg",
        "label": "Professional",
        "body": "Invoice-ready, insurance documentation on request. Vendor-management friendly.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "Clean Install",
        "body": "On-time setup and strike coordinated with your venue team. No surprises on event day.",
    },
]

# Gallery images.
GALLERY_IMAGES = [
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "alt": "Corporate logo balloon arch at branded event",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "alt": "Large corporate event balloon installation",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "Corporate arch and balloon bouquets at professional event",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/themed decor/Logo arch.png",
        "alt": "Custom logo balloon arch for corporate event",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/latex free decor/ihc heart columns latex free.png",
        "alt": "IHC latex-free corporate balloon columns",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/themed decor/Weberstock organic garland.png",
        "alt": "Organic balloon garland at Weberstock corporate event",
    },
]

# Service differentiators for corporate buyers.
CORPORATE_SERVICES = [
    "Grand Opening Arches",
    "Brand-Color Matched Decor",
    "Logo Integration",
    "Lobby & Entrance Installations",
    "Corporate Party Backdrops",
    "Product Launch Activations",
    "Drive-Thru & Exterior Decor",
    "Latex-Free Options Available",
]


def get_context(context):
    context.title = "Corporate Events — Locally Twisted"
    context.metatags = {
        "description": (
            "Professional balloon decor for corporate events, brand activations, "
            "store openings, and company parties across Utah. Trusted by KSL, "
            "KUTV, Zions Bank, Chick-Fil-A, Morgan Stanley, and 25+ Utah "
            "corporate clients. Brand-safe, AP-invoiceable, clean install."
        ),
        "og:title": "Corporate Event Balloon Decor — Locally Twisted",
        "og:description": (
            "On-brand balloon decor for corporate events, grand openings, "
            "and professional activations across the Wasatch Front."
        ),
        "og:type": "website",
    }
    context.corporate_clients = CORPORATE_CLIENTS
    context.case_studies = CASE_STUDIES
    context.proof_pillars = PROOF_PILLARS
    context.gallery_images = GALLERY_IMAGES
    context.corporate_services = CORPORATE_SERVICES
    return context
