"""Controller for /schools-campuses audience landing page.

Serves activity directors, athletic departments, PTAs, college student
life offices, and graduation organizers. Buyer posture: spirit-driven,
schedule-tight, school colors disciplined, family-friendly.
"""
import frappe

no_cache = 1
sitemap = 1

# School client roster — from the approved brief.
# Note: roster is intentionally short; per brief, lean into named
# relationships and named contexts rather than padding.
SCHOOL_CLIENTS = [
    "University of Utah",
    "Weber State University",
    "St. Joseph's High School",
    "Ogden City (school events)",
    "Tree House Museum (education days)",
]

# Context moments — the recurring job types schools hire for.
# Anchored to real photos and named clients where possible.
SCHOOL_MOMENTS = [
    {
        "tag": "Back to School",
        "client": "Weber State University",
        "headline": "Back-to-School Stage Displays",
        "body": (
            "Weber State returns to Locally Twisted year after year for "
            "back-to-school stage displays, welcome arches, and campus "
            "activation decor. School colors, large-format structures, "
            "and coordinated install around move-in and orientation schedules."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "alt": "Large balloon stage display for a back-to-school university event",
    },
    {
        "tag": "Graduation",
        "client": "University of Utah / Weber State",
        "headline": "Graduation Garlands and Ceremony Decor",
        "body": (
            "Commencement ceremonies need decor that photographs well "
            "and lands in thousands of family photos. Graduation garlands, "
            "formal entrance arches, and stage-front decor for university "
            "ceremonies — sized for auditoriums, not classrooms."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-grad-garland.webp",
        "alt": "Graduation balloon garland at a university commencement ceremony",
    },
    {
        "tag": "School Spirit",
        "client": "St. Joseph's High School",
        "headline": "Spirit Events and Athletic Installations",
        "body": (
            "Homecoming, pep rallies, athletic banquets, and game-day "
            "entrances. School colors matched precisely. Locally Twisted "
            "produces spirit decor that students remember — and that "
            "parents photograph."
        ),
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/themed decor/Weber Welcome bouquets.png",
        "alt": "School-color balloon bouquets welcoming students at a spirit event",
    },
]

# Proof pillars.
PROOF_PILLARS = [
    {
        "icon": "/assets/locally_twisted/icons/brand/school-spirit.svg",
        "label": "School Colors",
        "body": "Balloon palettes matched to your school's exact colors. No guessing, no surprises.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/event-stage.svg",
        "label": "Event Ready",
        "body": "Stage displays, entrance arches, and gymnasium installs sized for real venues.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/professional.svg",
        "label": "Schedule-Safe",
        "body": "Coordinated around school calendars, class schedules, and facility access windows.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/trusted-partner.svg",
        "label": "Family-Friendly",
        "body": "Every install is appropriate for student, family, and faculty audiences.",
    },
]

# Gallery — school context images.
GALLERY_IMAGES = [
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "alt": "Back-to-school balloon stage display at Weber State",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/school-grad-garland.webp",
        "alt": "Graduation balloon garland at commencement",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "WSU balloon arch and bouquets at campus event",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Photo opts/Back to school stage display 2.png",
        "alt": "Back-to-school stage balloon display",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Photo opts/Back to school stage display 3.png",
        "alt": "Large school event balloon stage installation",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Grad organic garland.png",
        "alt": "Organic balloon garland for graduation ceremony",
    },
]

# Service types for schools.
SCHOOL_SERVICES = [
    "Graduation Arches & Garlands",
    "Back-to-School Stage Displays",
    "Homecoming & Pep Rally Decor",
    "Athletic Banquet Installations",
    "Game-Day Entrance Arches",
    "Campus Activation Decor",
    "PTA & School Event Installs",
    "Color-Matched School Spirit",
]


def get_context(context):
    context.title = "Schools & Campuses — Locally Twisted"
    context.metatags = {
        "description": (
            "Balloon decor for schools and universities across Utah — "
            "graduation ceremonies, back-to-school events, homecoming, "
            "spirit events, and athletic installs. Trusted by University of "
            "Utah, Weber State University, and St. Joseph's High School."
        ),
        "og:title": "School & Campus Balloon Decor — Locally Twisted",
        "og:description": (
            "Graduation garlands, back-to-school stage displays, and "
            "spirit event decor for Utah schools and universities."
        ),
        "og:type": "website",
    }
    context.school_clients = SCHOOL_CLIENTS
    context.school_moments = SCHOOL_MOMENTS
    context.proof_pillars = PROOF_PILLARS
    context.gallery_images = GALLERY_IMAGES
    context.school_services = SCHOOL_SERVICES
    return context
