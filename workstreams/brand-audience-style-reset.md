# Brand, Audience, and Style Reset

Last updated: 2026-05-02

This workstream is the brand strategy lane for the current ERPNext build. It exists because the current `_resources/STYLE-GUIDE.md` and design artifacts still reflect earlier Claude-era decisions and need to be re-evaluated against Locally Twisted's actual business goals, buyer types, and long-term saleability.

Do not treat this file as final visual direction yet. Treat it as the working surface for the brand reset that will eventually produce a revised style guide.

## Core Brand Rule

Jeff is the business owner and an active source of process knowledge. Jeff is not the brand.

Locally Twisted is the brand.

Customer-facing copy should not make the company dependent on Jeff as the central character, the only expert, or the irreplaceable source of quality. That creates founder-dependent brand risk and makes the business harder to sell later.

Use Jeff's experience as company proof, not as the whole identity.

Prefer:

- "Locally Twisted has 20+ years of balloon decor experience."
- "Our team plans, builds, delivers, and installs balloon decor for Utah events."
- "We bring large-install experience to corporate, school, community, and private events."
- "Our process is built from decades of hands-on event work."

Avoid:

- "Jeff is the magic behind every install."
- "Book Jeff for your event."
- "Jeff personally makes Locally Twisted special."
- "Jeff's balloons are the reason customers trust us."

Allowed:

- Jeff can appear as founder, owner, or background context where useful.
- Jeff can be referenced in internal planning because he is active in the business and this build process.
- Jeff can have a founder note or About-page mention if it supports company trust without making him the whole business.

## Brand Positioning Draft

Locally Twisted should be positioned as Utah's experienced balloon decor company for corporate, institutional, public, and large-scale event installations.

The site should not feel like a small cute party catalog. It should communicate:

- scale
- reliability
- tenure
- logistics
- installation confidence
- visual polish
- local authority
- ability to handle harder versions of the customer's event

Joy and playfulness still matter, but they should come primarily from the balloon work, photography, and service personality. The UI itself should feel professional, confident, and easy to trust.

## Customer Priority Order

Launch brand priority:

1. Professional event planners: corporate, schools, churches, community organizations, venues, and institutions.
2. Big-scale public or event buyers: parades, city events, public installs, large venue activations.
3. Premium private event buyers: weddings, showers, milestone birthdays, upscale home or venue events.
4. Family party buyers: birthdays and smaller kid-focused events.

Balloon twisting and face painting are an exception lane. Those services can speak more directly to family party buyers and premium private events, while still staying organized and professional.

## Authority Pillars

Accepted direction from GL on 2026-05-02:

1. Scale proof: large installs, parades, corporate arches, venue work, and public-facing decor.
2. Client proof: recognizable Utah companies, schools, cities, churches, venues, repeat clients, and community events.
3. Process proof: consultation, planning, design, build, delivery, install, cleanup, and communication.
4. Experience proof: 20+ years in Utah balloon decor, framed as company capability rather than "Jeff is the business."
5. Craft proof: technically correct balloon structures, clean color logic, scale-appropriate builds, and professional install quality.

This should be written as company capability, not founder personality.

## Authority Proof Inventory

Local source inventory checked 2026-05-02:

- Previous-client source: `C:\Users\baenb\projects\locally-twisted-odoo\assets\previous clients.txt`
- Odoo-era image source: `C:\Users\baenb\projects\locally-twisted-odoo\assets\image assets\`
- Current site image source: `_resources/images/`
- Current homepage proof source: `apps/locally_twisted/locally_twisted/www/home.py`
- Shared Drive source: `https://drive.google.com/drive/folders/191Fnz-Eanwpi4rbTFyy08P6ZF8X5NqNz?usp=sharing`
- Public review/search source provided by GL: `https://www.google.com/search?q=Locally+Twisted+Reviews`
- Direct Google review panel link provided by GL: `https://www.google.com/search?q=Locally+Twisted+Reviews#lrd=0x87530f61f6ec2a07:0x271b533c2535be63,1,,,,`

Evidence currently available locally:

- 60 unique previous-client names from the Odoo source list. The raw file has 62 nonblank lines, with duplicate `Ogden city` and `Ogden airport` entries.
- Current homepage client crawl includes high-authority names such as FanX, Chick-fil-A, Ancestry, Zions Bank, America First CU, Utah Jazz, KSL, KUTV, FOX13, University of Utah, Weber State, Intermountain Health, UDOT, SLC Pride, Equality Utah, Ogden City, Sandy City, Herriman City, SLC County, Gallivan Center, Station Park, Museum of Illusion, Young Automotive, Alpine Events, Ogden Airport, Paramount, Shops at Southtown, and Daybreak.
- 191 local Odoo-era image asset files: 172 PNG, 11 JPG, and 8 JPEG.
- Odoo image categories include custom arches, custom columns, deliveries, organic decor, parades, photo opportunities, Pride, themed decor, latex-free decor, helium bouquets, balloon twisting, and face painting.
- Current repo `_resources/images/` includes homepage, contact, BTFP, and product/service imagery already used by the ERPNext build.
- Current homepage controller contains 19 Google-sourced review entries across delivery, event decor, school, corporate, church picnic, ribbon cutting, face painting, BTFP, family events, and other buyer contexts.

Shared Drive inventory checked 2026-05-02:

- Drive folder title: `photos for website`.
- Root listing is publicly readable through Google Drive's embedded folder view.
- 24 top-level folders and 10 top-level image files.
- 26 folders total including root and one nested folder.
- 276 image files counted recursively: 271 PNG, 4 HEIF, and 1 JPEG.
- Largest proof-relevant folders by file count: `standard decor` (51), `themed decor` (46), `Organic decor` (43), `Photo opts` (15), `latex free decor` (15), `deliveries` (12), `Custom arches` (7), `Parades` (7), `Halloween` (7), `custom columns` (6), `Twisting` (4).
- Generated/concept asset caution: root files include `ChatGPT Image...` files and `helium bouquets/Canva generated bouquets` contains 15 files. These can support style exploration or product mockups, but should not be treated as completed-install proof unless GL or Jeff confirms the usage.
- The Drive pass inventoried names and counts only. It did not download originals or visually classify every image.

Public proof sources checked 2026-05-02:

- Google Search itself did not expose a clean review list through the text browser; it redirected without review content. Use the direct Google Business Profile or owner's dashboard before publishing an exact live Google rating/count.
- The direct Google review panel link is the preferred outbound link for any Google review badge/trust chip, even though the text browser still cannot read the modal review contents from Google.
- Playwright browser verification attempted on 2026-05-02. Google redirected the automated browser to an "unusual traffic" page, so Google review modal extraction is not reliable from automated browsing in this environment. Use GL's direct Google pull or the owner's Google Business Profile view as the review-content source.
- Localo public profile reports `4.9` and `115 reviews from Google` for Locally Twisted, with review themes around corporate events, arches, twisting, deliveries, ease of working with the team, and quality. Treat this as a third-party Google-review mirror until confirmed directly in Google.
- GigSalad profile reports `5.0 (13)`, `Top Performer`, 10 photos, balloon twisting/decor services, Wasatch Front coverage, 20+ years of experience, and booked-event history including corporate events, grand openings, nonprofit events, sporting events, festivals, a parade, weddings, and birthday parties.
- Loc8NearMe has a secondary Riverdale listing with recent review excerpts about balloon displays, setup help, delivery, and customer service. Treat this as historical/secondary because the current primary storefront address is West Jordan.
- Legacy `locallytwisted.com` still presents customer-facing category structure and a "Some Of Our Latest Clients" logo strip, including major brands. Logo usage still needs permission review before carrying logos forward.
- GL clarified on 2026-05-02 that the review quotes already added to the current homepage were pulled directly from Google Reviews. Treat those quote entries as direct Google-source material from GL's pull, while still rechecking live rating/count before launch.
- GL provided a fresh direct Google review excerpt on 2026-05-02 showing the Google review count had drifted to 119, with recent reviews from Anne Beedie, Bobbie Weyland, Craig Campbell, Maria Manby, KJSCOTT, and Holly Offret. Themes included same-day delivery, custom party/event decor, helpful customer service, on-time memorial/funeral stand delivery, and setup access for a large Airbnb birthday install.

Localo secondary site checked 2026-05-02:

- URL: `https://locally-twisted.localo.site/`
- Detailed inventory: `workstreams/localo-secondary-site-inventory.md`
- This is a public secondary microsite, not only a review page.
- Localo documentation says `Localo.site` is automatically generated from Google Business Profile data, can be indexed in search, updates from profile changes, is not manually editable, and can be disabled from the Localo panel.
- Live LT Localo site shows `4.9` and `119 reviews from Google`.
- Visible sections include Home, Reviews, Blog, Gallery, Contact, customer reviews, blog posts, contact information, gallery, and social links.
- Visible contact info: `+1 801-644-9312`, `8969 South 2700 West West Jordan 84088`, and limited store hours.
- Social links include Facebook, Instagram, and Twitter/X.
- Localo is not the brand and should not be treated as a customer destination. The ERPNext site is where customers should land.
- It is useful as a photo/review/resource mine and as a possible external review trust reference through `https://locally-twisted.localo.site/reviews`.
- Do not link to the Localo landing page, blog, contact page, or gallery from the ERPNext site.
- Known stale fact: Localo shows Tuesday closed, but Jeff confirmed on 2026-05-02 that Locally Twisted is open on Tuesdays. The Tuesday-closed state was from a short period about a year and a half earlier. Do not reuse Localo hours.
- GL confirmed on 2026-05-02 that Localo is connected to Jeff's marketing company and that the material there is Locally Twisted's to use per contract. Treat this as GL/Jeff-provided contract status, not independent legal review.

Localo handling recommendation:

1. Do not delete/take it down until it has been inventoried.
2. Mine it for review themes, public proof structure, photo candidates, social links, service language, and SEO phrases.
3. Use Localo assets as contract-cleared marketing-company material, but keep a source log and prefer originals from the marketing company, Google Business Profile owner view, Drive, or Jeff's archive.
4. Do not hotlink Localo or Google-hosted image URLs from ERPNext. Copy, optimize, and serve selected assets locally.
5. Do not copy Localo auto-blog copy verbatim into the main site. Treat it as source material and rewrite it into the Locally Twisted brand voice.
6. Do not link to Localo as a site/brand destination. If used publicly, link only to `https://locally-twisted.localo.site/reviews` for multi-site review convergence.
7. Before ERPNext launch, verify whether the Google Business Profile `Website` field points to the real `locallytwisted.com` replacement and not the Localo microsite.
8. After launch, leave Localo live only if it does not compete with the ERPNext storefront and does not publish stale/wrong business facts.

Evidence not fully inventoried yet:

- Live direct Google Business Profile rating/count. The current homepage contains direct Google review quotes from GL's pull, but direct Google should still be checked before making a "current Google rating/review count" claim because counts can drift.
- Exact photo-to-proof mapping. The image folders and Drive folder prove asset availability, but each photo still needs classification by authority pillar before using it in final brand or SEO claims.
- Exact permission/source status for public client logos, third-party review snippets, and non-Localo Google/Drive assets. Localo material is GL/Jeff-confirmed usable per marketing-company contract, but still needs source logging and fact checks before launch use.

Cleanup needed before public/client-proof use:

- Normalize spelling and public names in the previous-client list, for example `Chick- Fil-A`, `Chillies`, `Galivan center`, `IHC`, and similar raw-source entries.
- Decide whether names can be shown as text-only client proof or whether logo/mark usage requires permission.
- Prefer category labels such as "schools," "cities," "financial institutions," "media organizations," and "major Utah venues" when logo permission is uncertain.
- Rewrite review proof so it supports the company brand. Existing review text often names Jeff; public copy can still use the reviews, but page framing should shift the authority back to Locally Twisted and the team.

## Proof Use Rules For The Site

The launch site should use proof in this order:

1. Show real installed work first.
2. Pair the work with buyer-context proof: corporate, public event, venue, school, city, church, family, or delivery.
3. Add recognizable client/category proof where allowed.
4. Add reviews as supporting trust, not as the only proof.
5. Use generated mockups only for concept/product visualization, never as evidence of completed installs.

Homepage proof direction:

- Above the fold: position Locally Twisted as an experienced Utah balloon decor company for event installations, not a small gift catalog.
- First proof band: real installation photos from large-scale or professional contexts, especially arches, columns, organic decor, parades, photo opportunities, and standard/themed decor.
- Client proof: start with text/category proof unless logo permission is confirmed.
- Review proof: use short, sourced review themes around reliability, ease of coordination, install quality, and guest impact. Do not over-center Jeff in the framing even when the original review names him.
- Service proof: let balloon twisting and face painting use family/private-event reviews more heavily than decor pages.
- Count wording: avoid exact Google review counts in durable copy unless verified immediately before launch. Prefer `100+ Google reviews` or `4.9 Google rating` in stable sections; use exact counts only in launch-checked data.

Image source priority:

1. Real photo assets from Drive, Odoo image assets, and current repo images.
2. Current homepage/product images already in the ERPNext build, if they are high quality and not stretched/cropped badly.
3. Generated mockups only for planned products, stylistic consistency, or image gaps where the page clearly needs a representative visual.

Social link visual rule:

- Use recognizable full-color social icons for external social links.
- Avoid monochrome social icons in customer-facing trust areas because they read as generic utilities instead of real destinations.
- Footer and `/contact` social sets updated 2026-05-02 to Facebook, Instagram, and X, matching the current Localo public social links and GL's visual preference. X replaced the old Twitter bird after checking the current brand direction on 2026-05-02.
- Active app social surfaces should be audited together before declaring social icon work complete. Current active surfaces are the shared footer and the `/contact` social block.

Proof that supports higher-value buyers:

- Scale: parades, large arches, custom arches, event entrances, venue/photo-op installs, dense standard/themed decor, and work that clearly shows setup size.
- Reliability: reviews mentioning on-time delivery, easy coordination, setup help, clear communication, and no-drama delivery.
- Authority: client history across companies, cities, schools, financial institutions, media, healthcare, universities, venues, and public/community events.
- Technical craft: clean arches/columns, color discipline, shape consistency, install stability, and scale cues such as doors, vehicles, people, stages, or venue entrances.

Proof that should not lead the brand:

- Single small delivery products.
- One-off novelty items without business-buyer relevance.
- AI-generated or Canva-generated images presented as completed work.
- Founder-only copy that makes customers think the quality depends on one person.

## Reference Site Lessons

Reference sites named by GL:

- Bubblegum Balloons: useful for consistent product/backdrop presentation and a polished catalog feel.
- Balloon Celebrations bouquet page: useful for image discovery, motion, and avoiding a flat wall of identical product cards.
- Balloons by Tommy: useful for professional authority, strong portfolio framing, corporate/private event positioning, gallery entry points, and company-scale proof.

Balloons by Tommy checked 2026-05-02:

- Homepage title positions the company as "Chicago's Leading Balloon Decor Company."
- Meta description leads with decorating Chicagoland since 2000 and names weddings plus corporate gatherings.
- Homepage headings include "Custom balloon decor for every event!", Instagram, "Photo Gallery", and "Video Gallery."
- The homepage links corporate events, photo gallery, video gallery, and booking paths.
- Copy frames the company as experienced in private events, corporate functions, schools/universities, and set-design work.

Lessons to carry into Locally Twisted:

- Lead with company authority and geography, not just product categories.
- Make gallery/portfolio access obvious from the main experience.
- Use image-led sections as proof of capability, not filler.
- Let the site show breadth: corporate events, schools, public/community events, private events, twisting/entertainment, deliveries, and large installations.
- Use social/Instagram freshness if it supports credibility, but do not make social media the only proof surface.
- Keep copy transferable to the company brand. Avoid "one named person is the whole business" framing.

Important difference from the references:

- Locally Twisted's v1 photo quality is uneven, so the site must protect the available photos with better selection, post-production, and layout rules.
- Locally Twisted should not force every proof image into a uniform crop. Use layout rhythm instead of crop sameness.
- Full-piece visibility matters more than card uniformity for arches, columns, organic garlands, photo ops, parade work, and large installs.

## Zurchers And Retail Clarity

GL paused the brand direction on 2026-05-02 because Jeff has referenced Zurchers as a sales model. Treat that as useful business signal, not as final visual direction.

What Zurchers can teach this build:

- Clear category labels help people buy quickly.
- Visible prices and simple add-to-cart behavior matter for ready-to-order products.
- Retail customers need obvious pickup/delivery and product-option confidence.
- A shop page should reduce friction, not turn simple products into a consultation.

What should not carry over:

- Sterile party-store visual language as the main company identity.
- Commodity retail framing for high-value custom event installations.
- UI that makes Locally Twisted feel interchangeable with a party supply store.
- A design system where product cards and price grids are the only proof of business quality.

Decision:

- Use Zurchers-style clarity only inside `Ready to Order` shopping flows.
- Do not make the homepage, gallery, custom decor, or company brand look like Zurchers.
- Use consultative event authority as the main brand posture.
- Keep `Plan Custom Decor` and large-install paths premium, guided, and proof-led.

Working phrase:

> Retail clarity inside an authority-led event brand.

## Accepted Visual Synthesis

Current preferred direction from GL on 2026-05-02:

- Civic/professional Utah authority.
- Slate blue and berry photo-treatment energy.
- Black, deep slate, warm white, and brass/gold professionalism.
- Mountain/territory cues when they support Utah-rooted authority.
- Gold balloon/icon details when they feel polished, not novelty.
- Mentor warmth: experienced, consultative, calm, and capable.

Do not use pastel/rainbow-first UI as the company identity. Balloon colors should come from the work, photos, product choices, and customer palettes. The site chrome should provide confidence, contrast, and structure.

Recommended brand token direction for the next style-guide pass:

| Role | Direction | Notes |
|---|---|---|
| Foundation | ink black, deep slate, warm white | Professional base for corporate/civic buyers |
| Trust accent | muted brass/gold | Use for icons, dividers, proof highlights, and premium CTAs |
| Primary color | deep teal or slate blue | Choose after checking current CSS and image behavior |
| Secondary accent | muted berry | Useful for CTA contrast and event-energy moments |
| Balloon color | comes from photos/products | Avoid turning the UI itself into a pastel/rainbow palette |
| BTFP lane | warmer and more family-friendly | Still organized, not childish |

Segmented design behavior:

- Homepage, gallery, custom decor, corporate, school, civic, and venue pages should feel premium, image-led, consultative, and locally authoritative.
- `Ready to Order` shop pages should be cleaner and more retail-functional: filters, clear prices, option confidence, pickup/delivery clarity, and direct cart behavior.
- Balloon twisting and face painting can be warmer and more family/private-event oriented, while staying visually connected to the main brand.
- `Plan Custom Decor` should eventually feel like a guided planning studio, not a game or checkout page.

## Copy Rules

Use:

- "we"
- "our team"
- "Locally Twisted"
- "our process"
- "our installation experience"
- "our Utah event experience"

Avoid overusing:

- "Jeff"
- "the owner"
- "the artist"
- "one-man"
- "personally"

Use first-person plural because it makes the company feel durable, trainable, transferable, and operationally mature.

## Style Guide Reset Notes

The current `_resources/STYLE-GUIDE.md` should be treated as a useful draft, not the final authority for target customer strategy or color direction.

Before rewriting colors or UI tokens, define:

- target buyer segments
- buying contexts
- decision drivers
- trust signals
- imagery rules
- color personality
- service-lane differences
- reusable design tokens

The likely visual direction is "professional event authority with colorful work," not "party-store color system."

Resolved direction from 2026-05-02: the current pastel-heavy teal/blush/lemon/seafoam/cyan/blue palette should not remain the main company color system. Move toward a more neutral professional base with brass/gold, slate/blue, and restrained berry/deep-teal accents, while letting balloon colors live primarily in photography, product imagery, and customer-selected palettes.
