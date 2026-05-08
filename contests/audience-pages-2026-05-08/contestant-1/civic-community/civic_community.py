"""
Civic & Community audience landing page — /civic-community

Proves LT's civic and community event scope: city governments, Pride
organizations, chambers of commerce, arts organizations, county events,
and public venues along the Wasatch Front.
"""
import frappe

no_cache = 1
sitemap = 1

# Curated civic/community client list from the approved roster.
# Used in the named-client proof grid on the page.
CIVIC_CLIENTS = [
    {"name": "SLC Pride", "category": "Pride & Community"},
    {"name": "Pride Center", "category": "Pride & Community"},
    {"name": "Equality Utah", "category": "Pride & Community"},
    {"name": "LGBT Chamber", "category": "Pride & Community"},
    {"name": "Ogden City", "category": "City Government"},
    {"name": "Sandy City", "category": "City Government"},
    {"name": "Herriman City", "category": "City Government"},
    {"name": "Syracuse City", "category": "City Government"},
    {"name": "West Point City", "category": "City Government"},
    {"name": "Clinton City", "category": "City Government"},
    {"name": "Kearns", "category": "City Government"},
    {"name": "Hooper City", "category": "City Government"},
    {"name": "SLC County", "category": "County & Regional"},
    {"name": "UDOT", "category": "State Agency"},
    {"name": "Ogden Weber Chamber", "category": "Chamber of Commerce"},
    {"name": "Gallivan Center", "category": "Public Venue"},
    {"name": "Ogden Airport", "category": "Public Venue"},
    {"name": "Utah Art Alliance", "category": "Arts & Culture"},
    {"name": "Tree House Museum", "category": "Arts & Culture"},
    {"name": "Western Sports Park", "category": "Recreation"},
    {"name": "Station Park", "category": "Public Venue"},
    {"name": "Downtown Daybreak", "category": "Community Development"},
    {"name": "Live Daybreak", "category": "Community Development"},
    {"name": "Shops at Southtown", "category": "Public Venue"},
    {"name": "Newgate Mall", "category": "Public Venue"},
    {"name": "Safe Kids Fair", "category": "Community Event"},
]

# Proof stats — do not inflate; these reflect provable scope only.
PROOF_STATS = [
    {"figure": "20+", "label": "Utah cities served"},
    {"figure": "10+", "label": "years of civic events"},
    {"figure": "Pride", "label": "Salt Lake City, Ogden & beyond"},
    {"figure": "Wasatch", "label": "Front to back range"},
]

# Case story — the narrative proof block. One real story, documented.
CASE_STORY = {
    "client": "SLC Pride",
    "context": "Utah's largest annual Pride celebration",
    "challenge": (
        "A parade-route arch installation visible from multiple city blocks, "
        "requiring full-day weather durability, crowd-safe anchoring, and "
        "design that photographed equally well from street level and elevated cameras."
    ),
    "outcome": (
        "A full rainbow-spectrum arch across the main celebration entrance, "
        "installed before sunrise and struck after dusk. Photographed by "
        "local press and social media coverage across Utah."
    ),
}

# Services most relevant to civic/community buyers.
AUDIENCE_SERVICES = [
    {
        "icon": "balloon-arch",
        "title": "Parade & Entrance Arches",
        "body": (
            "Engineered for outdoor civic events: weather-tolerant anchoring, "
            "full-day durability, and clean strike afterward."
        ),
    },
    {
        "icon": "balloon-column",
        "title": "Stage & Venue Columns",
        "body": (
            "Paired columns that frame stages, podiums, and civic entrances. "
            "Consistent sizing for professional civic photography."
        ),
    },
    {
        "icon": "organic-garland",
        "title": "Community Celebration Garlands",
        "body": (
            "Full-color garlands for ribbon cuttings, grand openings, "
            "and community gathering spaces."
        ),
    },
    {
        "icon": "balloon-cluster",
        "title": "Color-Matched City & Pride Decor",
        "body": (
            "Color systems designed for civic and Pride color standards, "
            "photographable for press and social coverage."
        ),
    },
]

# Operational buyer notes for civic/government coordinators.
# Mirrors the corporate "buyer notes" pattern: answers the procurement questions
# a Sandy City events coordinator or Pride operations director actually has.
CIVIC_BUYER_NOTES = [
    {
        "heading": "Vendor Documentation",
        "body": (
            "We can provide a W-9, vendor registration form, or Certificate of "
            "Insurance (COI) for city procurement. Ask when you reach out."
        ),
    },
    {
        "heading": "Permit-Friendly Coordination",
        "body": (
            "We work within your event permit timeline — setup windows, strike "
            "deadlines, and public-space restrictions. Tell us the constraints."
        ),
    },
    {
        "heading": "Invoicing for Government Accounts",
        "body": (
            "We invoice on your terms: purchase order reference, net-30, or "
            "department billing. We've worked with city accounts before."
        ),
    },
    {
        "heading": "Multi-Venue or Annual Events",
        "body": (
            "Recurring events — annual Pride, city parades, seasonal festivals — "
            "get consistent specs year over year. We keep the notes."
        ),
    },
]


def get_context(context):
    context.title = "Civic & Community Events — Locally Twisted"
    context.metatags = {
        "description": (
            "Balloon decor and event installations for Utah city governments, "
            "Pride organizations, chambers of commerce, and public community events. "
            "Serving Ogden, Salt Lake, Sandy, and the Wasatch Front."
        ),
        "og:title": "Civic & Community Events — Locally Twisted",
        "og:description": (
            "Professional balloon installations for Utah civic events, Pride celebrations, "
            "and community gatherings. 20+ cities served along the Wasatch Front."
        ),
        "og:type": "website",
    }
    context.civic_clients = CIVIC_CLIENTS
    context.proof_stats = PROOF_STATS
    context.case_story = CASE_STORY
    context.audience_services = AUDIENCE_SERVICES
    return context
