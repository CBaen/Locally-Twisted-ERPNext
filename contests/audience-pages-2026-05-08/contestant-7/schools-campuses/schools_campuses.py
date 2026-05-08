"""Controller for /schools-campuses audience landing page.

Audience: Activity directors, athletic departments, PTAs, college student
life, graduation organizers across Utah schools and campuses.

Buyer posture: Spirit-driven, schedule-tight, school colors disciplined,
family-friendly. These buyers are typically planning around the academic
calendar — back-to-school, homecoming, graduation, spirit week, and
major campus events. They have color systems (school colors), institutional
procurement rules, and a community audience that includes students, parents,
and faculty.
"""
import frappe

no_cache = 1
sitemap = 1

# Real school/campus clients from the approved roster.
SCHOOL_CLIENTS = [
    "University of Utah",
    "Weber State University",
    "St. Joseph's High School",
]

# Academic calendar moments with LT context.
SCHOOL_MOMENTS = [
    {
        "moment": "Graduation",
        "heading": "Garland and arch installations for commencement",
        "body": "Ceremony-appropriate balloon garlands and stage arches in school colors. Scale and installation timed to venue walk-through schedules.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/school-grad-garland.webp",
        "image_alt": "Balloon garland installation at a school graduation ceremony stage",
    },
    {
        "moment": "Back-to-School",
        "heading": "Stage backdrops for welcome events and assemblies",
        "body": "Large-format stage balloon installations for back-to-school nights, orientation assemblies, and welcome-week events.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "image_alt": "Large balloon backdrop installed at a school back-to-school stage event",
    },
    {
        "moment": "Campus Events",
        "heading": "Arch and bouquet installs for campus-wide programming",
        "body": "University and high school event decor with institutional color matching — Weber State, University of Utah, and St. Joseph's.",
        "image_path": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "image_alt": "Weber State University balloon arch and bouquet installation on campus",
    },
]

# Capability pillars for school buyers.
SCHOOL_CAPABILITIES = [
    {
        "icon": "/assets/locally_twisted/icons/brand/school-spirit.svg",
        "label": "School Color Match",
        "body": "Balloon palettes matched to your school's official colors — not generic colors, yours.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/event-stage.svg",
        "label": "Ceremony Timing",
        "body": "Installation timed to venue setup windows, including early-morning delivery before student arrival.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/professional.svg",
        "label": "Family Appropriate",
        "body": "All decor suitable for student, parent, and faculty audiences. No surprises for administrators.",
    },
    {
        "icon": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "Clean Strike",
        "body": "Teardown included. Venue returned to original condition before the next school day.",
    },
]


def get_context(context):
    context.title = "Schools & Campuses — Locally Twisted"
    context.metatags = {
        "description": (
            "Balloon decor for Utah schools, universities, and campuses. "
            "Graduation arches, back-to-school stages, homecoming, spirit events, "
            "and campus-wide installations in your school colors."
        ),
        "og:title": "School & Campus Balloon Decor — Locally Twisted",
        "og:description": (
            "Custom balloon installations for Utah school and campus events. "
            "School color matching, graduation-ready arches, and family-appropriate decor."
        ),
        "og:type": "website",
    }
    context.school_clients = SCHOOL_CLIENTS
    context.school_moments = SCHOOL_MOMENTS
    context.school_capabilities = SCHOOL_CAPABILITIES
    return context
