"""Shared content model for Event Balloons audience pages."""

from __future__ import annotations


PAGE_CSS = """
.lt-event-type-page {
  --lt-audience-gap: clamp(1rem, 2.5vw, 1.75rem);
}

.lt-event-type-page .lt-authority-hero__content {
  max-width: 900px;
}

.lt-event-type-page .lt-authority-hero h1 {
  max-width: 28ch;
}

.lt-event-type-page .lt-authority-actions {
  flex-wrap: wrap;
}

.lt-event-type-page .lt-authority-proof__inner {
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
}

.lt-event-type-page .lt-authority-proof__text {
  max-width: 34ch;
}

.lt-audience-section {
  background: var(--lt-warm-white);
  padding: clamp(2.75rem, 7vw, 5rem) 1rem;
}

.lt-audience-section--stone {
  background:
    linear-gradient(135deg, rgba(250, 247, 242, 0.96), rgba(231, 229, 225, 0.72));
}

.lt-audience-section__inner {
  box-sizing: border-box;
  width: min(100%, 1160px);
  margin: 0 auto;
}

.lt-audience-section__heading {
  max-width: 760px;
  margin-bottom: 1.6rem;
}

.lt-audience-section__heading h2 {
  margin: 0;
  color: var(--lt-ink);
  font-family: var(--lt-font-heading);
  font-size: clamp(2rem, 5vw, 3.4rem);
  line-height: 1.02;
}

.lt-audience-section__lede {
  max-width: 720px;
  margin: 0.85rem 0 0;
  color: var(--lt-soft-gray);
  font-family: var(--lt-font-body);
  font-size: 1rem;
  line-height: 1.65;
}

.lt-audience-proof-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--lt-audience-gap);
}

@media (min-width: 760px) {
  .lt-audience-proof-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.lt-audience-proof-card,
.lt-audience-story,
.lt-audience-plan-card {
  box-sizing: border-box;
  min-width: 0;
  border: 1px solid rgba(14, 34, 64, 0.14);
  border-radius: 4px;
  background: #fff;
  box-shadow: 0 16px 34px rgba(10, 10, 11, 0.06);
}

.lt-audience-proof-card {
  padding: clamp(1rem, 3vw, 1.45rem);
  border-top: 4px solid var(--lt-brass);
}

.lt-audience-proof-card h3,
.lt-audience-story h3,
.lt-audience-plan-card h3 {
  margin: 0;
  color: var(--lt-ink);
  font-family: var(--lt-font-heading);
  font-size: clamp(1.35rem, 3vw, 1.9rem);
  line-height: 1.08;
}

.lt-audience-proof-card p,
.lt-audience-story p,
.lt-audience-plan-card p {
  color: var(--lt-soft-gray);
  font-family: var(--lt-font-body);
  font-size: 0.97rem;
  line-height: 1.58;
}

.lt-audience-client-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  list-style: none;
  margin: 1rem 0 0;
  padding: 0;
}

.lt-audience-client-list li {
  background: rgba(14, 34, 64, 0.06);
  border: 1px solid rgba(14, 34, 64, 0.12);
  color: var(--lt-navy);
  font: 900 0.76rem/1.2 var(--lt-font-body);
  padding: 0.45rem 0.6rem;
  text-transform: uppercase;
}

.lt-audience-story-grid,
.lt-audience-plan-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--lt-audience-gap);
}

@media (min-width: 900px) {
  .lt-audience-story-grid,
  .lt-audience-plan-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.lt-audience-story {
  overflow: hidden;
}

.lt-audience-story img {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  background: var(--lt-stone);
}

.lt-audience-story__body {
  padding: clamp(1rem, 3vw, 1.35rem);
}

.lt-audience-kicker {
  margin: 0 0 0.55rem;
  color: var(--lt-crimson);
  font-family: var(--lt-font-body);
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.2;
  text-transform: uppercase;
}

.lt-audience-plan-card {
  padding: clamp(1rem, 3vw, 1.35rem);
}

.lt-audience-plan-card ul {
  display: grid;
  gap: 0.45rem;
  margin: 0.8rem 0 0;
  padding-left: 1.1rem;
}

.lt-audience-plan-card li {
  color: var(--lt-soft-gray);
  font-family: var(--lt-font-body);
  font-size: 0.94rem;
  line-height: 1.45;
}

.lt-audience-cta {
  background:
    linear-gradient(135deg, rgba(14, 34, 64, 0.96), rgba(10, 10, 11, 0.96));
  border-top: 1px solid rgba(184, 154, 91, 0.48);
  padding: clamp(2.75rem, 7vw, 4.5rem) 1rem;
}

.lt-audience-cta__inner {
  box-sizing: border-box;
  width: min(100%, 860px);
  margin: 0 auto;
  text-align: center;
}

.lt-audience-cta h2 {
  margin: 0;
  color: var(--lt-warm-white);
  font-family: var(--lt-font-heading);
  font-size: clamp(2rem, 5vw, 3.35rem);
  line-height: 1.02;
}

.lt-audience-cta p {
  max-width: 640px;
  margin: 0.85rem auto 0;
  color: rgba(250, 247, 242, 0.86);
  font-family: var(--lt-font-body);
  font-size: 1rem;
  line-height: 1.6;
}

.lt-audience-cta .lt-authority-actions {
  justify-content: center;
  margin-top: 1.35rem;
}


.lt-event-type-page .lt-authority-hero__inner {
  display: block;
  min-height: 0;
  padding-block: 0;
}

.lt-audience-gallery {
  background: #fff;
  padding: clamp(2.75rem, 7vw, 5rem) 1rem;
}

.lt-audience-gallery__inner {
  box-sizing: border-box;
  width: min(100%, 1160px);
  margin: 0 auto;
}

.lt-audience-gallery__heading {
  max-width: 760px;
  margin-bottom: 1.5rem;
}

.lt-audience-gallery__heading h2 {
  margin: 0;
  color: var(--lt-ink);
  font-family: var(--lt-font-heading);
  font-size: clamp(2rem, 5vw, 3.4rem);
  line-height: 1.02;
}

.lt-audience-gallery__heading p {
  max-width: 680px;
  margin: 0.85rem 0 0;
  color: var(--lt-soft-gray);
  font: 1rem/1.65 var(--lt-font-body);
}

.lt-audience-gallery__grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: clamp(0.75rem, 2vw, 1.2rem);
}

.lt-audience-gallery__item {
  grid-column: span 4;
  overflow: hidden;
  margin: 0;
  border: 1px solid rgba(14, 34, 64, 0.14);
  border-radius: 4px;
  background: var(--lt-warm-white);
  box-shadow: 0 16px 36px rgba(10, 10, 11, 0.07);
}

.lt-audience-gallery__item--wide {
  grid-column: span 6;
}

.lt-audience-gallery__item img {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  background: var(--lt-stone);
}

.lt-audience-gallery__item--wide img {
  aspect-ratio: 16 / 10;
}

.lt-audience-gallery__caption {
  padding: 0.9rem 1rem 1rem;
}

.lt-audience-gallery__caption strong {
  display: block;
  color: var(--lt-ink);
  font-family: var(--lt-font-heading);
  font-size: 1.25rem;
  line-height: 1.05;
}

.lt-audience-gallery__caption span {
  display: block;
  margin-top: 0.35rem;
  color: var(--lt-soft-gray);
  font: 0.92rem/1.45 var(--lt-font-body);
}

@media (max-width: 899.98px) {
  .lt-audience-gallery__item,
  .lt-audience-gallery__item--wide {
    grid-column: span 6;
  }
}

@media (max-width: 575.98px) {
  .lt-audience-gallery__grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .lt-audience-gallery__item,
  .lt-audience-gallery__item--wide {
    grid-column: auto;
  }
}

@media (max-width: 575.98px) {
  .lt-event-type-page .lt-authority-hero .lt-authority-eyebrow {
    font-size: 0.72rem;
    letter-spacing: 0;
    line-height: 1.2;
  }

  .lt-event-type-page .lt-authority-hero h1 {
    font-size: clamp(1.75rem, 7vw, 2rem);
    line-height: 1.03;
  }

  .lt-event-type-page .lt-authority-hero__lede {
    font-size: 0.9rem;
    line-height: 1.32;
  }

  .lt-event-type-page .lt-authority-hero .lt-authority-actions {
    gap: 0.5rem;
    margin-top: 0.6rem;
  }

  .lt-event-type-page .lt-authority-hero .lt-authority-button {
    flex: 0 1 auto;
    min-height: 44px;
    padding-inline: 0.8rem;
  }

  .lt-event-type-page .lt-authority-hero .lt-authority-button--secondary {
    display: none;
  }
}
"""


PORTFOLIO_BASE = "/assets/locally_twisted/images/portfolio/optimized"


EVENT_TYPE_PAGES = {
    "civic_community": {
        "route": "civic-community",
        "root_class": "lt-page-civic",
        "eyebrow": "Civic and community events",
        "title": "Balloon decor for Utah public events.",
        "lede": (
            "Parade arches, civic plaza moments, Pride installations, and community decor "
            "need to read clearly in public, photograph well, and respect the event plan."
        ),
        "meta_title": "Civic and Community Balloon Decor in Utah",
        "meta_description": (
            "Quote-led balloon decor for Utah city, county, chamber, Pride, community, "
            "and public-facing events."
        ),
        "quote_href": "/contact?intent=quote&source=civic-community",
        "support_href": "/portfolio?event=civic",
        "support_label": "See Civic Work",
        "proof": [
            ("Public-facing scale", "Entrances, columns, arches, and stage moments should guide guests and hold up in photographs."),
            ("Local event context", "City, county, chamber, Pride, venue, and public-space work needs practical access and timing details up front."),
            ("Friendly, not casual", "The room can feel welcoming while still fitting official programs, public venues, and sponsor-facing events."),
            ("Quote-led planning", "The right next step is the inquiry form, where date, venue, access, audience, and scale can be shaped together."),
        ],
        "client_groups": [
            ("Cities and counties", ["Ogden City", "Sandy City", "Herriman City", "Syracuse City", "SLC County", "UDOT"]),
            ("Community organizations", ["Equality Utah", "SLC Pride", "Pride Center", "LGBT Chamber", "Ogden Weber Chamber"]),
            ("Public venues and events", ["Gallivan Center", "Ogden Airport", "Station Park", "Tree House Museum", "Safe Kids Fair"]),
        ],
        "stories_heading": "Public work needs a public-ready plan.",
        "stories_lede": (
            "Public event decor works best when guest flow, photo points, scale, and setup conditions are planned together."
        ),
        "stories": [
            {
                "kicker": "Civic photo moments",
                "title": "Color that reads in a crowd",
                "body": "Columns, arches, and backdrops give public events a clear point of arrival without turning the space into clutter.",
                "image": f"{PORTFOLIO_BASE}/seasonal-pride-columns.webp",
                "alt": "Rainbow balloon columns at a public community event",
            },
            {
                "kicker": "Community scale",
                "title": "Large enough for outdoor attention",
                "body": "Public-facing work needs scale, sightlines, and install choices that make sense for shared spaces and visitor traffic.",
                "image": f"{PORTFOLIO_BASE}/corporate-weberstock-photo-opt.webp",
                "alt": "Large balloon photo backdrop at a Utah community event",
            },
            {
                "kicker": "Seasonal gatherings",
                "title": "Family-friendly without looking temporary",
                "body": "Community and seasonal installs can feel warm and accessible while still looking planned, balanced, and finished.",
                "image": f"{PORTFOLIO_BASE}/seasonal-easter-rabbit-arch.webp",
                "alt": "Seasonal balloon arch with public-event styling",
            },
        ],
        "gallery_heading": "Inspiration from real public work.",
        "gallery_lede": "Customers need to see the kind of scale and color Locally Twisted can bring to a civic or community space.",
        "gallery": [
            {"title": "Rainbow civic columns", "caption": "Color that can anchor an entrance or community photo point.", "image": f"{PORTFOLIO_BASE}/seasonal-pride-columns.webp", "alt": "Rainbow balloon columns at a public community event", "wide": True},
            {"title": "Festival-scale backdrop", "caption": "A larger installation built to read in photos and crowds.", "image": f"{PORTFOLIO_BASE}/corporate-weberstock-photo-opt.webp", "alt": "Large balloon backdrop at a Utah festival event", "wide": True},
            {"title": "Seasonal public arch", "caption": "Friendly seasonal decor that still feels planned and finished.", "image": f"{PORTFOLIO_BASE}/seasonal-easter-rabbit-arch.webp", "alt": "Seasonal Easter balloon arch for a public event", "wide": False},
        ],
        "plan_title": "What civic coordinators need to settle early",
        "plan": [
            {
                "title": "Access and timing",
                "text": "Share the venue, load-in window, public access constraints, and strike expectations before design decisions harden.",
                "bullets": ["Public spaces", "Street or plaza events", "Venue contacts", "Teardown windows"],
            },
            {
                "title": "Visibility and guest flow",
                "text": "The piece should help orient guests, frame photos, and keep paths clear.",
                "bullets": ["Entrances", "Stage edges", "Photo points", "Sponsor-safe placement"],
            },
            {
                "title": "Weather and placement",
                "text": "Outdoor installs need practical decisions about sun, wind, shade, anchoring, and backup placement.",
                "bullets": ["Outdoor exposure", "Shade needs", "Surface type", "Indoor fallback"],
            },
        ],
        "cta_title": "Planning a public event?",
        "cta_body": "Send the date, location, audience, and rough install goal. Locally Twisted will help shape a quote path from there.",
    },
    "corporate_events": {
        "route": "corporate-events",
        "root_class": "lt-page-corporate",
        "eyebrow": "Corporate events",
        "title": "On-brand balloon decor for Utah company events.",
        "lede": (
            "Grand openings, brand activations, receptions, and company celebrations need clean color, "
            "reliable timing, and a quote path that supports a professional event plan."
        ),
        "meta_title": "Corporate Event Balloon Decor in Utah",
        "meta_description": (
            "Quote-led balloon decor for Utah corporate events, launches, receptions, restaurants, "
            "media events, offices, and customer-facing business gatherings."
        ),
        "quote_href": "/contact?intent=quote&source=corporate-events",
        "support_href": "/portfolio?event=corporate",
        "support_label": "See Corporate Work",
        "proof": [
            ("Brand-aware color", "The install should support the brand palette without looking like generic party decor."),
            ("Schedule discipline", "Corporate events have doors-open moments, stakeholder timing, vendor access, and teardown windows."),
            ("Camera-ready finish", "Broadcast, launch, ribbon-cutting, and employee-event moments need clean sightlines."),
            ("Purchase-path ready", "The quote should give enough scope detail for budget, approval, and internal routing."),
        ],
        "client_groups": [
            ("Business and finance", ["Ancestry", "Zions Bank", "America First CU", "Fidelity", "Morgan Stanley"]),
            ("Media and entertainment", ["KSL", "KUTV", "FOX13", "Utah Jazz", "FanX", "Megaplex"]),
            ("Restaurant and retail", ["Chick-fil-A", "Texas Roadhouse", "Applebee's", "Chili's", "Station Park"]),
        ],
        "stories_heading": "Built for professional rooms.",
        "stories_lede": (
            "Company events need decor that looks intentional in person, photographs cleanly, and fits the event schedule."
        ),
        "stories": [
            {
                "kicker": "Brand entrances",
                "title": "A finished arrival point",
                "body": "Logo arches and branded entrances help guests find the moment while keeping the event polished and on-color.",
                "image": f"{PORTFOLIO_BASE}/corporate-logo-arch.webp",
                "alt": "Corporate logo balloon arch at a Utah event entrance",
            },
            {
                "kicker": "High-visibility events",
                "title": "Photo backdrops that stay professional",
                "body": "Corporate and media-facing events need decor that photographs cleanly and does not fight the venue or brand.",
                "image": f"{PORTFOLIO_BASE}/corporate-weberstock-photo-opt.webp",
                "alt": "Corporate balloon photo backdrop at a Utah business event",
            },
            {
                "kicker": "Campus and company events",
                "title": "Color matched to the room",
                "body": "Corporate, school, and institutional events often need color discipline, quick setup, and balanced scale.",
                "image": f"{PORTFOLIO_BASE}/corporate-wsu-arch-bouquets.webp",
                "alt": "Purple and white corporate balloon arch and bouquet install",
            },
        ],
        "gallery_heading": "Inspiration for company rooms and entrances.",
        "gallery_lede": "Corporate buyers want to know the decor can look polished on camera, on brand, and finished when doors open.",
        "gallery": [
            {"title": "Branded entrance arch", "caption": "A clear arrival moment for guests, photos, and launches.", "image": f"{PORTFOLIO_BASE}/corporate-logo-arch.webp", "alt": "Corporate logo balloon arch at an event entrance", "wide": True},
            {"title": "Large photo backdrop", "caption": "Scale and color for media, reception, and sponsor-facing moments.", "image": f"{PORTFOLIO_BASE}/corporate-weberstock-photo-opt.webp", "alt": "Corporate balloon photo backdrop at a Utah event", "wide": True},
            {"title": "Campus-color install", "caption": "Color discipline for institutions, companies, and university events.", "image": f"{PORTFOLIO_BASE}/corporate-wsu-arch-bouquets.webp", "alt": "Purple and white balloon arch and bouquet install", "wide": False},
        ],
        "plan_title": "What corporate buyers need to settle early",
        "plan": [
            {
                "title": "Brand and color",
                "text": "Share brand colors, sponsor constraints, logo needs, and the visual role of the install.",
                "bullets": ["Grand openings", "Logo arches", "Launches", "Reception photos"],
            },
            {
                "title": "Venue schedule",
                "text": "Confirm access, doors-open time, teardown rules, and who approves the final placement.",
                "bullets": ["Load-in windows", "Venue contacts", "Stakeholder timing", "Strike timing"],
            },
            {
                "title": "Quote clarity",
                "text": "The inquiry should capture enough scope for approval without pretending the event is a preset package.",
                "bullets": ["Budget routing", "Install scope", "Delivery details", "Decision timeline"],
            },
        ],
        "cta_title": "Tell us what the event needs.",
        "cta_body": "Send the date, venue, brand colors, and rough install goal. The next step is a quote, not an online purchase.",
    },
    "schools_campuses": {
        "route": "schools-campuses",
        "root_class": "lt-page-school",
        "eyebrow": "Schools and campuses",
        "title": "School-color balloon decor for campus moments.",
        "lede": (
            "Graduations, assemblies, athletics, dances, and back-to-school events need color clarity, "
            "fast setup, and placement that works for students, families, staff, and visitors."
        ),
        "meta_title": "School and Campus Balloon Decor in Utah",
        "meta_description": (
            "Quote-led balloon decor for Utah schools, colleges, graduations, assemblies, athletics, "
            "back-to-school events, and campus celebrations."
        ),
        "quote_href": "/contact?intent=quote&source=schools-campuses",
        "support_href": "/portfolio?event=school",
        "support_label": "See School Work",
        "proof": [
            ("School-color clarity", "Decor should read instantly in gyms, commons areas, stages, entrances, and outdoor arrival points."),
            ("Schedule-aware setup", "School events have bell schedules, family arrival times, custodial access, and tight teardown windows."),
            ("Joyful but contained", "Campus decor can feel celebratory while still looking polished for students, families, and staff."),
            ("Quote-led support", "The safest path is to collect date, campus location, colors, and setup constraints through the inquiry form."),
        ],
        "client_groups": [
            ("Higher education", ["University of Utah", "Weber State"]),
            ("School communities", ["St. Joseph's", "Back-to-school events", "Graduation moments"]),
            ("Family and youth venues", ["Tree House Museum", "Sea Quest", "Safe Kids Fair", "Western Sports Park"]),
        ],
        "stories_heading": "Campus work has its own timing.",
        "stories_lede": "School events need color, timing, access, and placement decisions before the right piece can be quoted.",
        "stories": [
            {
                "kicker": "Back-to-school",
                "title": "A first-day photo point",
                "body": "Campus entrances and stage moments need to welcome families while staying clear of traffic and schedules.",
                "image": f"{PORTFOLIO_BASE}/school-back-to-school-stage.webp",
                "alt": "School stage balloon display for a back-to-school event",
            },
            {
                "kicker": "Graduations",
                "title": "Color that carries the ceremony",
                "body": "Graduation and recognition events need school color, clear sightlines, and enough scale to frame the milestone.",
                "image": f"{PORTFOLIO_BASE}/school-grad-garland.webp",
                "alt": "School graduation balloon garland in school colors",
            },
            {
                "kicker": "Spirit events",
                "title": "Built for families and students",
                "body": "Assemblies, athletics, and family nights need polished energy without blocking movement or becoming clutter.",
                "image": f"{PORTFOLIO_BASE}/corporate-wsu-arch-bouquets.webp",
                "alt": "Purple and white balloon install suitable for campus events",
            },
        ],
        "gallery_heading": "Inspiration for school-color moments.",
        "gallery_lede": "School and campus buyers need to see ceremony scale, family photo energy, and school-spirit color before they ask for a quote.",
        "gallery": [
            {"title": "Graduation garland", "caption": "School colors framing a milestone without crowding the ceremony.", "image": f"{PORTFOLIO_BASE}/school-grad-garland.webp", "alt": "School graduation balloon garland in school colors", "wide": True},
            {"title": "Back-to-school stage", "caption": "A cheerful focal point for assemblies, photos, and family arrival.", "image": f"{PORTFOLIO_BASE}/school-back-to-school-stage.webp", "alt": "School stage balloon display for a back-to-school event", "wide": True},
            {"title": "University color palette", "caption": "Polished campus color that can work for athletics, welcome events, or recognition days.", "image": f"{PORTFOLIO_BASE}/corporate-wsu-arch-bouquets.webp", "alt": "Purple and white university balloon install", "wide": False},
        ],
        "plan_title": "What schools need to settle early",
        "plan": [
            {
                "title": "Colors and location",
                "text": "Start with school colors, mascot constraints, where the piece sits, and who needs to approve placement.",
                "bullets": ["Gyms", "Stages", "Entrances", "Commons areas"],
            },
            {
                "title": "Arrival and teardown",
                "text": "Campus work needs timing around families, students, custodial teams, and locked spaces.",
                "bullets": ["Bell schedules", "Ceremony times", "After-hours access", "Cleanup windows"],
            },
            {
                "title": "Audience fit",
                "text": "The same piece may need to work for students, parents, administrators, and photos.",
                "bullets": ["Graduations", "Assemblies", "Athletics", "Family nights"],
            },
        ],
        "cta_title": "Planning a school or campus event?",
        "cta_body": "Send the event date, campus location, colors, and setup window. The quote can be shaped from there.",
    },
    "private_celebrations": {
        "route": "private-celebrations",
        "root_class": "lt-page-private",
        "eyebrow": "Private celebrations",
        "title": "Polished balloons for personal celebrations.",
        "lede": (
            "Birthdays, weddings, showers, memorials, and hosted family events often need one finished focal point "
            "that feels personal without looking improvised."
        ),
        "meta_title": "Private Celebration Balloon Decor in Utah",
        "meta_description": (
            "Quote-led balloon decor for Utah birthdays, weddings, showers, memorials, hosted home events, "
            "venues, and family celebrations."
        ),
        "quote_href": "/contact?intent=quote&source=private-celebrations",
        "support_href": "/portfolio?event=private",
        "support_label": "See Celebration Work",
        "proof": [
            ("Personal scale", "Private events usually need a strong photo moment or room anchor, not scattered decoration everywhere."),
            ("Tasteful details", "Names, themes, and color palettes can be personal while the finished piece stays clean and elevated."),
            ("Venue or home fit", "Delivery, pickup, indoor/outdoor placement, and teardown choices change the right recommendation."),
            ("Inquiry first", "The contact form lets the team shape the right piece before promising a product or price."),
        ],
        "client_groups": [
            ("Venue and event context", ["Alpine Events", "Lux Events", "Ogden Country Club", "The Boiler Room"]),
            ("Family-facing settings", ["Station Park", "Newgate Mall", "Shops at Southtown", "Tree House Museum"]),
            ("Celebration types", ["Birthdays", "Weddings", "Showers", "Memorials", "Hosted family events"]),
        ],
        "stories_heading": "Personal events still need structure.",
        "stories_lede": "Personal celebrations work best when the room has one clear focal point and the setup fits the place.",
        "stories": [
            {
                "kicker": "Milestone birthdays",
                "title": "A clear focal point for the room",
                "body": "Birthday installs work best when the balloon piece gives guests one finished place to gather, photograph, and celebrate.",
                "image": f"{PORTFOLIO_BASE}/birthday-dolphin-backdrop.webp",
                "alt": "Birthday balloon backdrop with a finished photo moment",
            },
            {
                "kicker": "Weddings and showers",
                "title": "Soft color, clean structure",
                "body": "Private celebrations can carry personal colors and themes while still feeling composed, warm, and venue-ready.",
                "image": f"{PORTFOLIO_BASE}/wedding-floral-half-arch.webp",
                "alt": "Wedding floral balloon half arch for a private celebration",
            },
            {
                "kicker": "Family gatherings",
                "title": "Easy to understand at a glance",
                "body": "A polished arch, column, or backdrop helps a personal gathering feel intentional without overcomplicating the room.",
                "image": f"{PORTFOLIO_BASE}/birthday-balloon-bouquets.webp",
                "alt": "Birthday balloon bouquets arranged for a private celebration",
            },
        ],
        "gallery_heading": "Inspiration for personal celebrations.",
        "gallery_lede": "Private-event customers often know the feeling before they know the product name. These examples help turn that feeling into a clear quote request.",
        "gallery": [
            {"title": "Floral half arch", "caption": "Soft, polished, and personal for weddings, showers, and hosted celebrations.", "image": f"{PORTFOLIO_BASE}/wedding-floral-half-arch.webp", "alt": "Wedding floral balloon half arch for a private celebration", "wide": True},
            {"title": "Under-the-sea backdrop", "caption": "A themed photo moment that still feels finished and intentional.", "image": f"{PORTFOLIO_BASE}/birthday-dolphin-backdrop.webp", "alt": "Ocean-themed birthday balloon backdrop", "wide": True},
            {"title": "Birthday bouquets", "caption": "Pickup-friendly pieces can still make the room feel ready.", "image": f"{PORTFOLIO_BASE}/birthday-balloon-bouquets.webp", "alt": "Birthday balloon bouquets arranged for a party table", "wide": False},
        ],
        "plan_title": "What private-event planners need to settle early",
        "plan": [
            {
                "title": "The main photo moment",
                "text": "Name the part of the room that should feel finished first: entrance, table, backdrop, stage, or gift area.",
                "bullets": ["Birthday backdrops", "Wedding accents", "Shower entrances", "Memorial stands"],
            },
            {
                "title": "Room and delivery fit",
                "text": "The same idea changes if it is a home, venue, church hall, backyard, or pickup piece.",
                "bullets": ["Ceiling height", "Indoor/outdoor", "Delivery access", "Pickup timing"],
            },
            {
                "title": "Personal details",
                "text": "Colors, names, theme notes, and tone help shape the design without promising a preset package.",
                "bullets": ["Names", "Palette", "Mood", "Family priorities"],
            },
        ],
        "cta_title": "Tell us what you are imagining.",
        "cta_body": "Send the date, place, colors, and the moment you want the room to hold. Locally Twisted will help shape the right quote.",
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
