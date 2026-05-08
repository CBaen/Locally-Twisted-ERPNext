"""
Schools & Campuses audience landing page — /schools-campuses

Proves LT's school and campus event scope: university events,
high school activities, graduation decor, back-to-school installations,
and athletic department events.
"""
import frappe

no_cache = 1
sitemap = 1

# Curated school/campus client list from the approved roster.
SCHOOL_CLIENTS = [
    {
        "name": "University of Utah",
        "short": "UofU",
        "category": "University",
        "note": "Athletic events and campus celebrations",
    },
    {
        "name": "Weber State University",
        "short": "WSU",
        "category": "University",
        "note": "Weberstock festival + campus installations",
    },
    {
        "name": "St. Joseph's High School",
        "short": "St. Joseph's",
        "category": "High School",
        "note": "School events and spirit decor",
    },
]

# Services most relevant to school/campus buyers.
AUDIENCE_SERVICES = [
    {
        "icon": "school-spirit",
        "title": "School Color Arches",
        "body": (
            "Team colors, school colors, mascot palettes. "
            "Sized for gymnasium entrances, stadium tunnels, and auditorium stages."
        ),
    },
    {
        "icon": "balloon-arch",
        "title": "Graduation Ceremony Decor",
        "body": (
            "Stage arches, column pairs, and garland runs for graduation ceremonies. "
            "Fast install before the event, full strike at close."
        ),
    },
    {
        "icon": "balloon-column",
        "title": "Back-to-School & Spirit Events",
        "body": (
            "Rally setups, pep assembly decor, and orientation event installations "
            "scaled for gymnasium and outdoor quad spaces."
        ),
    },
    {
        "icon": "organic-garland",
        "title": "Hallway & Stage Garlands",
        "body": (
            "School-color garland runs for hallways, cafeteria stages, "
            "and main entrance photo moments."
        ),
    },
]

# What school buyers actually need to know.
BUYER_NOTES = [
    {
        "heading": "School Color Matching",
        "body": (
            "Submit your school's colors and LT matches the closest available "
            "balloon system. We've served Ute crimson, Wildcat purple, and full "
            "school-spirit palettes across the Wasatch Front."
        ),
    },
    {
        "heading": "Schedule-Tight Installs",
        "body": (
            "Schools have tight setup windows between classes, gym schedules, "
            "and event doors. LT coordinates around your schedule and installs "
            "fast without disrupting hallways or common areas."
        ),
    },
    {
        "heading": "Clean Strike After the Event",
        "body": (
            "Full teardown and removal at close. No cleanup left for your "
            "custodial staff, no balloon litter on campus."
        ),
    },
    {
        "heading": "PTA and Activity Budget",
        "body": (
            "Invoicing available for PTA, student life budgets, and activity "
            "accounts. Quote before you commit."
        ),
    },
]

# Case story.
CASE_STORY = {
    "client": "Weber State University",
    "context": "Weberstock outdoor campus festival, Ogden",
    "challenge": (
        "A large outdoor campus festival needing both a branded entrance arch "
        "and a standing photo-opt installation visible to student crowds. "
        "Installation had to survive a full-day Utah outdoor event in summer."
    ),
    "outcome": (
        "Full entry arch and large photo-opt in WSU purple and white, "
        "installed before gates opened and struck after close. "
        "Photographed by students and featured in university social coverage."
    ),
}

# Proof stats.
PROOF_STATS = [
    {"figure": "UofU", "label": "University of Utah"},
    {"figure": "WSU", "label": "Weber State University"},
    {"figure": "Graduation", "label": "ceremony installs"},
    {"figure": "Spirit", "label": "events & rally decor"},
]


def get_context(context):
    context.title = "Schools & Campuses — Locally Twisted"
    context.metatags = {
        "description": (
            "Balloon decor for Utah schools and universities: graduation ceremonies, "
            "spirit events, back-to-school installations, and campus celebrations. "
            "University of Utah, Weber State, and more."
        ),
        "og:title": "Schools & Campuses — Locally Twisted",
        "og:description": (
            "School-color balloon installations for Utah universities and high schools. "
            "Graduation arches, spirit decor, and schedule-tight installs."
        ),
        "og:type": "website",
    }
    context.school_clients = SCHOOL_CLIENTS
    context.audience_services = AUDIENCE_SERVICES
    context.buyer_notes = BUYER_NOTES
    context.case_story = CASE_STORY
    context.proof_stats = PROOF_STATS
    return context
