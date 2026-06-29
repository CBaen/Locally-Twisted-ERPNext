"""Ad landing-page content for ready-to-order bouquet products."""

from __future__ import annotations

AD_CAMPAIGN_SLUG = "lt_bouquet_test_2026q3"


PAGE_CSS = """
.lt-product-ad-page {
  background: var(--lt-warm-white);
  color: var(--lt-ink);
}

.lt-product-ad-page .lt-fullbleed {
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  width: 100vw;
}

.lt-ad-hero {
  background:
    linear-gradient(135deg, rgba(14, 34, 64, 0.96), rgba(10, 10, 11, 0.94));
  border-bottom: 4px solid var(--lt-crimson);
  color: var(--lt-warm-white);
  padding: clamp(2.5rem, 7vw, 4.5rem) 1rem;
}

.lt-ad-hero__inner,
.lt-ad-proof__inner,
.lt-ad-section__inner,
.lt-ad-gallery__inner,
.lt-ad-cta__inner {
  box-sizing: border-box;
  margin: 0 auto;
  width: min(1160px, 100%);
}

.lt-ad-hero__inner {
  align-items: center;
  display: grid;
  gap: clamp(1.4rem, 4vw, 2.8rem);
  grid-template-columns: minmax(0, 1fr);
}

@media (min-width: 900px) {
  .lt-ad-hero__inner {
    grid-template-columns: minmax(0, 0.9fr) minmax(320px, 0.72fr);
  }
}

.lt-ad-eyebrow,
.lt-ad-kicker {
  color: var(--lt-brass);
  font-family: var(--lt-font-body);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.25;
  margin: 0 0 0.65rem;
  text-transform: uppercase;
}

.lt-ad-hero h1,
.lt-ad-section h2,
.lt-ad-gallery h2,
.lt-ad-cta h2 {
  font-family: var(--lt-font-heading);
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.02;
  margin: 0;
}

.lt-ad-hero h1 {
  color: var(--lt-warm-white);
  font-size: clamp(2.25rem, 6vw, 4.35rem);
  max-width: 12ch;
}

.lt-ad-hero__lede {
  color: rgba(250, 247, 242, 0.9);
  font-family: var(--lt-font-body);
  font-size: clamp(1rem, 2vw, 1.17rem);
  line-height: 1.52;
  margin: 0.95rem 0 0;
  max-width: 38rem;
}

.lt-ad-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  margin-top: 1.2rem;
}

.lt-ad-button {
  align-items: center;
  border: 1px solid transparent;
  border-radius: 4px;
  display: inline-flex;
  font-family: var(--lt-font-body);
  font-size: 0.86rem;
  font-weight: 900;
  justify-content: center;
  line-height: 1.2;
  min-height: 44px;
  padding: 0.82rem 1rem;
  text-decoration: none;
  text-transform: uppercase;
}

.lt-ad-button--primary {
  background: var(--lt-crimson);
  color: #fff;
}

.lt-ad-button--secondary {
  background: transparent;
  border-color: rgba(250, 247, 242, 0.45);
  color: var(--lt-warm-white);
}

.lt-ad-button:focus-visible {
  outline: 3px solid rgba(184, 154, 91, 0.58);
  outline-offset: 3px;
}

.lt-ad-hero__media {
  margin: 0;
}

.lt-ad-hero__media img {
  aspect-ratio: 4 / 3;
  background: rgba(250, 247, 242, 0.08);
  border: 1px solid rgba(250, 247, 242, 0.18);
  display: block;
  object-fit: cover;
  width: 100%;
}

.lt-ad-hero__media figcaption {
  color: rgba(250, 247, 242, 0.78);
  font-family: var(--lt-font-body);
  font-size: 0.88rem;
  line-height: 1.45;
  margin-top: 0.65rem;
}

.lt-ad-proof {
  background: #fffdf9;
  border-bottom: 1px solid rgba(14, 34, 64, 0.12);
  padding: 1rem;
}

.lt-ad-proof__inner {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: minmax(0, 1fr);
}

@media (min-width: 760px) {
  .lt-ad-proof__inner {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.lt-ad-proof__item {
  border-left: 4px solid var(--lt-brass);
  min-width: 0;
  padding: 0.4rem 0 0.4rem 0.85rem;
}

.lt-ad-proof__label {
  color: var(--lt-navy);
  display: block;
  font-family: var(--lt-font-heading);
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.08;
}

.lt-ad-proof__text {
  color: var(--lt-soft-gray);
  display: block;
  font-family: var(--lt-font-body);
  font-size: 0.94rem;
  line-height: 1.45;
  margin-top: 0.2rem;
}

.lt-ad-section,
.lt-ad-gallery {
  padding: clamp(2.75rem, 7vw, 5rem) 1rem;
}

.lt-ad-section--warm {
  background: #faf7f2;
}

.lt-ad-section--white,
.lt-ad-gallery {
  background: #fffdf9;
}

.lt-ad-section__heading,
.lt-ad-gallery__heading {
  max-width: 760px;
}

.lt-ad-section h2,
.lt-ad-gallery h2 {
  color: var(--lt-navy);
  font-size: clamp(2rem, 5vw, 3.35rem);
}

.lt-ad-section__lede,
.lt-ad-gallery__lede {
  color: var(--lt-soft-gray);
  font-family: var(--lt-font-body);
  font-size: 1rem;
  line-height: 1.62;
  margin: 0.85rem 0 0;
  max-width: 45rem;
}

.lt-ad-grid,
.lt-ad-step-grid,
.lt-ad-gallery__grid {
  display: grid;
  gap: clamp(0.9rem, 2.5vw, 1.25rem);
  grid-template-columns: minmax(0, 1fr);
  margin-top: 1.45rem;
}

@media (min-width: 760px) {
  .lt-ad-grid,
  .lt-ad-step-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .lt-ad-gallery__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.lt-ad-card,
.lt-ad-step {
  background: #fff;
  border: 1px solid rgba(14, 34, 64, 0.14);
  border-radius: 4px;
  box-shadow: 0 16px 34px rgba(10, 10, 11, 0.06);
  min-width: 0;
  padding: clamp(1rem, 3vw, 1.35rem);
}

.lt-ad-card h3,
.lt-ad-step h3 {
  color: var(--lt-ink);
  font-family: var(--lt-font-heading);
  font-size: clamp(1.35rem, 3vw, 1.85rem);
  line-height: 1.08;
  margin: 0;
}

.lt-ad-card p,
.lt-ad-step p {
  color: var(--lt-soft-gray);
  font-family: var(--lt-font-body);
  font-size: 0.96rem;
  line-height: 1.56;
  margin: 0.7rem 0 0;
}

.lt-ad-step__number {
  color: var(--lt-crimson);
  display: block;
  font-family: var(--lt-font-body);
  font-size: 0.78rem;
  font-weight: 900;
  margin-bottom: 0.45rem;
}

.lt-ad-gallery__item {
  margin: 0;
  min-width: 0;
}

.lt-ad-gallery__item img {
  aspect-ratio: 1 / 1;
  background: var(--lt-stone);
  display: block;
  object-fit: cover;
  width: 100%;
}

.lt-ad-gallery__item--wide {
  grid-column: span 1;
}

@media (min-width: 760px) {
  .lt-ad-gallery__item--wide {
    grid-column: span 2;
  }

  .lt-ad-gallery__item--wide img {
    aspect-ratio: 2 / 1;
  }
}

.lt-ad-cta {
  background: linear-gradient(135deg, rgba(14, 34, 64, 0.96), rgba(10, 10, 11, 0.96));
  border-top: 1px solid rgba(184, 154, 91, 0.48);
  color: var(--lt-warm-white);
  padding: clamp(2.75rem, 7vw, 4.5rem) 1rem;
}

.lt-ad-cta__inner {
  max-width: 860px;
  text-align: center;
}

.lt-ad-cta h2 {
  color: var(--lt-warm-white);
  font-size: clamp(2rem, 5vw, 3.35rem);
}

.lt-ad-cta p {
  color: rgba(250, 247, 242, 0.86);
  font-family: var(--lt-font-body);
  font-size: 1rem;
  line-height: 1.6;
  margin: 0.85rem auto 0;
  max-width: 42rem;
}

.lt-ad-cta .lt-ad-actions {
  justify-content: center;
}

@media (max-width: 520px) {
  .lt-ad-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .lt-ad-button {
    width: 100%;
  }
}
"""


PRODUCT_AD_PAGES = {
    "missionary_balloon_gift": {
        "slug": "missionary-balloon-gift",
        "route_path": "/missionary-balloon-gift",
        "root_class": "lt-ad-page--missionary",
        "item_code": "large-head-missionary",
        "product_url": "/shop-items/bouquets/large-head-missionary",
        "contact_url": "/contact?intent=missionary-balloon-gift&item=large-head-missionary",
        "final_url": (
            "/missionary-balloon-gift?"
            "utm_source=meta&utm_medium=paid_social&"
            f"utm_campaign={AD_CAMPAIGN_SLUG}&utm_content=missionary_gift_ad_v1"
        ),
        "title": "A larger-than-life missionary balloon gift for the moment everyone photographs.",
        "meta_title": "Missionary Balloon Gift | Locally Twisted",
        "description": (
            "Large-head missionary balloon gift for mission call celebrations, "
            "SLC airport returns, homecomings, open houses, and farewell party photo moments."
        ),
        "eyebrow": "Missionary homecomings, callings, and farewells",
        "lede": (
            "Make the SLC airport pickup, welcome-home porch, open house, mission calling celebration, "
            "or farewell party feel unmistakably special. Choose the missionary style and colors online, "
            "then use checkout for pickup or delivery."
        ),
        "hero_image": "/files/large-head-missionary.png",
        "hero_alt": "Large-head missionary balloon gift with personalized details",
        "hero_caption": "Starts at $175 before delivery and selected options.",
        "primary_label": "Configure Missionary Gift",
        "secondary_label": "Ask a Custom Question",
        "proof": [
            ("From $175", "Clear starting price before delivery and chosen options."),
            ("Personalized look", "Choose Elder or Sister, skin tone, and hair color."),
            ("Photo-ready scale", "A large focal piece for SLC airport pickups, homecomings, open houses, and farewell parties."),
        ],
        "use_heading": "Made for the return, the calling, and the party pictures.",
        "use_lede": (
            "Utah families know these moments get photographed: the first airport hug, the welcome-home porch, "
            "the open house, the mission calling celebration, and the farewell party."
        ),
        "use_cases": [
            {
                "title": "SLC airport return",
                "text": "Bring one big, easy-to-spot photo piece for the welcome-home crowd.",
            },
            {
                "title": "Welcome-home porch or open house",
                "text": "Give the first photos and the family gathering one clear focal point.",
            },
            {
                "title": "Mission calling celebration",
                "text": "Turn the announcement into something bright, personal, and ready for pictures.",
            },
            {
                "title": "Farewell party gift",
                "text": "Give the party table one recognizable centerpiece before the bags are packed.",
            },
        ],
        "gallery_heading": "Personal, recognizable, and easy to celebrate with.",
        "gallery_lede": "Use the product page to choose Elder or Sister, skin tone, hair color, and accents.",
        "gallery": [
            {"image": "/files/large-head-missionary.png", "alt": "Large-head missionary balloon gift", "wide": True},
            {"image": "/files/large-head-missionary--extra-01.png", "alt": "Large-head missionary balloon gift detail", "wide": False},
        ],
        "steps_heading": "How the order works.",
        "steps": [
            {"title": "Choose the missionary style", "text": "Pick Elder or Sister plus skin tone, hair color, and accents."},
            {"title": "Use checkout", "text": "Select pickup or local delivery details during checkout."},
            {"title": "Set the photo moment", "text": "Bring it to the airport pickup, porch welcome, open house, or farewell party."},
        ],
        "cta_title": "Make the missionary moment impossible to miss.",
        "cta_body": "Configure the piece online, or send a question if airport pickup timing, delivery, or personalization needs a quick check.",
        "service_type": "Balloon gift",
    },
}


def get_product_ad_context(context, page_key: str):
    from locally_twisted.seo import business_graph, service_schema

    page = dict(PRODUCT_AD_PAGES[page_key])
    context.title = page["meta_title"]
    context.product_ad_page = page
    context.page_css = PAGE_CSS
    context.metatags = {
        "title": page["meta_title"],
        "description": page["description"],
        "og:title": page["meta_title"],
        "og:description": page["description"],
        "og:type": "website",
    }
    context.structured_data = [
        business_graph(page["route_path"]),
        service_schema(
            page["meta_title"],
            page["description"],
            page["route_path"],
            service_type=page["service_type"],
        ),
    ]
    return context
