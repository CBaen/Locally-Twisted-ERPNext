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
        "body": "Setup begins after the venue opens for ceremony prep — usually early morning, before families arrive. Garlands, entrance arches, and stage backdrops are positioned and cleared before the venue resets for the next event that day. The color-matching conversation happens at quote time so there are no surprises when materials arrive.",
    },
    {
        "title": "Back-to-School & Welcome Week",
        "body": "The install window is typically 7am or earlier — students arrive, the energy needs to already be there. Stage displays, hallway arches, and spirit columns go up and are cleared before the school day starts. The team knows the window isn't negotiable.",
    },
    {
        "title": "Homecoming & Spirit Events",
        "body": "Between the lunch bell and the pep rally, there isn't much time. Homecoming arches and team-color backdrops are sized and staged ahead of the event window so setup doesn't depend on having a spare hour. Outdoor and gym configurations both available.",
    },
    {
        "title": "Prom & Formal Events",
        "body": "Prom decor is one of the few events where students have strong opinions about the palette — and those opinions matter. Color selections go through student leadership or event committee sign-off before materials are sourced, so the install reflects what was actually approved, not a best guess.",
    },
    {
        "title": "PTA & Campus Community Events",
        "body": "Family fun fairs and school carnivals have kids in the crowd from the first minute. The installs are built for that: anchored, kid-tested for durability, and family-appropriate scale. The same setup timeline discipline applies — the fair is ready when families arrive.",
    },
    {
        "title": "Athletic & Campus Milestones",
        "body": "Signing-day setups, championship recognitions, and athletic department announcements often come together quickly. The team is used to shorter lead times on milestone moments — share the date and the school colors and the quote turnaround matches the timeline.",
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
