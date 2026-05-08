"""
Controller for /schools-campuses — audience page for activity directors,
athletic departments, PTAs, college student life offices, and graduation organizers.

Route: /schools-campuses
"""
import frappe

no_cache = 1
sitemap = 1

# School and campus clients from the approved roster.
SCHOOL_CLIENTS = [
    {"name": "University of Utah", "abbr": "UofU", "type": "University"},
    {"name": "Weber State University", "abbr": "WSU", "type": "University"},
    {"name": "St. Joseph's High School", "abbr": "St. Joseph's", "type": "High School"},
    {"name": "Tree House Museum", "abbr": "Tree House Museum", "type": "Education / Community"},
    {"name": "Safe Kids Fair", "abbr": "Safe Kids Fair", "type": "Education / Community"},
]

# Three proof-story beats.
SCHOOL_PROOF_STORIES = [
    {
        "client": "Weber State University",
        "context": "WSU Spirit Events",
        "headline": "In school colors, at campus scale",
        "body": (
            "A full balloon arch and bouquet cluster built to WSU's purple and white — "
            "sized for the campus entrance and photographed as part of the university's "
            "event coverage. Locally Twisted matches school colors across latex and foil "
            "so every piece reads right in the school's own media."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "image_alt": "Weber State University balloon arch and bouquets in school colors",
    },
    {
        "client": "Back-to-School Events",
        "context": "Stage & Platform Decor",
        "headline": "The moment the gym becomes a stage",
        "body": (
            "Back-to-school stage builds — column pairs, arch framing, "
            "and photo-moment setups for school assemblies. "
            "Installed before the first bell, cleared before the last one."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "image_alt": "Large balloon stage backdrop for a school back-to-school event",
    },
    {
        "client": "Graduation Season",
        "context": "Grad Garlands & Ceremony Decor",
        "headline": "Graduation: designed to remember",
        "body": (
            "Organic garlands, column pairs, and entrance arches for graduation ceremonies. "
            "The schedule is tight and the photos last forever — "
            "Locally Twisted builds for both."
        ),
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-grad-garland.webp",
        "image_alt": "Graduation organic balloon garland at a school ceremony",
    },
]

# Notes specific to what school/campus buyers need.
# Round 2: tightened detail copy to match the specificity of the pill ledger.
SCHOOL_SERVICE_NOTES = [
    {
        "icon": "school-spirit",
        "label": "School Colors. Exactly.",
        "detail": (
            "University crimson, institutional navy, school gold — sourced to your "
            "school's official palette reference, not the catalog's nearest option. "
            "Latex and foil matched so every piece reads right in your school's own photography."
        ),
    },
    {
        "icon": "event-stage",
        "label": "On Schedule for School Logistics",
        "detail": (
            "Installed before the first student arrives, cleared before the custodians "
            "need the space. Install and strike windows confirmed in writing so your "
            "facilities team knows exactly when we're on-site."
        ),
    },
    {
        "icon": "professional",
        "label": "Family-Friendly and Safe",
        "detail": (
            "Appropriate for all ages, K–12 through university. Professional install "
            "crew — background-checked, uniformed, on time. No unsupervised access "
            "to student spaces."
        ),
    },
    {
        "icon": "delivery-install",
        "label": "Budget-Aware Builds",
        "detail": (
            "School budgets have ceilings. Tell us yours and we'll design to it — "
            "full arch or targeted column pair, the color discipline stays the same "
            "regardless of scale."
        ),
    },
]


def get_context(context):
    context.title = "Schools & Campuses — Locally Twisted Balloon Decor"
    context.metatags = {
        "description": (
            "Balloon decor for school events, graduations, back-to-school, "
            "athletic events, and campus celebrations. Trusted by University of Utah, "
            "Weber State, and St. Joseph's High School."
        ),
        "og:title": "Schools & Campuses — Locally Twisted",
        "og:description": (
            "School-color-matched balloon arches, garlands, and stage decor "
            "for Utah schools and universities."
        ),
        "og:type": "website",
    }
    context.school_clients = SCHOOL_CLIENTS
    context.school_proof_stories = SCHOOL_PROOF_STORIES
    context.school_service_notes = SCHOOL_SERVICE_NOTES
    return context
