"""Controller for /civic-community audience landing page.

Serves city events coordinators, Pride organizers, chambers,
county events, and public-facing community organizations across
the Wasatch Front. Proof is built from LT's real civic client roster.
"""
import frappe

no_cache = 1
sitemap = 1

# Civic client roster — pulled from the approved brief.
CIVIC_CLIENTS = [
    "SLC Pride", "Pride Center", "Equality Utah", "LGBT Chamber",
    "Ogden City", "Sandy City", "Herriman City", "Kearns City",
    "Hooper City", "Syracuse City", "West Point City", "Clinton City",
    "SLC County", "Ogden Weber Chamber", "Gallivan Center", "UDOT",
    "Ogden Airport", "Utah Art Alliance", "Safe Kids Fair",
    "Tree House Museum", "Western Sports Park", "Station Park",
    "Downtown Daybreak", "Live Daybreak", "Shops at Southtown",
    "Newgate Mall",
]

# Case studies — named moments that illustrate scale and civic fit.
CASE_STUDIES = [
    {
        "client": "SLC Pride",
        "headline": "Pride on the Wasatch Front",
        "body": (
            "From rainbow columns lining the parade route to a 20-foot "
            "Progress Flag arch at the festival entrance, Locally Twisted "
            "has been the decor team behind SLC Pride's public installations "
            "for multiple years running. Coordinated install windows, "
            "weather-aware rigging, and on-site strike."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp",
        "alt": "Rainbow balloon columns installed along a Pride parade route in Salt Lake City",
        "tag": "Pride & Community",
    },
    {
        "client": "Ogden City / Gallivan Center",
        "headline": "Civic Entrances, Parade Arches, Public Stages",
        "body": (
            "City events need decor that reads at street scale. "
            "Locally Twisted has produced parade arches, festival entrances, "
            "and public-stage backdrops for Ogden City, Sandy City, "
            "SLC County, and the Gallivan Center — all coordinated around "
            "city event schedules and public-access requirements."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/seasonal-easter-rabbit-arch.webp",
        "alt": "Large balloon arch installed at a public civic event entrance",
        "tag": "City Events",
    },
    {
        "client": "Utah Art Alliance / Station Park / Daybreak",
        "headline": "Community Districts and Retail Venues",
        "body": (
            "Station Park, Downtown Daybreak, and the Utah Art Alliance "
            "use Locally Twisted for seasonal activations, grand openings, "
            "and community celebration moments that need a professional "
            "install without the event-production overhead."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "alt": "Large-scale balloon display at a community retail event",
        "tag": "Community & Retail",
    },
]

# Proof icons — from the approved brand suite.
PROOF_PILLARS = [
    {
        "icon": "/assets/locally_twisted/icons/brand/civic-parade.svg",
        "label": "Civic Scale",
        "body": "Parade arches, festival entrances, and public-stage installs across Utah municipalities.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/utah-rooted.svg",
        "label": "Utah Rooted",
        "body": "Based on the Wasatch Front. Jeff's team shows up, sets up, and strikes cleanly — on city time.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/professional.svg",
        "label": "Professional",
        "body": "Insurance documentation available. Coordinated with city event managers and venue staff.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "Delivered Cleanly",
        "body": "On-time delivery, full setup, and post-event strike. No vendor overhead left behind.",
    },
]

# Gallery — optimized images relevant to civic context.
GALLERY_IMAGES = [
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp",
        "alt": "Rainbow balloon columns at SLC Pride",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/seasonal-easter-rabbit-arch.webp",
        "alt": "Balloon arch at a public civic event",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "alt": "Large balloon installation at a community event",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Progress Flag backdrop.png",
        "alt": "Progress Pride flag balloon backdrop",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Parades/Rainbow heart parade.png",
        "alt": "Rainbow heart balloon installation in a parade",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Standard arch for parade.png",
        "alt": "Standard balloon arch for a public parade",
    },
]


def get_context(context):
    context.title = "Civic & Community Events — Locally Twisted"
    context.metatags = {
        "description": (
            "Professional balloon decor for city events, Pride celebrations, "
            "public festivals, parades, and community organizations across the "
            "Wasatch Front. Trusted by SLC Pride, Ogden City, Sandy City, "
            "SLC County, and 20+ Utah civic clients."
        ),
        "og:title": "Civic & Community Balloon Decor — Locally Twisted",
        "og:description": (
            "Utah's civic balloon decor team. Parade arches, festival entrances, "
            "and public-stage installs for city events, Pride, and community orgs."
        ),
        "og:type": "website",
    }
    context.civic_clients = CIVIC_CLIENTS
    context.case_studies = CASE_STUDIES
    context.proof_pillars = PROOF_PILLARS
    context.gallery_images = GALLERY_IMAGES
    return context
