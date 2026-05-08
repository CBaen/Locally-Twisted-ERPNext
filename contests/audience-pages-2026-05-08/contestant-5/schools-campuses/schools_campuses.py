"""Controller for /schools-campuses audience landing page.

Schools & Campuses: activity directors, athletic departments, PTAs,
college student life, graduation organizers. Buyer posture: spirit-driven,
schedule-tight, school colors disciplined, family-friendly.
"""

no_cache = 1
sitemap = 1

# Named school and campus clients from the approved roster.
SCHOOL_CLIENTS = [
    {
        "name": "University of Utah",
        "short": "UofU",
        "context": "Campus & athletics events",
    },
    {
        "name": "Weber State University",
        "short": "WSU",
        "context": "Campus events & graduation",
    },
    {
        "name": "St. Joseph's High School",
        "short": "St. Joseph's",
        "context": "School spirit & events",
    },
]

# Installed work proof — photo references for the visual proof section.
PROOF_PHOTOS = [
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "alt": "Large balloon stage display for a school back-to-school event",
        "caption": "Back-to-school stage — school event install",
    },
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/school-grad-garland.webp",
        "alt": "Balloon garland installed for a graduation ceremony",
        "caption": "Graduation garland — commencement decor",
    },
    {
        "path": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "Balloon arch and bouquets at a Weber State University event",
        "caption": "Campus arch with bouquets — Weber State University",
    },
    {
        "path": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Parades/Back to school stage display.png",
        "alt": "Large back-to-school balloon stage backdrop in school colors",
        "caption": "Stage backdrop — school colors install",
    },
]

# Icon proof bar
PROOF_ICONS = [
    {
        "svg": "school-spirit",
        "label": "School Spirit Ready",
        "note": "Color-matched installs for school athletics, graduation, and campus events",
    },
    {
        "svg": "utah-rooted",
        "label": "Utah Campus Experience",
        "note": "Established relationships with University of Utah, Weber State, and Utah high schools",
    },
    {
        "svg": "event-stage",
        "label": "Stage & Assembly Ready",
        "note": "Large-format stage backdrops, graduation arches, and pep rally installs that read from the bleachers",
    },
    {
        "svg": "professional",
        "label": "Schedule Disciplined",
        "note": "School events run on tight windows. Setup is complete before students arrive, teardown before the next class period",
    },
]

# Occasion breakdown for schools
SCHOOL_OCCASIONS = [
    {
        "title": "Graduation & Commencement",
        "body": "Stage garlands, entrance arches, and photo backdrops for indoor and outdoor graduation ceremonies. Color-matched to school palette. Setup before guests arrive.",
    },
    {
        "title": "Back-to-School & Welcome Week",
        "body": "Stage displays, hallway arches, and spirit columns for back-to-school assemblies, orientation days, and first-week campus energy.",
    },
    {
        "title": "Homecoming & Spirit Events",
        "body": "Homecoming arches, pep rally backdrops, and team-color installs for athletic events and spirit week. Outdoor and gym-appropriate options.",
    },
    {
        "title": "Prom & Formal Events",
        "body": "Elegant entrances, photo backdrops, and ceiling decor for prom, semi-formal, and end-of-year events. School color palettes or custom student-selected colors.",
    },
    {
        "title": "PTA & Campus Community Events",
        "body": "Family fun fairs, community fundraisers, teacher appreciation events, and school carnivals. Family-friendly scale and kid-tested durability.",
    },
    {
        "title": "Athletic & Campus Milestones",
        "body": "Championship banners, signing-day celebrations, athletic department installs, and campus milestone recognition events.",
    },
]


def get_context(context):
    context.title = "School & Campus Balloon Decor — Locally Twisted Utah"
    context.metatags = {
        "description": (
            "Balloon decor for Utah schools and campuses. Graduation ceremonies, back-to-school "
            "events, homecoming, prom, and campus spirit events. Serving University of Utah, "
            "Weber State, St. Joseph's High School, and Wasatch Front schools."
        ),
        "og:title": "School & Campus Balloon Decor — Locally Twisted",
        "og:description": (
            "Spirit-driven balloon installations for graduation, back-to-school, homecoming, "
            "and campus events. Named clients include UofU, Weber State, and St. Joseph's High School."
        ),
        "og:type": "website",
    }
    context.school_clients = SCHOOL_CLIENTS
    context.proof_photos = PROOF_PHOTOS
    context.proof_icons = PROOF_ICONS
    context.school_occasions = SCHOOL_OCCASIONS
    return context
