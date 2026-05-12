"""Shared content model for Event Balloons audience pages."""

from __future__ import annotations

from locally_twisted.seo import service_schema


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

.lt-event-type-page .lt-authority-hero__lede {
  max-width: 43rem;
}

.lt-event-type-page .lt-authority-actions {
  flex-wrap: wrap;
}

@media (min-width: 1200px) {
  .lt-event-type-page .lt-authority-hero__content {
    padding-block: 20px;
  }

  .lt-event-type-page .lt-authority-hero h1 {
    font-size: 2.55rem;
    line-height: 1.02;
  }

  .lt-event-type-page .lt-authority-hero__lede {
    line-height: 1.28;
    margin-bottom: 0.65rem;
  }
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
  padding: clamp(2.5rem, 6vw, 4.5rem) 1rem;
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
  column-count: 3;
  column-gap: clamp(0.75rem, 1.5vw, 1rem);
}

.lt-audience-gallery__item {
  break-inside: avoid;
  display: block;
  margin: 0;
  padding: 0 0 clamp(0.75rem, 1.5vw, 1rem);
}

.lt-audience-gallery__item img {
  display: block;
  width: 100%;
  height: auto;
  object-fit: contain;
  background: var(--lt-stone);
}

@media (max-width: 899.98px) {
  .lt-audience-gallery__grid {
    column-count: 2;
  }
}

@media (max-width: 575.98px) {
  .lt-audience-gallery__grid {
    column-count: 1;
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
LANDING_PHOTO_BASE = "/assets/locally_twisted/images/landing-page-pics"


def _photo(folder: str, filename: str, alt: str) -> dict[str, str]:
    return {"image": f"{LANDING_PHOTO_BASE}/{folder}/{filename}", "alt": alt}


EVENT_TYPE_PAGES = {
    "civic_community": {
        "route": "civic-community",
        "root_class": "lt-page-civic",
        "eyebrow": "Civic and community events",
        "title": "Community events deserve a photo people frame.",
        "lede": (
            "Parades, ribbon cuttings, festivals, and fundraisers. Locally Twisted has installed "
            "alongside Utah civic teams and volunteers for more than 20 years. We bring the decor "
            "and the install crew so your volunteers can run the event."
        ),
        "meta_title": "Civic and Community Balloon Decor in Utah",
        "meta_description": (
            "Photo-ready balloon decor for Utah parades, chambers, school fundraisers, city "
            "festivals, and public events. Sponsor-color recognition and volunteer-friendly install."
        ),
        "quote_href": "/contact?intent=quote&source=civic-community",
        "support_href": "/portfolio?event=civic",
        "support_label": "See Civic Work",
        "proof_bar": [
            {
                "icon": "trusted-partner",
                "label": "Install crew included",
                "sub": "Your volunteers run the program. We deliver, install, and remove the decor.",
            },
            {
                "icon": "civic-parade",
                "label": "Photo-ready moments",
                "sub": "Ribbon-cutting arches, stage backdrops, sponsor-color photo walls.",
            },
            {
                "icon": "delivery-install",
                "label": "Weather plans built in",
                "sub": "Indoor backup, weighted bases, wind-aware sizing. We call early when it matters.",
            },
            {
                "icon": "design-driven",
                "label": "Sponsor color recognition",
                "sub": "Brand colors woven through garlands, arches, and photo backdrops.",
            },
        ],
        "named_orgs": {
            "eyebrow": "Real organizations",
            "heading": "Utah cities, chambers, and community teams already trust us.",
            "lede": (
                "Two decades of installations across municipal events, school fundraisers, "
                "chamber galas, festivals, and public celebrations."
            ),
            "photos": [
                {
                    "image": f"{PORTFOLIO_BASE}/seasonal-pride-columns.webp",
                    "alt": "Rainbow balloon columns at a Utah community event",
                },
                {
                    "image": f"{PORTFOLIO_BASE}/corporate-weberstock-photo-opt.webp",
                    "alt": "Large festival-scale balloon photo backdrop",
                },
                {
                    "image": f"{PORTFOLIO_BASE}/seasonal-easter-rabbit-arch.webp",
                    "alt": "Seasonal balloon arch at a public family event",
                },
            ],
            "ribbon_label": "Installed for",
            # TODO(GL): Confirm which of these names LT has genuinely installed for.
            "names": [
                "Ogden City",
                "Sandy City",
                "Herriman City",
                "Syracuse City",
                "SLC County",
                "UDOT",
                "SLC Pride",
                "Equality Utah",
                "Ogden Weber Chamber",
                "Gallivan Center",
                "Ogden Airport",
                "Safe Kids Fair",
            ],
        },
        "process": {
            "eyebrow": "How we work with civic organizers",
            "heading": "Your volunteers run the event. We handle the decor.",
            "lede": (
                "The civic event workflow is built for chamber organizers, school PTAs, city "
                "coordinators, and nonprofit volunteer leads who already have enough to manage."
            ),
            "steps": [
                "Send the event, the location, and your sponsor list. Quote returned within one or two business days.",
                "We work with municipal permitting and venue contacts directly when needed.",
                "Lead time: two to three weeks for parades, festivals, and fairs. Faster for ribbon cuttings.",
                "Outdoor events get a weather call window communicated 48 hours before doors.",
                "Sponsor colors woven into garlands, arches, or backdrops so recognition reads in every photo.",
                "Volunteer-friendly install. We arrive, set up, and remove so your team focuses on the program.",
            ],
            "photo": {
                "image": f"{PORTFOLIO_BASE}/seasonal-pride-columns.webp",
                "alt": "Locally Twisted civic install at a public Utah event",
            },
        },
        "featured_install": {
            "eyebrow": "Featured civic install",
            "title": "Festival-scale photo backdrop, sponsor-color garlands, weather contingency on file.",
            "image": f"{PORTFOLIO_BASE}/corporate-weberstock-photo-opt.webp",
            "alt": "Large balloon installation at a Utah community festival",
            "facts": [
                {"label": "Event", "value": "Public community festival"},  # TODO: name the event
                {"label": "Scope", "value": "Large photo backdrop, sponsor-color garlands, entrance arch"},
                {"label": "Lead time", "value": "Quoted three weeks ahead"},
                {"label": "Setup", "value": "Pre-doors install, weather call window confirmed 48 hours prior"},
                {"label": "Outcome", "value": "Event-night photos used in chamber communications"},
            ],
        },
        # TODO(GL): Add real PTA / chamber / civic-organizer quote when permission granted.
        # "pull_quote": {
        #     "text": "We had a parade to run. They handled the rest.",
        #     "attribution": "Chamber event organizer - Northern Utah",
        # },
        "gallery_heading": "More civic and community work.",
        "gallery_lede": "A broader look at the kinds of public-facing rooms and outdoor moments we have built.",
        "gallery": [
            _photo("community", "balloon Ferris wheel Salt lake city utah - Copy.webp", "Balloon Ferris wheel installation at a Utah public event"),
            _photo("community", "Barbie Box photo opt - Copy.webp", "Life-size themed balloon photo box at a community event"),
            _photo("community", "bird costums for parades.webp", "Costumed parade characters at a public community event"),
            _photo("community", "Giant Pumpkin Balloon.webp", "Large pumpkin balloon sculpture for a public seasonal event"),
            _photo("community", "IMG_0215.webp", "Balloon decor installation for a community celebration"),
            _photo("community", "IMG_1807 - Copy.webp", "Large balloon decor for a Utah community event"),
            _photo("community", "IMG_2628 - Copy.webp", "Balloon installation at a civic or community gathering"),
            _photo("community", "IMG_2635 - Copy.webp", "Community event balloon decor with large-scale color"),
            _photo("community", "IMG_8457 - Copy.webp", "Photo-ready balloon installation for a Utah public event"),
            _photo("community", "IMG_8625 - Copy.webp", "Balloon decor built for a community event space"),
            _photo("community", "leukemia .webp", "Balloon decor for a community fundraising event"),
            _photo("community", "tree house dinner.webp", "Balloon decor for a Treehouse Museum community event"),
        ],
        "faq_eyebrow": "Questions civic organizers ask",
        "faq_heading": "What you need before you bring it to your board.",
        "faq": [
            {
                "q": "Can you work with our municipal permit process?",
                "a": (
                    "Yes. Send the venue, the date, and the permitting contact and we will "
                    "coordinate directly. We have worked with city event coordinators, public "
                    "venues, and street/plaza permits across the Wasatch Front."
                ),
            },
            {
                "q": "Outdoor event - what is your wind and weather plan?",
                "a": (
                    "Every outdoor install uses weighted bases and wind-aware sizing. We call "
                    "the weather window 48 hours before doors so you can decide whether to "
                    "trigger the indoor backup, which we plan with you up front."
                ),
            },
            {
                "q": "Can you coordinate sponsor colors or logos in the decor?",
                "a": (
                    "Yes. Send your sponsor list with brand colors and we will weave recognition "
                    "into the garland, arch, or photo backdrop so sponsors read in every event "
                    "photo without becoming the whole visual."
                ),
            },
            {
                "q": "We are a 501(c)(3) - do you offer nonprofit pricing?",
                "a": (
                    "We work with nonprofits regularly. Mention your status in the inquiry and "
                    "we will share the options available for your scope."
                ),
            },
            {
                "q": "Will our volunteers need to help with setup?",
                "a": (
                    "No. We deliver, install, and remove the decor. Your volunteers focus on "
                    "the program, the photo line, the sponsor table, and everything that needs "
                    "a person who knows your event."
                ),
            },
            {
                "q": "Can you do a school fundraiser within a typical PTA budget?",
                "a": (
                    "Often yes. Send your budget range, the event, and a photo of the space and "
                    "we will scope to what is doable. We will be honest if the scale you want "
                    "needs more, and we will tell you what is possible at the budget you have."
                ),
            },
        ],
        "cta_title": "Planning a public event?",
        "cta_body": (
            "Send the date, location, audience, and rough install goal. Locally Twisted will "
            "shape a quote within one or two business days."
        ),
    },
    "corporate_events": {
        "route": "corporate-events",
        "root_class": "lt-page-corporate",
        "eyebrow": "Corporate events",
        "title": "Corporate balloon decor that lands the way your meeting does.",
        "lede": (
            "Lobby installations, brand-aligned color, and on-time setup before doors open. "
            "Locally Twisted has installed for Utah corporate offices, conferences, and team "
            "events for more than 20 years."
        ),
        "meta_title": "Corporate Event Balloon Decor in Utah",
        "meta_description": (
            "Brand-aligned balloon decor for Utah corporate events, launches, conferences, "
            "and team celebrations. Twenty years of professional install experience, PO and "
            "COI ready."
        ),
        "quote_href": "/contact?intent=quote&source=corporate-events",
        "support_href": "/portfolio?event=corporate",
        "support_label": "See Corporate Work",
        # --- NEW: 4-tile buyer-language proof bar with brass-line icons ---
        # Icon names map to files in apps/locally_twisted/locally_twisted/public/icons/brand/<name>.svg
        "proof_bar": [
            {
                "icon": "trusted-partner",
                "label": "Booked off a PO",
                "sub": "We invoice. W-9 on request. Repeat corporate work supported on standard terms.",
            },
            {
                "icon": "delivery-install",
                "label": "Setup before doors",
                "sub": "Standard 90-minute install windows. Off-hours and overnight setup available on request.",
            },
            {
                "icon": "design-driven",
                "label": "Brand-color matched",
                "sub": "Bring your brand deck or Pantone reference. We match to closest stock latex.",
            },
            {
                "icon": "professional",
                "label": "Certificate of Insurance",
                "sub": "COI available on request, with additional-insured language for your venue or building.",
            },
        ],
        # --- NEW: Named-organization wall ---
        # TODO: replace placeholder list with confirmed corporate clients once GL/Jeff verify
        #       who LT has actually installed for. Avoid name-dropping orgs LT hasn't worked with.
        "named_orgs": {
            "eyebrow": "Real organizations",
            "heading": "Utah corporate teams have trusted us before.",
            "lede": (
                "Over 20 years of installations across Utah business and finance, media, "
                "restaurants and retail, and campus events."
            ),
            # TODO(GL): Drop in real photos of installs at named corporate clients.
            # Three is the sweet spot; the photos do the heavy lifting and the ribbon
            # below picks up the name-dropping in a single editorial credit line.
            "photos": [
                {
                    "image": f"{PORTFOLIO_BASE}/corporate-logo-arch.webp",
                    "alt": "Branded corporate balloon arch at a Utah event entrance",
                },
                {
                    "image": f"{PORTFOLIO_BASE}/corporate-weberstock-photo-opt.webp",
                    "alt": "Large corporate balloon backdrop for a Utah business event",
                },
                {
                    "image": f"{PORTFOLIO_BASE}/corporate-wsu-arch-bouquets.webp",
                    "alt": "Corporate-color balloon arch and bouquet install",
                },
            ],
            "ribbon_label": "Installed for",
            # TODO(GL): Confirm which of these names LT has genuinely installed for.
            # Remove any that are aspirational; keep only verified clients.
            "names": [
                "Ancestry",
                "Zions Bank",
                "America First CU",
                "Fidelity",
                "KSL",
                "KUTV",
                "FOX13",
                "Utah Jazz",
                "FanX",
                "Megaplex",
                "Chick-fil-A",
                "Texas Roadhouse",
            ],
        },
        # --- NEW: "How we work with corporate planners" process list ---
        "process": {
            "eyebrow": "How we work with corporate planners",
            "heading": "Hand it off. We handle the install.",
            "lede": (
                "The corporate event workflow is built for secretaries, EAs, and office "
                "managers who need the decor to be one less thing to worry about."
            ),
            "steps": [
                "Email or call with date, venue, and rough scope. Quote returned within one business day.",
                "PO or card on file. W-9 and COI provided on request before the work starts.",
                "Lead time: two weeks standard. Forty-eight hours possible for arches and columns when stock allows.",
                "Loading dock, freight elevator, and after-hours access notes go in the work order.",
                "Setup typically completes 60 to 90 minutes before doors open. Off-hours and overnight available.",
                "Same-day teardown and balloon disposal included. Event photos returned for your file.",
            ],
            "photo": {
                # TODO(GL): Replace with a real "setup in progress" photo from a corporate venue
                # (install crew at work, ladder, branded décor mid-build). Reusing portfolio shot for now.
                "image": f"{PORTFOLIO_BASE}/corporate-logo-arch.webp",
                "alt": "Locally Twisted install crew finishing a branded corporate event entrance",
            },
        },
        # --- NEW: Featured installation case-study ---
        # TODO(GL): Replace with a real named corporate install. Fill in actual lead time,
        # attendee count, setup window, and event type. No fabricated stats.
        "featured_install": {
            "eyebrow": "Featured corporate install",
            "title": "Annual all-hands, brand-color entrance, dock setup before 7am.",
            "image": f"{PORTFOLIO_BASE}/corporate-weberstock-photo-opt.webp",
            "alt": "Branded balloon installation for a Utah corporate annual event",
            "facts": [
                {"label": "Event", "value": "Corporate annual gathering"},  # TODO: name the event
                {"label": "Scope", "value": "Branded entrance arch + two column pairs + registration garlands"},
                {"label": "Lead time", "value": "Quoted three weeks ahead of event date"},
                {"label": "Setup", "value": "Dock load-in 6:00am, complete by 7:30am"},
                {"label": "Notes", "value": "Same-day teardown. Photos returned for the planning file."},
            ],
        },
        # --- NEW: Pull-quote attributed by role (NOT by name unless permission granted) ---
        # TODO(GL): Replace with a real EA/secretary/events-coordinator quote we have permission
        # to publish. Until that exists, this section stays absent — the template renders nothing.
        # "pull_quote": {
        #     "text": "I sent one email and they handled the rest. The arch was up before our first guests arrived.",
        #     "attribution": "Executive Assistant - Utah finance firm",
        # },
        # --- Existing: gallery (kept as-is; real installs already in place) ---
        "gallery_heading": "Real corporate installs.",
        "gallery": [
            _photo("corporate", "25_ 24_ balloon plus stars organic.webp", "Large organic balloon arch with star accents for a corporate event"),
            _photo("corporate", "Custom halloween backdrop - Copy.webp", "Custom Halloween balloon backdrop for a branded event"),
            _photo("corporate", "ihc heart columns latex free.webp", "Latex-free heart balloon columns for a corporate or healthcare event"),
            _photo("corporate", "IMG_1263 - Copy.webp", "Corporate balloon decor installation in a Utah event space"),
            _photo("corporate", "IMG_1799 - Copy.webp", "Professional balloon installation for a corporate event"),
            _photo("corporate", "IMG_1802 - Copy.webp", "Balloon decor arranged for a business event entrance"),
            _photo("corporate", "IMG_3809 - Copy.webp", "Corporate event balloon decor with branded color"),
            _photo("corporate", "IMG_4341 - Copy.webp", "Corporate balloon installation for a public-facing event"),
            _photo("corporate", "Smurfs backdrop - Copy.webp", "Custom movie-release balloon backdrop for a corporate event"),
            _photo("corporate", "Smurfs movie release - Copy.webp", "Balloon decor for a branded movie release event"),
            _photo("corporate", "UTA Photo opt.webp", "Large balloon photo opportunity for a Utah organization event"),
            _photo("corporate", "walmart.webp", "Corporate balloon decor for a Walmart event"),
        ],
        # --- NEW: Plain-language FAQ (corporate buyer's questions, in their words) ---
        "faq_eyebrow": "Questions corporate planners ask",
        "faq_heading": "What you need before you send the request to your team.",
        "faq": [
            {
                "q": "Do you invoice and accept POs?",
                "a": (
                    "Yes. We invoice in advance or after the event depending on your AP workflow. "
                    "Send us your billing contact and any vendor onboarding paperwork with the "
                    "initial inquiry and we will get it back the same day."
                ),
            },
            {
                "q": "Can you provide a certificate of insurance?",
                "a": (
                    "Yes. We carry general liability and can issue a COI naming your building or "
                    "venue as additional insured. Send the venue's COI requirements with the "
                    "inquiry and we will route it to our carrier."
                ),
            },
            {
                "q": "How fast can you turn a quote?",
                "a": (
                    "One business day for standard scope. Larger or multi-room installs may take "
                    "a second touch to scope correctly, but we will respond within one business "
                    "day either way."
                ),
            },
            {
                "q": "Can you match our exact brand colors?",
                "a": (
                    "We match to the closest stock latex available. Send your brand deck, Pantone "
                    "references, or sample swatches with the inquiry. If your brand color sits "
                    "outside the stock palette, we will tell you up front and propose the nearest "
                    "match."
                ),
            },
            {
                "q": "What lead time do you need?",
                "a": (
                    "Two weeks is the standard. Arches, columns, and standard color bouquets can "
                    "often be turned in 48 hours when stock allows. For brand-specific color "
                    "matches or sponsor-coordinated installs, give us as much notice as you can."
                ),
            },
            {
                "q": "Do you handle teardown and disposal?",
                "a": (
                    "Yes. Same-day teardown and balloon disposal are included on standard "
                    "corporate installs. Next-day teardown is available for events that run late "
                    "or wrap on a weekend."
                ),
            },
        ],
        "cta_title": "Tell us what the event needs.",
        "cta_body": (
            "Send the date, venue, brand colors, and rough scope. We will return a quote within "
            "one business day. The next step is a quote, not an online purchase."
        ),
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
        "named_orgs": {
            # TODO(GL): Confirm which of these names LT has genuinely installed for.
            "names": [
                "University of Utah",
                "Weber State",
                "St. Joseph's",
                "Tree House Museum",
                "Sea Quest",
                "Safe Kids Fair",
                "Western Sports Park",
                "Graduations",
                "Back-to-School Events",
                "Assemblies",
                "Athletics",
                "Family Nights",
            ],
        },
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
            _photo("school", "Back to school stage display - Copy.webp", "Back-to-school balloon stage display"),
            _photo("school", "Back to school stage display 4 - Copy.webp", "Large back-to-school balloon stage installation"),
            _photo("school", "Cactus columns - Copy.webp", "Cactus-themed balloon columns for a school event"),
            _photo("school", "north davis.webp", "North Davis school balloon decor"),
            _photo("school", "Sports themed balloon arch.webp", "Sports-themed balloon arch for a campus event"),
            _photo("school", "UofU football.webp", "University of Utah football balloon decor"),
            _photo("school", "Weber balloons.webp", "Weber school-color balloon decor"),
            _photo("school", "WSU arch and bouquets - Copy.webp", "Weber State balloon arch and bouquets"),
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
        "title": "The reveal that makes the room gasp.",
        "lede": (
            "Birthdays, baby showers, gender reveals, milestone anniversaries, hosted family events. "
            "Locally Twisted has been making the photo-ready moment for Utah families since 2003."
        ),
        "meta_title": "Private Celebration Balloon Decor in Utah",
        "meta_description": (
            "Photo-ready balloon decor for Utah birthdays, baby showers, gender reveals, milestone "
            "anniversaries, and hosted family events. Delivered before guests arrive."
        ),
        "quote_href": "/contact?intent=quote&source=private-celebrations",
        "support_href": "/portfolio?event=private",
        "support_label": "See Celebration Work",
        "proof_bar": [
            {
                "icon": "premium-private-event",
                "label": "The WOW moment",
                "sub": "Designed for the photo before the first guest arrives.",
            },
            {
                "icon": "trusted-partner",
                "label": "Kid-safe materials",
                "sub": "Latex from industry-trusted suppliers. We brief you on choking-hazard awareness.",
            },
            {
                "icon": "balloon-arch",
                "label": "Indoor or outdoor",
                "sub": "Weighted bases, ceiling-safe install, anchoring for backyard or venue.",
            },
            {
                "icon": "delivery-install",
                "label": "Delivered before guests",
                "sub": "Time-of-arrival coordinated. Surprise reveals timed to your moment.",
            },
        ],
        "named_orgs": {
            "eyebrow": "Real venues, real homes",
            "heading": "Utah families and venues have hosted us for over 20 years.",
            "lede": (
                "Two decades of birthdays, baby showers, gender reveals, weddings, milestone "
                "anniversaries, memorials, and hosted family events."
            ),
            "photos": [
                {
                    "image": f"{PORTFOLIO_BASE}/birthday-dolphin-backdrop.webp",
                    "alt": "Themed birthday balloon backdrop for a private celebration",
                },
                {
                    "image": f"{PORTFOLIO_BASE}/wedding-floral-half-arch.webp",
                    "alt": "Floral wedding balloon half arch for a private celebration",
                },
                {
                    "image": f"{PORTFOLIO_BASE}/birthday-balloon-bouquets.webp",
                    "alt": "Birthday balloon bouquets arranged for a private celebration",
                },
            ],
            "ribbon_label": "Installed at",
            # TODO(GL): Confirm which venues / event types LT has genuinely installed for.
            "names": [
                "Alpine Events",
                "Lux Events",
                "Ogden Country Club",
                "The Boiler Room",
                "Station Park",
                "Tree House Museum",
                "Birthdays",
                "Baby Showers",
                "Gender Reveals",
                "Weddings",
                "Milestone Anniversaries",
                "Memorials",
            ],
        },
        "process": {
            "eyebrow": "How we work on private events",
            "heading": "Tell us the photo you want. We bring the rest.",
            "lede": (
                "The private-event workflow is built for parents, hosts, and family planners "
                "who know the feeling they want before they know the product name."
            ),
            "steps": [
                "Send the event, the date, and the photo you want. Quote returned within one or two business days.",
                "Card on file holds the date. Deposit applied to the final balance.",
                "Lead time: two weeks standard. Rush available when stock and schedule allow.",
                "Indoor or outdoor. We ask about ceilings, sun, wind, pets, and kids' ages so the install is safe.",
                "Delivery window timed so the host gets the reveal before guests arrive.",
                "Same-day or next-day teardown available. We will tell you which fits your venue.",
            ],
            "photo": {
                "image": f"{PORTFOLIO_BASE}/birthday-dolphin-backdrop.webp",
                "alt": "Locally Twisted private-event install in a Utah celebration space",
            },
        },
        "featured_install": {
            "eyebrow": "Featured private install",
            "title": "Surprise birthday reveal, themed photo wall, delivered while the guest of honor was at brunch.",
            "image": f"{PORTFOLIO_BASE}/birthday-dolphin-backdrop.webp",
            "alt": "Themed birthday balloon backdrop installed for a Utah private celebration",
            "facts": [
                {"label": "Event", "value": "Milestone birthday surprise"},  # TODO: name the event
                {"label": "Scope", "value": "Themed photo backdrop, balloon column pair, table bouquets"},
                {"label": "Lead time", "value": "Quoted two weeks ahead"},
                {"label": "Delivery", "value": "Two-hour window aligned with guest-of-honor away time"},
                {"label": "Outcome", "value": "Reveal photo used in the family's holiday card"},
            ],
        },
        # TODO(GL): Add real parent/host quote when permission granted.
        # "pull_quote": {
        #     "text": "She walked in and the whole room went quiet. We still talk about that photo.",
        #     "attribution": "Birthday host - Salt Lake City",
        # },
        "gallery_heading": "More private celebrations.",
        "gallery_lede": "A broader look at the kinds of personal moments we have built.",
        "gallery": [
            _photo("private", "birthday.webp", "Birthday balloon decor for a private celebration"),
            _photo("private", "birthday1.webp", "Birthday balloon display for a private event"),
            _photo("private", "carrousel.webp", "Carousel-themed decor for a private celebration"),
            _photo("private", "Floral backdrop.webp", "Floral balloon backdrop for a private celebration"),
            _photo("private", "home tree.webp", "Home celebration balloon decor"),
            _photo("private", "IMG_9061 - Copy.webp", "Private party balloon installation"),
            _photo("private", "private.webp", "Balloon decor for a private hosted celebration"),
            _photo("private", "retirement remove watermark.webp", "Retirement balloon decor for a private celebration"),
        ],
        "faq_eyebrow": "Questions hosts ask",
        "faq_heading": "What you need to know before the party.",
        "faq": [
            {
                "q": "How far in advance do I book?",
                "a": (
                    "Two weeks is the standard. Rush windows are available when stock and "
                    "schedule allow. Send the date as early as you can - the calendar fills "
                    "fastest around graduation, spring/summer wedding, and holiday seasons."
                ),
            },
            {
                "q": "Can I see colors in person?",
                "a": (
                    "Yes. Send a Pinterest board, photo, or color swatch and we will match to "
                    "the closest stock latex. For complicated palettes, we can show samples "
                    "before the install is built."
                ),
            },
            {
                "q": "Is it kid-safe and pet-safe?",
                "a": (
                    "We use latex from industry-trusted suppliers and brief you on "
                    "choking-hazard awareness when kids under three will be at the party. We "
                    "anchor and weight installs so pets, toddlers, and the wind cannot pull "
                    "them down."
                ),
            },
            {
                "q": "What if it rains, or it is hot, or my event is in the backyard?",
                "a": (
                    "Outdoor installs use weighted bases, wind-aware sizing, and a weather "
                    "plan we agree on before delivery. We will call the weather window 24 to "
                    "48 hours before doors and you decide whether to trigger the indoor plan."
                ),
            },
            {
                "q": "Can you set up while I keep the birthday person out of the room?",
                "a": (
                    "Yes. Tell us the surprise window in the inquiry and we will time delivery "
                    "and install so the reveal happens the way you imagined."
                ),
            },
            {
                "q": "What is the smallest size you do, and what is a typical price range?",
                "a": (
                    "Bouquets, single columns, and table arrangements work for smaller "
                    "gatherings. Larger backdrops, arches, and full room installs scale up "
                    "from there. Send the event and your rough budget in the inquiry and we "
                    "will be honest about what fits and what does not."
                ),
            },
            {
                "q": "Will it last through the whole party?",
                "a": (
                    "Yes. We use installation techniques and materials selected for the "
                    "event length and environment. Heat, sun, ceiling height, and indoor "
                    "versus outdoor each change the choice; we plan for the conditions of "
                    "your specific event."
                ),
            },
        ],
        "cta_title": "Tell us what you are imagining.",
        "cta_body": (
            "Send the date, place, colors, and the moment you want the room to hold. "
            "Locally Twisted will shape the right quote within one or two business days."
        ),
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
    context.structured_data = [
        service_schema(
            event_page["meta_title"],
            event_page["meta_description"],
            f"/{event_page['route']}",
            service_type="Balloon decor and event installation",
        )
    ]
    return context
