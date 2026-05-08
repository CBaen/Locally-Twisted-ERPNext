"""Controller for /civic-community audience landing page.

Civic & Community: city event coordinators, Pride organizers, chambers,
county events, and public-facing community organizations across Utah.
"""

no_cache = 1
sitemap = 1

# Named civic and community clients from the approved roster.
CIVIC_CLIENTS = [
    {"name": "SLC Pride", "category": "Pride & Equality"},
    {"name": "Pride Center", "category": "Pride & Equality"},
    {"name": "Equality Utah", "category": "Pride & Equality"},
    {"name": "LGBT Chamber", "category": "Pride & Equality"},
    {"name": "Ogden City", "category": "Municipal"},
    {"name": "Sandy City", "category": "Municipal"},
    {"name": "Herriman City", "category": "Municipal"},
    {"name": "Kearns", "category": "Municipal"},
    {"name": "Hooper City", "category": "Municipal"},
    {"name": "Syracuse City", "category": "Municipal"},
    {"name": "West Point City", "category": "Municipal"},
    {"name": "Clinton City", "category": "Municipal"},
    {"name": "SLC County", "category": "County & Regional"},
    {"name": "Ogden Weber Chamber", "category": "Chamber & Civic Org"},
    {"name": "Gallivan Center", "category": "Public Venue"},
    {"name": "UDOT", "category": "State Agency"},
    {"name": "Ogden Airport", "category": "Public Infrastructure"},
    {"name": "Utah Art Alliance", "category": "Arts & Culture"},
    {"name": "Safe Kids Fair", "category": "Community Health"},
    {"name": "Tree House Museum", "category": "Family & Community"},
    {"name": "Western Sports Park", "category": "Recreation"},
    {"name": "Station Park", "category": "Public Venue"},
    {"name": "Downtown Daybreak", "category": "Community District"},
    {"name": "Live Daybreak", "category": "Community District"},
    {"name": "Shops at Southtown", "category": "Community Retail"},
    {"name": "Newgate Mall", "category": "Community Retail"},
]

# Installed work proof — photo references for the visual proof section.
PROOF_PHOTOS = [
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp",
        "alt": "Rainbow balloon columns installed at an outdoor Utah Pride event",
        "caption": "Pride columns — outdoor civic install",
    },
    {
        "path": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Pride/20_ progress flag arch.png",
        "alt": "Progress flag balloon arch installed for a Utah Pride parade",
        "caption": "Progress flag arch — parade installation",
    },
    {
        "path": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Pride/Iheart media pride float.png",
        "alt": "Pride float with balloon decor for iHeart Media Utah",
        "caption": "Parade float decor — civic broadcast partner",
    },
    {
        "path": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Parades/Standard arch for parade.png",
        "alt": "Standard balloon arch installed at a Utah community parade",
        "caption": "Community parade arch — civic scale",
    },
]

# Icon proof bar — relevant to civic buyers.
PROOF_ICONS = [
    {
        "svg": "utah-rooted",
        "label": "Utah Rooted",
        "note": "Serving Wasatch Front municipalities since 1998",
    },
    {
        "svg": "civic-parade",
        "label": "Parade & Public Event Ready",
        "note": "Arches, columns, floats, and stage installs for outdoor civic events",
    },
    {
        "svg": "professional",
        "label": "Professional",
        "note": "Insured, punctual, and vendor-ready for public event permit requirements",
    },
    {
        "svg": "trusted-partner",
        "label": "Trusted by Utah Cities",
        "note": "Named clients across 8+ Wasatch Front municipalities",
    },
]


def get_context(context):
    context.title = "Civic & Community Balloon Decor — Locally Twisted Utah"
    context.metatags = {
        "description": (
            "Balloon decor for Utah public events, city celebrations, Pride parades, "
            "chamber events, and community gatherings. Serving municipalities and civic "
            "organizations across the Wasatch Front."
        ),
        "og:title": "Civic & Community Balloon Decor — Locally Twisted",
        "og:description": (
            "Real balloon installations for Utah cities, Pride events, chambers, "
            "and public venues. Named clients include SLC Pride, Sandy City, Ogden City, "
            "Gallivan Center, and more."
        ),
        "og:type": "website",
    }
    context.civic_clients = CIVIC_CLIENTS
    context.proof_photos = PROOF_PHOTOS
    context.proof_icons = PROOF_ICONS
    return context
