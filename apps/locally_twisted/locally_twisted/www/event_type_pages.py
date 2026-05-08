"""Shared content model for Event Balloons audience pages."""

from __future__ import annotations


PAGE_CSS = """
.lt-event-type-page .lt-authority-hero__content {
  max-width: 960px;
}

.lt-event-type-page .lt-authority-hero h1 {
  max-width: 30ch;
}

.lt-event-type-page .lt-authority-proof__inner {
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
}

.lt-event-type-page .lt-authority-card strong {
  color: var(--lt-navy);
  display: block;
  font-weight: 900;
  margin-bottom: 0.25rem;
}

.lt-event-client-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  list-style: none;
  margin: 1.5rem 0 0;
  padding: 0;
}

.lt-event-client-cloud li {
  background: var(--lt-navy);
  border: 1px solid rgba(184, 154, 91, 0.42);
  color: var(--lt-warm-white);
  font: 900 0.82rem/1.15 var(--lt-font-body);
  padding: 0.55rem 0.7rem;
  text-transform: uppercase;
}

.lt-event-type-page .lt-authority-step ul {
  margin: 0.65rem 0 0;
  padding-left: 1.1rem;
}

.lt-event-type-page .lt-authority-section--dark .lt-authority-step h3 {
  color: var(--lt-ink);
}

.lt-event-type-page .lt-authority-section--dark .lt-authority-step p,
.lt-event-type-page .lt-authority-section--dark .lt-authority-step li {
  color: var(--lt-soft-gray);
}

.lt-event-type-page .lt-authority-step li + li {
  margin-top: 0.35rem;
}

@media (max-width: 575.98px) {
  .lt-event-type-page .lt-authority-hero .lt-authority-eyebrow {
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    line-height: 1.2;
  }

  .lt-event-type-page .lt-authority-hero h1 {
    font-size: clamp(1.8rem, 7.2vw, 2rem);
    line-height: 1.03;
  }
}
"""


EVENT_TYPE_PAGES = {
    "civic_community": {
        "route": "civic-community",
        "eyebrow": "Public events",
        "title": "Civic and community balloon decor.",
        "lede": (
            "Public-facing events need decor that looks welcoming, photographs cleanly, "
            "and respects access, timing, traffic, and venue rules."
        ),
        "meta_title": "Civic and Community Balloon Decor in Utah",
        "meta_description": (
            "Balloon arches, garlands, stages, entrances, and public-space decor for Utah "
            "city, county, chamber, Pride, community, and public events."
        ),
        "proof": [
            ("City work", "Ogden City, Sandy City, Herriman City, Syracuse City, West Point City, Clinton City, Hooper City, and Kearns are all named in the site proof crawl."),
            ("County and public agencies", "SLC County and UDOT belong on this lane because public work needs timing, visibility, and clear setup plans."),
            ("Community organizations", "Equality Utah, SLC Pride, Pride Center, LGBT Chamber, Ogden Weber Chamber, Safe Kids Fair, and Utah Art Alliance show the community-event range."),
            ("Public venues", "Gallivan Center, Ogden Airport, Station Park, Newgate Mall, Shops at Southtown, and the Tree House Museum need guest-ready installs."),
        ],
        "clients": [
            "Ogden City", "Sandy City", "Herriman City", "Syracuse City", "West Point City",
            "Clinton City", "Hooper City", "Kearns", "SLC County", "UDOT",
            "Gallivan Center", "Equality Utah", "SLC Pride", "Pride Center",
            "LGBT Chamber", "Ogden Weber Chamber", "Safe Kids Fair", "Utah Art Alliance",
        ],
        "plan_title": "What this lane needs",
        "plan": [
            {
                "title": "Readable from a distance",
                "text": "Arches, columns, and stage frames should guide guests without becoming clutter.",
                "bullets": ["City celebrations", "Ribbon cuttings", "Public fairs", "Community open houses"],
            },
            {
                "title": "Built around access",
                "text": "Public installs need early decisions about load-in, pedestrian flow, wind, and teardown.",
                "bullets": ["Venue access", "Outdoor exposure", "Photo locations", "After-event cleanup"],
            },
            {
                "title": "Friendly without looking casual",
                "text": "The design can feel celebratory while still fitting city, chamber, school, and public-agency settings.",
                "bullets": ["Civic color palettes", "Brand-safe accents", "Family-friendly scale", "Clear quote scope"],
            },
        ],
    },
    "corporate_events": {
        "route": "corporate-events",
        "eyebrow": "Business events",
        "title": "Corporate event balloons.",
        "lede": (
            "Business events need clean entrances, brand-aware color, reliable install timing, "
            "and a quote path that can support invoice and purchasing workflows."
        ),
        "meta_title": "Corporate Event Balloon Decor in Utah",
        "meta_description": (
            "Brand-safe balloon decor for Utah corporate events, launches, receptions, restaurants, "
            "media events, offices, and customer-facing business gatherings."
        ),
        "proof": [
            ("Brand and finance names", "Ancestry, Zions Bank, America First CU, Fidelity, and Morgan Stanley are proof-crawl names that belong with corporate event buyers."),
            ("Media and entertainment", "KSL, KUTV, FOX13, Utah Jazz, FanX, Megaplex, and Museum of Illusion point to high-visibility branded moments."),
            ("Restaurants and retail", "Chick-fil-A, Texas Roadhouse, Applebee's, Chili's, Honey Baked Ham, PotBelly, Station Park, and Shops at Southtown belong on business and retail event pages."),
            ("Employer and auto groups", "Young Automotive and other business names in the crawl need a page that speaks to openings, staff events, and customer activations."),
        ],
        "clients": [
            "Ancestry", "Zions Bank", "America First CU", "Fidelity", "Morgan Stanley",
            "KSL", "KUTV", "FOX13", "Utah Jazz", "FanX", "Megaplex",
            "Chick-fil-A", "Texas Roadhouse", "Applebee's", "Chili's",
            "Honey Baked Ham", "PotBelly", "Young Automotive",
        ],
        "plan_title": "What corporate buyers need",
        "plan": [
            {
                "title": "Brand-safe impact",
                "text": "Use color and scale to support the brand without making the install feel messy or novelty-only.",
                "bullets": ["Logo entrances", "Launch moments", "Ribbon cuttings", "Reception photo points"],
            },
            {
                "title": "Reliable arrival",
                "text": "Corporate installs have schedules, stakeholders, and access rules. The quote should capture those early.",
                "bullets": ["Load-in windows", "Venue contacts", "Invoice needs", "Teardown timing"],
            },
            {
                "title": "Looks good on camera",
                "text": "Media, customer events, and internal celebrations need clean sightlines and intentional photo moments.",
                "bullets": ["Step-and-repeat moments", "Stage accents", "Employee events", "Customer activations"],
            },
        ],
    },
    "schools_campuses": {
        "route": "schools-campuses",
        "eyebrow": "Schools and campuses",
        "title": "School and campus balloon decor.",
        "lede": (
            "School events need clear color, durable scale, quick setup, and designs that work for students, "
            "families, staff, and campus visitors."
        ),
        "meta_title": "School and Campus Balloon Decor in Utah",
        "meta_description": (
            "Balloon decor for Utah schools, colleges, graduations, assemblies, athletics, "
            "back-to-school events, and campus celebration moments."
        ),
        "proof": [
            ("Higher education", "University of Utah and Weber State are named in the homepage proof crawl and belong on the campus lane."),
            ("School communities", "St. Joseph's and school-focused review proof support assemblies, dances, graduations, and family-facing campus events."),
            ("Nearby youth venues", "Tree House Museum, Sea Quest, Safe Kids Fair, and Western Sports Park show family and youth event range."),
            ("Event-day pressure", "Campus installs need clean delivery, school colors, safe placement, and fast teardown around tight schedules."),
        ],
        "clients": [
            "University of Utah", "Weber State", "St. Joseph's", "Tree House Museum",
            "Sea Quest", "Safe Kids Fair", "Western Sports Park", "Utah Jazz",
        ],
        "plan_title": "What schools and campuses need",
        "plan": [
            {
                "title": "School-color clarity",
                "text": "The palette should read instantly in halls, gyms, stages, and outdoor entrances.",
                "bullets": ["Graduations", "Back-to-school", "Spirit weeks", "Athletics"],
            },
            {
                "title": "Fast, contained setup",
                "text": "Install plans need to respect bell schedules, foot traffic, custodial access, and family arrival times.",
                "bullets": ["Gym entrances", "Stage frames", "Photo backdrops", "Pickup timing"],
            },
            {
                "title": "Kid-safe celebration",
                "text": "The design should feel joyful without blocking paths or creating distracting clutter.",
                "bullets": ["Assemblies", "Dances", "Family nights", "Campus open houses"],
            },
        ],
    },
    "private_celebrations": {
        "route": "private-celebrations",
        "eyebrow": "Private celebrations",
        "title": "Private celebration balloons.",
        "lede": (
            "Private events can be personal without feeling thrown together. The right balloon piece gives the room "
            "a finished focal point for birthdays, weddings, memorials, showers, and hosted family events."
        ),
        "meta_title": "Private Celebration Balloon Decor in Utah",
        "meta_description": (
            "Balloon decor for Utah private parties, weddings, birthdays, showers, memorials, venues, "
            "and family celebrations with quote-led design support."
        ),
        "proof": [
            ("Venue and event partners", "Alpine Events, Lux Events, Ogden Country Club, The Boiler Room, Paramount, and Daybreak belong with private and venue-led celebration work."),
            ("Family-facing destinations", "Station Park, Newgate Mall, Shops at Southtown, Sea Quest, and Tree House Museum show public/private celebration overlap."),
            ("Personal review proof", "Reviews mention birthdays, weddings, Mother's Day, memorial stands, neighborhood parties, church picnics, and family events."),
            ("Designed, not generic", "Private work still needs color choices, delivery timing, indoor/outdoor planning, and a clean focal point."),
        ],
        "clients": [
            "Alpine Events", "Lux Events", "Ogden Country Club", "The Boiler Room",
            "Paramount", "Daybreak", "Station Park", "Newgate Mall", "Shops at Southtown",
            "Sea Quest", "Tree House Museum",
        ],
        "plan_title": "What private celebrations need",
        "plan": [
            {
                "title": "A clear photo moment",
                "text": "Private events usually need one strong focal point more than a room full of scattered decor.",
                "bullets": ["Birthday backdrops", "Wedding accents", "Shower entrances", "Memorial stands"],
            },
            {
                "title": "Help choosing scale",
                "text": "The quote path should help decide what fits the room, budget, timeline, and delivery plan.",
                "bullets": ["Home installs", "Venue delivery", "Pickup pieces", "Outdoor conditions"],
            },
            {
                "title": "Personal but polished",
                "text": "Themes, colors, and names can be personal while the final install still feels clean and intentional.",
                "bullets": ["Family milestones", "Holiday moments", "Neighborhood events", "Hosted celebrations"],
            },
        ],
    },
}


def get_event_type_context(context, page_key: str):
    event_page = EVENT_TYPE_PAGES[page_key]
    context.event_page = event_page
    context.title = event_page["meta_title"]
    context.page_css = PAGE_CSS
    context.metatags = {
        "title": event_page["meta_title"],
        "description": event_page["meta_description"],
        "og:title": event_page["meta_title"],
        "og:description": event_page["meta_description"],
        "og:type": "website",
    }
    return context
