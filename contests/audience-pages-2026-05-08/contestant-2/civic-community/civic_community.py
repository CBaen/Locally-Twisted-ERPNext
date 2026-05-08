"""
Controller for /civic-community — audience page for city events coordinators,
Pride organizers, chambers of commerce, county events teams, and public-facing
community organizations across the Wasatch Front.

Route: /civic-community
"""
import frappe

no_cache = 1
sitemap = 1

# Named civic clients — drawn directly from the approved roster in BRIEF.md.
# Grouped by category for the proof grid on the page.
CIVIC_CLIENTS = {
    "Cities & Counties": [
        "Ogden City", "Sandy City", "Herriman City", "Kearns City",
        "Hooper City", "Syracuse City", "West Point City", "Clinton City",
        "SLC County",
    ],
    "Pride & Equality": [
        "SLC Pride", "Pride Center", "Equality Utah", "LGBT Chamber",
    ],
    "Chambers & Civic Orgs": [
        "Ogden Weber Chamber", "Gallivan Center", "UDOT", "Ogden Airport",
        "Utah Art Alliance",
    ],
    "Community Venues & Events": [
        "Safe Kids Fair", "Tree House Museum", "Western Sports Park",
        "Station Park", "Downtown Daybreak", "Live Daybreak",
        "Shops at Southtown", "Newgate Mall",
    ],
}

# Proof work — story beats for the case-study section.
CIVIC_PROOF_STORIES = [
    {
        "client": "SLC Pride",
        "headline": "The arches the press photographs",
        "body": (
            "When SLC Pride is on the news that night, these are the arches in the frame. "
            "Balloon structures sized for public parade clearance, built to read at distance, "
            "and coordinated with Pride Center and Equality Utah across multiple years. "
            "The work that has to look right when a city puts it on a banner."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp",
        "image_alt": "Rainbow balloon columns installed for a civic Pride event",
    },
    {
        "client": "Gallivan Center",
        "headline": "Public plaza photo moments",
        "body": (
            "Custom photo-op structures scaled for outdoor public plazas. "
            "Engineered to hold form through a full event day — "
            "the kind of installation that keeps working long after the ribbon cutting."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "image_alt": "Large balloon photo moment installed at a public civic plaza event",
    },
    {
        "client": "Ogden City",
        "headline": "Municipal event ready",
        "body": (
            "Parade arches, street-closure installs, and community fair "
            "decor for Ogden City events. Permitted, professional, and built "
            "with the logistics a public works coordinator actually needs."
        ),
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Parades/Standard arch for parade.png",
        "image_alt": "Balloon arch installed along a parade route for a municipal event",
    },
]

# Service notes — the things civic buyers specifically need to know.
CIVIC_SERVICE_NOTES = [
    {
        "icon": "civic-parade",
        "label": "Parade & Street-Closure Installs",
        "detail": "Arches sized for clearance. Coordinated delivery and strike.",
    },
    {
        "icon": "event-stage",
        "label": "Stage & Platform Decor",
        "detail": "Podium backdrops, stage wings, and ribbon-cutting arches.",
    },
    {
        "icon": "professional",
        "label": "Professionally Coordinated",
        "detail": "Invoiced to organizations. COI available on request.",
    },
    {
        "icon": "utah-rooted",
        "label": "Utah Rooted Since 1998",
        "detail": "Two decades of community events across the Wasatch Front.",
    },
]


def get_context(context):
    context.title = "Civic & Community Events — Locally Twisted Balloon Decor"
    context.metatags = {
        "description": (
            "Balloon decor for Utah city events, parades, Pride celebrations, "
            "chambers of commerce, and public community events. "
            "Trusted by SLC Pride, Ogden City, Sandy City, Gallivan Center, and more."
        ),
        "og:title": "Civic & Community Events — Locally Twisted",
        "og:description": (
            "Parade arches, plaza photo moments, and public-event balloon decor "
            "for Utah cities, civic organizations, and community events."
        ),
        "og:type": "website",
    }
    context.civic_clients = CIVIC_CLIENTS
    context.civic_proof_stories = CIVIC_PROOF_STORIES
    context.civic_service_notes = CIVIC_SERVICE_NOTES
    return context
