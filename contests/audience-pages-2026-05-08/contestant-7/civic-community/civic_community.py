"""Controller for /civic-community audience landing page.

Audience: City events coordinators, Pride organizers, chambers, county
events, public-facing community organizations across the Wasatch Front.

Buyer posture: Public-facing, civic-scale, photographable, Utah-proud.
These buyers need to show their community something that reads on a stage
or down a parade route. They want proof of prior municipal relationships,
not a consumer pitch.
"""
import frappe

no_cache = 1
sitemap = 1

# Real civic/community clients — grouped by type so a coordinator scans
# for peer organizations, not just names.
CIVIC_CLIENT_GROUPS = [
    {
        "group": "Cities & Counties",
        "clients": [
            "Ogden City", "Sandy City", "Herriman City", "Kearns City",
            "Hooper City", "Syracuse City", "West Point City", "Clinton City",
            "SLC County",
        ],
    },
    {
        "group": "Pride & Equality",
        "clients": [
            "SLC Pride", "Pride Center", "Equality Utah", "LGBT Chamber",
        ],
    },
    {
        "group": "Chambers & Civic Venues",
        "clients": [
            "Ogden Weber Chamber", "Gallivan Center", "UDOT", "Ogden Airport",
            "Utah Art Alliance",
        ],
    },
    {
        "group": "Community & Family Events",
        "clients": [
            "Safe Kids Fair", "Tree House Museum", "Western Sports Park",
            "Station Park", "Downtown Daybreak", "Live Daybreak",
            "Shops at Southtown", "Newgate Mall",
        ],
    },
]

# Proof installs — specific named civic contexts for the story block.
CIVIC_PROOF_STORIES = [
    {
        "client": "SLC Pride",
        "context": "Parade arches and column runs along the parade route",
        "detail": "Full arch installations sized for street-level photography and television broadcast framing.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp",
        "image_alt": "Rainbow balloon columns installed for the SLC Pride parade route",
        "image_source": "optimized",
    },
    {
        "client": "Gallivan Center",
        "context": "Venue entrance and event stage decor",
        "detail": "Stage and entrance arch work for public events at the downtown Salt Lake City plaza.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "image_alt": "Large balloon arch installed at an outdoor civic venue entrance",
        "image_source": "optimized",
    },
    {
        "client": "Sandy City & Herriman City",
        "context": "Community days, ribbon cuttings, and public celebrations",
        "detail": "Municipal installations delivered on city timelines with public-safety clearance.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/seasonal-easter-rabbit-arch.webp",
        "image_alt": "Balloon arch installed at a community public event",
        "image_source": "optimized",
    },
]

# Capability proof points specific to civic buyers.
CIVIC_CAPABILITIES = [
    {
        "icon": "/assets/locally_twisted/icons/brand/civic-parade.svg",
        "label": "Parade Route Ready",
        "body": "Arches, columns, and float decor sized for street-level clearance and broadcast photography.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/utah-rooted.svg",
        "label": "Utah Rooted",
        "body": "Established relationships with Wasatch Front cities, counties, and chambers of commerce.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/professional.svg",
        "label": "Vendor Credentialed",
        "body": "Available for purchase-order and AP-approved billing. Experienced with municipal procurement.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "Delivered and Struck",
        "body": "Full delivery, setup, and teardown — coordinate directly with venue or event operations.",
    },
]


def get_context(context):
    context.title = "Civic & Community Events — Locally Twisted"
    context.metatags = {
        "description": (
            "Balloon decor for Utah civic events, city celebrations, Pride parades, "
            "chamber events, and community organizations. Serving SLC, Ogden, Sandy, "
            "Herriman, and across the Wasatch Front."
        ),
        "og:title": "Civic & Community Balloon Decor — Locally Twisted",
        "og:description": (
            "Professional balloon installations for Utah city events, parades, "
            "Pride celebrations, and public gatherings. Named relationships with "
            "SLC County, Sandy City, Ogden City, Gallivan Center, and more."
        ),
        "og:type": "website",
    }
    context.civic_client_groups = CIVIC_CLIENT_GROUPS
    context.civic_proof_stories = CIVIC_PROOF_STORIES
    context.civic_capabilities = CIVIC_CAPABILITIES
    return context
