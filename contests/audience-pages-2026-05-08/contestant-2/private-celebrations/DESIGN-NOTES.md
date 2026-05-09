# Private Celebrations — Design Notes

## Audience
Birthday parents, wedding planners, baby shower hosts, milestone families, and memorial/celebration-of-life organizers.

## Buyer posture
This is the most emotionally varied audience of the four. A birthday mom wants delight and convenience. A wedding planner wants elegance and coordination. A celebration-of-life organizer is grieving and needs to feel that the vendor will handle this with care, not with a package price.

The brief is explicit: no named-client roster (privacy expectation). Use category-level proof, testimonial phrasing, and anonymized portfolio photos. The page has to prove capability without naming anyone — which means the photography and the honest customer voice carry the weight.

The page's emotional register should be warmer than civic/corporate, but still quiet confidence. Not "we LOVE birthdays!" — that is the wrong frequency. More like: "Private celebrations are personal. Each one is designed from scratch — not from a template package."

## Concept: "Designed for the moment. Made to last in the photos."
The universal private-celebrations truth: the moment passes, the photos last. This is true for birthdays (the photo book stays for years), weddings (albums, obviously), baby showers (those scrapbooks), and celebrations of life (the memorial slideshow with the floral garland in the corner).

The headline names what every private buyer is actually investing in: a beautiful moment that will read well in photographs. This is not about the balloon product. It is about what the balloon does.

## Section decisions

### Hero
- Image: Wedding organic half arch — the most elevated, taste-calibrated image in the portfolio for private celebrations. Immediately signals "this is not a birthday party balloon company from Party City."
- H1: "Designed for the moment. Made to last in the photos." — The emotional proof in one line.
- CTA: "Tell us what you're imagining →" — pulled directly from the approved copy guide. Invites without pushing.

### Celebration type panels (2×2 grid)
- Four types: Birthdays, Weddings, Baby & Bridal Showers, Celebrations of Life.
- 2-column on desktop (even 2+2, no orphan rows).
- Each panel: image → category label → editorial headline → body → optional stat → proof anchor.
- The celebration-of-life panel is handled with the most care: "Something beautiful for a hard day." / "Locally Twisted has walked families through this. It is not a department. It is part of the work." — This is the line that makes a grieving person feel seen.
- The birthday panel shows "300+ birthday installs" — the one stat in the brief that can be used.
- Headline style is more editorial than functional for this page: "The party that felt like you planned it for a year." / "Elegant enough for the photographs. Personal enough for the couple." These are the buyer's interior monologue, not feature claims.
- **Proof anchor per panel (added after Proxy Loop 1-1):** Each panel ends with a short attributed quote fragment drawn from the verified Google reviews — the moment of "this sounds beautiful" is now also the moment of "here's someone who felt it." The testimonials section below still exists for the longer-form voice, but the skeptical first-time buyer hits evidence at the panel level, not two scrolls later. Quotes kept short (one sentence max, first name + event type) so they read as punctuation, not as a second testimonial block.

### "It is not a department. It is part of the work." — Layout Constraint

This sentence in the Celebrations of Life section **must render as an isolated paragraph with no adjacent content on either side.** It cannot appear mid-paragraph, immediately before a list item, or run-on into the next sentence.

If the CMS or Frappe's Rich Text renderer strips surrounding `<p>` tags and collapses adjacent content into one block, this sentence loses its weight entirely. The build instance must enforce the surrounding paragraph breaks — empty `<p>` spacers, a `<br>` pair, or explicit margin — whatever the rendering surface requires. The whitespace is not decoration. It is the mechanism by which the sentence lands.

Do not let implementation simplify this away.

---

### Brass divider (warm white, raw-band)
- Same treatment as civic page — breaks sections visually without adding color.

### Customer voice (stone background)
- Four selected Google review quotes (already verified as real, from the home.py list).
- Quotes chosen for private-occasion specificity: birthday, celebration-of-life, wedding, and the "my go-to for family events" longtime client.
- Attribution: first name + event type only. No last names. No full name.
- 4-column on desktop (even 4), 2-column on tablet, 1-column mobile.
- Clean card format: opening quote mark (brass, decorative) → quote text → attribution.
- Stone background clearly distinct from warm white on either side.

### Trust pillars (navy band)
- Navy separates visually from the stone voice section.
- Heading: "How Locally Twisted handles private events" — doesn't claim to read minds, just states the operating mode.
- Four pillars: Custom Design for Every Event (no template packages), Organic & Premium Builds (signals range), Delivered and Installed (the thing a birthday parent wants — not to touch the balloons), Personal, Start to Finish (direct contact, no middleman).
- The "no template packages" line directly addresses the buyer's fear that they'll get a generic thing.

### Service notes (warm white)
- Heading: "The full range" — simple, honest.
- Lede: "From a hand-delivered birthday bouquet to a full organic garland ceiling" — names the scale extremes.
- Cards use brass-border on all four sides (just a border, no directional accent) — softer, more personal than the left-rule (civic) or top-rule (corporate) treatments.

### Photo gallery (sandstone background)
- Sandstone is warmer than stone — fits the private/personal register.
- Four images: wedding organic arch, floral arch (bridal/shower), birthday Smurfs arch (custom/themed), birthday bouquets (smaller scale, accessible).
- Shows range within the private celebration world.

### Closing CTA (slate blue)
- Slate rather than full navy — warmer than the institutional dark.
- CTA headline: "Tell us what you're imagining." — the exact phrase from the approved copy guide.
- CTA body: "Every private event starts with a conversation — the occasion, the space, and whatever is already in your head. Locally Twisted takes it from there." — The most important thing to say to a private buyer: tell me what's in your head and I'll handle the rest.
- Button CTA: "Start the conversation" — not "Book Now," not "Request a Quote." The lower-friction invitation is appropriate for this emotional category.

## Photo choices
- `wedding-organic-half-arch.webp` — hero + gallery: most elevated/taste-calibrated private image
- `wedding-floral-half-arch.webp` — type panel (showers) + gallery: floral, bridal/shower-appropriate
- `birthday-smurfs-arch.webp` — type panel (birthdays) + gallery: custom themed, memorable
- `birthday-dolphin-backdrop.webp` — type panel (celebration of life): repurposed as "personal celebration" backdrop, clean and themed
- `birthday-balloon-bouquets.webp` — gallery: smaller scale, accessible, everyday private celebration

## Voice decisions
- "Designed for the moment. Made to last in the photos." — photography-truth headline.
- "Tell us what you're imagining." — the guide's own example of the right invitation CTA.
- "It is not a department. It is part of the work." — names the celebration-of-life service without treating grief as a product category.
- "300+ birthday installs" — the one quantified claim the brief supports.
- "No template packages" — names the buyer's fear and resolves it.
- "You don't touch the balloons." — the best way to describe full-service private install. Not "white-glove delivery," just the plain English version.
- "Start the conversation" — softest CTA label of the four pages. Appropriate for the emotional register.
