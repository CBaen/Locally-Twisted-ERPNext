# Design Notes — Corporate Events

## Audience and buyer posture
Marketing teams, brand activation managers, store-opening coordinators, event producers for broadcasters (KSL, KUTV, FOX13), bank community-days staff, and corporate party planners. The buyer often needs:
- Proof that LT is vendor-safe (AP, invoicing, W-9s)
- Confidence in color accuracy for branded installs
- Photographic proof of similar corporate work
- A recognizable roster of Utah companies that trusted them

## Structural choices

### Hero
- Background: `corporate-logo-arch.webp` — the strongest corporate proof photo in the optimized library. Shows a branded arch with clear corporate-entrance context.
- Left-side dark gradient: the corporate buyer expects a clean, professional presentation. Avoided the same deep-navy background as the civic page — used slate blue overlay to give it a different register.
- H1: "On-color, on-brand, on time." — three short promises that map directly to corporate buyer anxiety (brand fidelity, professionalism, reliability). No sticker language.
- CTA: deep navy (quieter than crimson) with brass border — corporate buyers distrust hard-sell crimson CTAs. Hover reveals crimson.

### Photo layout (section 3)
- Featured hero photo (logo arch) left / large, secondary 2×2 grid right. This asymmetric layout differs from the civic page's 2×3 uniform grid and gives the corporate page a more editorial feel.
- Selected photos: corporate-logo-arch (hero), Weberstock branded festival, WSU arch/bouquets, logo arch from Odoo (retail context), IHC latex-free (healthcare corporate context).
- IHC photo specifically called out because latex-free capability is a real corporate differentiator (hospitals, healthcare venues).

### Client roster (section 4)
- Two-column layout on desktop: text intro left / client grid right. This is different from the civic page's full-width grid approach. Feels more like a corporate capabilities presentation.
- 30 clients listed with industry category — organized so the breadth across sectors reads immediately (broadcast, financial, healthcare, hospitality, tech, food).

### Service cards (section 5)
- Four service types specifically chosen to match corporate buyer scenarios:
  - Branded entrances → grand openings, storefronts, lobbies
  - Stage/broadcast backdrops → KSL/KUTV/FOX13 context, conference stages
  - Activation & photo moments → FanX, experiential retail
  - Latex-free → IHC, Mountain Star, healthcare facilities
- Named clients inline in the card descriptions — "FanX has relied on...", "KSL, KUTV, FOX13..." This pattern of proof-inside-service-description is unique to this page.

### AP/Admin trust note (section 6)
- The `lt-corp-trust` section is the page's most audience-specific move. No other audience page needs to address AP processes, W-9 requests, Net-30, or vendor registration. This section exists only because the corporate buyer is often blocked by their accounts payable team's vendor setup requirements.
- Slate-tint background with a brass top rule — visually distinct from the preceding warm-white services section without being another fullbleed dark band.

### CTA (slate, section 7)
- Same slate ground as the hero, giving the page a visual bookend quality.
- Shorter copy than the civic CTA — corporate buyers don't need a list of scenarios; they already know their own event type.

## Container contract
1. Hero — fullbleed
2. Stats — fullbleed (ink)
3. Photos — band (near-white)
4. Roster — fullbleed (navy)
5. Services — band (warm-white)
6. AP trust note — contained (slate-tint)
7. CTA — fullbleed (slate)

Adjacent fullbleed color check:
- Stats (ink) → Photos (near-white): ✅
- Photos (near-white) → Roster (navy): ✅
- Roster (navy) → Services (warm-white): ✅
- Services (warm-white) → AP note (slate-tint): ✅ (contained, not fullbleed)
- AP note (slate-tint) → CTA (slate): ✅ different surface type

## What makes this page feel specifically corporate
1. "AP-ready invoicing" is mentioned twice — once in stats, once in the trust note
2. "Latex-free" is its own service card, with named healthcare clients
3. The hero CTA is navy (quieter), not crimson
4. The roster intro mentions "30 corporate clients" specifically
5. The photo layout is editorial/asymmetric vs the civic uniform grid
6. Client names appear inside service card descriptions — not just in the roster
