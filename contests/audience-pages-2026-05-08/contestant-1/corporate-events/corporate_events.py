"""
Corporate Events audience landing page — /corporate-events

Proves LT's corporate event scope: retail activations, broadcaster events,
branded store openings, corporate parties, bank/credit-union community days,
media events, and brand-safe corporate installations.
"""
import frappe

no_cache = 1
sitemap = 1

# Curated corporate client list from the approved roster.
CORPORATE_CLIENTS = [
    {"name": "Ancestry", "category": "Technology"},
    {"name": "Zions Bank", "category": "Financial Services"},
    {"name": "America First Credit Union", "category": "Financial Services"},
    {"name": "Fidelity", "category": "Financial Services"},
    {"name": "Morgan Stanley", "category": "Financial Services"},
    {"name": "KSL", "category": "Media & Broadcasting"},
    {"name": "KUTV", "category": "Media & Broadcasting"},
    {"name": "FOX13", "category": "Media & Broadcasting"},
    {"name": "Paramount", "category": "Entertainment"},
    {"name": "Megaplex", "category": "Entertainment"},
    {"name": "Utah Jazz", "category": "Sports & Entertainment"},
    {"name": "FanX", "category": "Entertainment Events"},
    {"name": "Chick-Fil-A", "category": "Food & Beverage"},
    {"name": "Texas Roadhouse", "category": "Food & Beverage"},
    {"name": "Applebee's", "category": "Food & Beverage"},
    {"name": "Chili's", "category": "Food & Beverage"},
    {"name": "Honey Baked Ham", "category": "Food & Beverage"},
    {"name": "PotBelly", "category": "Food & Beverage"},
    {"name": "IHC", "category": "Healthcare"},
    {"name": "Mountain Star Medical", "category": "Healthcare"},
    {"name": "Henry Schein", "category": "Healthcare"},
    {"name": "Young Automotive", "category": "Automotive"},
    {"name": "Clear", "category": "Technology"},
    {"name": "LVT", "category": "Technology"},
    {"name": "Museum of Illusion", "category": "Entertainment"},
    {"name": "SeaQuest", "category": "Entertainment"},
    {"name": "Lux", "category": "Hospitality"},
    {"name": "The Boiler Room", "category": "Events"},
    {"name": "Alpine Events", "category": "Events"},
    {"name": "In the Events", "category": "Events"},
]

# Service features most relevant to corporate buyers.
AUDIENCE_SERVICES = [
    {
        "icon": "corporate-entrance",
        "title": "Branded Entrances & Logo Arches",
        "body": (
            "Color-matched to your brand standards. Logo integration available "
            "for grand openings, store activations, and corporate receptions."
        ),
    },
    {
        "icon": "balloon-arch",
        "title": "Grand Opening Arches",
        "body": (
            "Classic, photographable entrances for ribbon cuttings, new locations, "
            "and brand activations. Clean install, clean strike."
        ),
    },
    {
        "icon": "balloon-column",
        "title": "Lobby & Stage Columns",
        "body": (
            "Corporate lobbies, conference stages, and event entrances. "
            "Consistent sizing, brand-palette discipline."
        ),
    },
    {
        "icon": "balloon-cluster",
        "title": "Brand-Color Cluster Decor",
        "body": (
            "Organic clusters, bouquet arrangements, and ceiling decor "
            "using exact brand color systems for on-camera events."
        ),
    },
]

# What corporate buyers actually need to know before approving a vendor.
BUYER_NOTES = [
    {
        "heading": "AP-Friendly Invoicing",
        "body": (
            "Invoices issued through ERPNext with line items, service dates, and "
            "event details. Submit for reimbursement or cost-center allocation."
        ),
    },
    {
        "heading": "Brand Color Matching",
        "body": (
            "Submit your brand hex, Pantone, or CMYK. The team selects the "
            "closest available balloon color and sends a pre-event sample on request."
        ),
    },
    {
        "heading": "On-Site Install & Strike",
        "body": (
            "Professional delivery, setup before your event, and full strike at "
            "close. No cleanup left for your team."
        ),
    },
    {
        "heading": "Multi-Location Coordination",
        "body": (
            "Serving the Wasatch Front from Ogden to Provo. "
            "Consistent execution across multiple sites."
        ),
    },
]

# Case story — the narrative proof block.
CASE_STORY = {
    "client": "Weber State University / Corporate Partner Event",
    "context": "Weberstock branded outdoor festival, Ogden campus",
    "challenge": (
        "A large outdoor event requiring a coordinated photo-opportunity installation "
        "and entry arch — both needed to photograph well under full Utah summer sun "
        "and stay anchored for multi-day use."
    ),
    "outcome": (
        "Full branded arch at the event entrance plus a large photo-opt backdrop, "
        "both in event-specified colors. Featured in coverage by broadcast partners "
        "KSL and KUTV."
    ),
}


def get_context(context):
    context.title = "Corporate Events — Locally Twisted"
    context.metatags = {
        "description": (
            "Professional balloon decor for Utah corporate events: grand openings, "
            "brand activations, broadcaster events, and corporate parties. "
            "Clients include Ancestry, Zions Bank, KSL, Utah Jazz, and 30+ more."
        ),
        "og:title": "Corporate Events — Locally Twisted",
        "og:description": (
            "Brand-safe balloon installations for Utah corporate events, "
            "store openings, and media activations. AP-friendly invoicing available."
        ),
        "og:type": "website",
    }
    context.corporate_clients = CORPORATE_CLIENTS
    context.audience_services = AUDIENCE_SERVICES
    context.buyer_notes = BUYER_NOTES
    context.case_story = CASE_STORY
    return context
