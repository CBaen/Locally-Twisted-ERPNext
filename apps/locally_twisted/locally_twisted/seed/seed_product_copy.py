"""Seed Quiet Confidence brand copy + plain-language details for all 53 Website Items.

Two-field discipline (GL directive 2026-04-30):
- lt_brand_description — Voice. Present-tense. What it is, the moment it's for.
- lt_product_details   — Specs. What's included, options, format. Brand-true only;
                          no invented dimensions, lead times, or prices.

Voice rules from STYLE-GUIDE.md (Quiet Confidence):
1. Present tense, not promises.
2. Invite, never push.
3. Warm, not performing.
No exclamation points, no all-caps emphasis, no "stunning/amazing/perfect."

Run:
    docker exec locally-twisted-erpnext-v15-backend-1 \\
        bench --site frontend execute \\
        locally_twisted.seed.seed_product_copy.run

Idempotent — overwrites the two fields on every run. The legacy
web_long_description field is left in place; the template's two-field
branch supersedes it when both new fields are populated.
"""

import frappe


COPY = {
    "WEB-ITM-0001": {  # Number Balloon Columns — Columns
        "brand": "<p>Two columns — one tied to the age, the other to the number that says it. The pair frames a doorway, a stage, or a photo wall and tells everyone exactly what they came to celebrate.</p>",
        "details": "<ul><li>Two freestanding columns, each anchored by a large foil number</li><li>Color palette in your hands — share what you have in mind</li><li>Indoor and outdoor friendly</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0002": {  # Graduation Grab n Go — Grab & Go
        "brand": "<p>Two columns in school colors with a graduation-cap topper that does the talking. Anchors the front door for the open house, the photo spot at the family dinner, or the side of the stage at the ceremony.</p>",
        "details": "<ul><li>Pickup-ready set: two columns plus a foil cap topper</li><li>School colors of your choice</li><li>Built ahead and ready to go on your day</li><li>Pickup at our West Jordan location</li></ul>",
    },
    "WEB-ITM-0003": {  # Premium Organic Column — Columns
        "brand": "<p>Balloons up to 24 inches stacked into a single column. The scale makes a difference you feel before you read — a piece that holds the room without trying to.</p>",
        "details": "<ul><li>One freestanding column built from larger latex, up to 24\"</li><li>Custom palette</li><li>Indoor and outdoor capable</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0004": {  # Classic Organic Column — Columns
        "brand": "<p>A freestanding column in the organic balloon style — varied sizes and your colors, blended in a way that feels grown rather than assembled.</p>",
        "details": "<ul><li>One freestanding column, balloons up to 11\"</li><li>Choose your palette</li><li>Indoor and outdoor friendly</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0005": {  # Baby Shower Garland — Garlands
        "brand": "<p>A flowing organic garland in soft tones — the kind of piece that makes a brunch feel like a moment. We design around the theme that fits your story.</p>",
        "details": "<ul><li>One organic garland, sized to your space</li><li>Themes we work with regularly: gender reveal, woodland, safari, classic pastels</li><li>Or whatever you have in mind we haven't done yet</li><li>Hung wherever the photo will happen</li></ul>",
    },
    "WEB-ITM-0006": {  # Unicorn Bouquet — Bouquets
        "brand": "<p>A bouquet built around a unicorn foil — pastels, sparkle, a little bit of magic. Makes its way into birthday photos and memory boxes alike.</p>",
        "details": "<ul><li>Hand-tied bouquet with a unicorn foil topper</li><li>Latex balloons in coordinating pastels</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0007": {  # Mickey Mouse Bouquet — Bouquets
        "brand": "<p>Red, black, and yellow around a Mickey foil — a small thing that lights up the kid who already loves him.</p>",
        "details": "<ul><li>Hand-tied bouquet with a Mickey Mouse foil topper</li><li>Classic Mickey palette</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0008": {  # Minion Bouquet — Bouquets
        "brand": "<p>Yellow, blue, and just enough goggles. The kind of bouquet that earns a real laugh before it earns a thank-you.</p>",
        "details": "<ul><li>Hand-tied bouquet with a Minion foil topper</li><li>Yellow, blue, and white latex</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0009": {  # Encanto Bouquet — Bouquets
        "brand": "<p>Soft pinks, butterflies, and a Mirabel foil — the family the song is about, the way she'd want to be welcomed.</p>",
        "details": "<ul><li>Hand-tied bouquet with an Encanto foil topper</li><li>Pinks, yellows, and accent colors</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0010": {  # Stitch Bouquet — Bouquets
        "brand": "<p>Blue, white, and a little chaos in the best way. For the kid who knows every line.</p>",
        "details": "<ul><li>Hand-tied bouquet with a Stitch foil topper</li><li>Blues, whites, and accent latex</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0011": {  # Flamingo Bouquet — Bouquets
        "brand": "<p>A flamingo foil with pinks and corals around it — beach-day energy in any season.</p>",
        "details": "<ul><li>Hand-tied bouquet with a flamingo foil topper</li><li>Pink and coral palette</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0012": {  # Football Bouquet — Bouquets
        "brand": "<p>A bouquet that knows the score. Built around a football foil with the team colors you actually wear.</p>",
        "details": "<ul><li>Hand-tied bouquet with a football foil topper</li><li>Tell us your team and we'll match the palette</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0013": {  # Soccer Bouquet — Bouquets
        "brand": "<p>Black and white around a soccer-ball foil, with whatever team colors travel with you. The one for the post-game dinner.</p>",
        "details": "<ul><li>Hand-tied bouquet with a soccer-ball foil topper</li><li>Team colors on request</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0014": {  # Over the Hill Bouquet — Bouquets
        "brand": "<p>Black, gray, and the kind of humor that survives every birthday after the round numbers stop sounding fun. Makes the moment lighter.</p>",
        "details": "<ul><li>Hand-tied bouquet with an Over the Hill foil topper</li><li>Black and gray palette with accent colors of your choice</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0015": {  # Space Bouquet — Bouquets
        "brand": "<p>Astronaut-and-rocket foils with deep blues and silvers around them. For the kid who already knows the names of the planets.</p>",
        "details": "<ul><li>Hand-tied bouquet with space-themed foil topper</li><li>Blues, silvers, and accent latex</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0016": {  # 7' Butterfly Column — Columns
        "brand": "<p>A seven-foot column woven through with butterfly accents. Light, almost weightless to look at — the kind of piece that makes someone stop and say <em>oh</em>.</p>",
        "details": "<ul><li>One freestanding seven-foot column with butterfly cutouts integrated</li><li>Color palette in your hands</li><li>Indoor and outdoor friendly</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0017": {  # 7' Epic Column — Columns
        "brand": "<p>A seven-foot column built to be the thing in the room. Large latex, structured spirals, and your colors — done at scale.</p>",
        "details": "<ul><li>One freestanding seven-foot column in the Epic build</li><li>Custom palette</li><li>Indoor and outdoor capable</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0018": {  # Organic Grab n' Go — Grab & Go
        "brand": "<p>A pickup-ready piece in the organic style — varied sizes, soft palette, no setup required on your end. The easy yes.</p>",
        "details": "<ul><li>Pickup-ready organic balloon piece</li><li>Choose your palette</li><li>Built ahead and ready to go on your day</li><li>Pickup at our West Jordan location</li></ul>",
    },
    "WEB-ITM-0019": {  # Easter Balloon Cups — Seasonal & Specialty
        "brand": "<p>Pastel mini-clusters in cup arrangements — small enough for a brunch table, soft enough for a basket, exactly seasonal.</p>",
        "details": "<ul><li>Set of pastel balloon cups</li><li>Easter palette: pinks, lavenders, mints, soft yellows</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0020": {  # Baby Table Decor — Table Decor
        "brand": "<p>A centerpiece in the colors of the shower — soft, hand-built, the kind that fits between the cake and the cards without taking either's place.</p>",
        "details": "<ul><li>One table centerpiece, sized to your table</li><li>Choose pinks, blues, neutrals, or the palette you've already picked</li><li>Indoor use</li><li>Built and delivered to the venue</li></ul>",
    },
    "WEB-ITM-0021": {  # Logo 3 Layered Bouquet — Bouquets
        "brand": "<p>A three-tier bouquet in your brand colors. The detail that turns a corporate event into one people actually remember.</p>",
        "details": "<ul><li>Hand-tied three-layer bouquet</li><li>Your brand palette — share hex codes or a logo and we'll match</li><li>Latex only; foil topper add-on available on request</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0022": {  # Mother's Day front yard 7' Column — Columns
        "brand": "<p>A seven-foot column on the front lawn for Mother's Day morning. Soft palette, balloons that catch the breeze — the kind of welcome that lives in the photo before she's even out of the car.</p>",
        "details": "<ul><li>One freestanding seven-foot column for outdoor placement</li><li>Mother's Day palette — pinks, lavenders, whites — or your colors</li><li>Setup the morning of</li><li>Teardown included</li></ul>",
    },
    "WEB-ITM-0023": {  # Marble Table Decor — Table Decor
        "brand": "<p>A centerpiece with the soft swirl of marble worked into the latex — a quiet luxury that earns a second look.</p>",
        "details": "<ul><li>One table centerpiece in the marble-finish style</li><li>Choose two or three colors and we'll blend them</li><li>Indoor use</li><li>Built and delivered to the venue</li></ul>",
    },
    "WEB-ITM-0024": {  # Paw Patrol Bouquet — Bouquets
        "brand": "<p>A bouquet around a Paw Patrol foil — bright, primary, exactly what the kid asks for by name.</p>",
        "details": "<ul><li>Hand-tied bouquet with a Paw Patrol foil topper</li><li>Reds, blues, yellows in the cast palette</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0025": {  # Elsa Bouquet — Bouquets
        "brand": "<p>Icy blues and whites around an Elsa foil — winter the whole year, for the kid who already knows the words.</p>",
        "details": "<ul><li>Hand-tied bouquet with an Elsa foil topper</li><li>Blues, whites, and silver accents</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0026": {  # Holy COW!! Bouquet — Bouquets
        "brand": "<p>Black, white, and the kind of milestone-birthday humor that earns the laugh before the candles. For the round number nobody saw coming.</p>",
        "details": "<ul><li>Hand-tied bouquet with a milestone foil topper</li><li>Black and white palette with accent colors of your choice</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0027": {  # Butterfly GET WELL — Get-Well Bouquets
        "brand": "<p>A bouquet for the hospital room — butterflies, soft colors, no latex. The kind of small thing that lands in the day someone needs it most.</p>",
        "details": "<ul><li>Hand-tied get-well bouquet with butterfly foil topper</li><li>Foil only — fully latex-free, hospital-safe</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0028": {  # Bandage GET WELL — Get-Well Bouquets
        "brand": "<p>A bandage foil with a smile drawn on, surrounded by foils that earn one back. Fully latex-free for hospital rooms.</p>",
        "details": "<ul><li>Hand-tied get-well bouquet with a bandage foil topper</li><li>Foil only — no latex</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0029": {  # Shooting Star GET WELL — Get-Well Bouquets
        "brand": "<p>A shooting-star foil and the foils that travel with it — bright, hopeful, hospital-safe.</p>",
        "details": "<ul><li>Hand-tied get-well bouquet with a shooting star foil topper</li><li>Foil only — no latex</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0030": {  # 6' Graduation Stands — Stands & Easels
        "brand": "<p>Six-foot stands flanking the photo wall — caps, school colors, names if you want them. The frame the cap-and-gown photos deserve.</p>",
        "details": "<ul><li>Pair of six-foot stands in your school colors</li><li>Caps and accents integrated</li><li>Indoor use only — the base is balloons and will pop on grass or concrete</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0031": {  # Classic organic for easel — Stands & Easels
        "brand": "<p>An organic-style accent built for an easel — for the welcome sign, the seating chart, the memorial photo. The piece that frames the thing the day is about.</p>",
        "details": "<ul><li>One organic balloon accent designed to mount on an easel</li><li>Easel can be provided or yours</li><li>Color palette in your hands</li><li>Indoor use; setup included</li></ul>",
    },
    "WEB-ITM-0032": {  # Mother's Day Bouquet — Bouquets
        "brand": "<p>Soft pinks, lavenders, and whites in a bouquet that says what flowers say — and lasts longer.</p>",
        "details": "<ul><li>Hand-tied Mother's Day bouquet</li><li>Pinks, lavenders, whites — or pick another palette</li><li>Foil topper add-on available on request</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0033": {  # Large Organic Column — Columns
        "brand": "<p>Balloons up to 24 inches stacked into a column. The scale brings presence that a standard column doesn't.</p>",
        "details": "<ul><li>One freestanding column built from larger latex, up to 24\"</li><li>Custom palette</li><li>Indoor and outdoor friendly</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0034": {  # Basketball Arch — Arches
        "brand": "<p>A full-span arch in basketball colors — for the team dinner, the playoff watch party, the senior-night photo wall. Anchors the room exactly where the moment lives.</p>",
        "details": "<ul><li>One full-span balloon arch in your team's palette</li><li>Tell us the colors, we match</li><li>Indoor and outdoor capable</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0035": {  # Baby Shower Combination Photo Op — Table Decor
        "brand": "<p>A garland-and-arch combination built as a photo backdrop. The piece that turns a corner of the room into the corner everyone takes pictures in front of.</p>",
        "details": "<ul><li>Combination piece — garland and arch elements built together</li><li>Custom palette in shower-soft tones or your choice</li><li>Indoor use</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0036": {  # Classic Organic Balloon Garland — Garlands
        "brand": "<p>An organic garland — varied sizes, blended palette, draped along the wall, the table, or the stair rail. The decor staple that makes the rest of the room feel pulled together.</p>",
        "details": "<ul><li>One organic balloon garland, balloons up to 11\"</li><li>Lengths sized to your space</li><li>Choose your palette</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0037": {  # Easter Balloon Arch - Bunny Ear — Arches
        "brand": "<p>Soft pastels and spring greens in a garden-inspired arch with a pair of bunny ears at the apex. Designed for egg hunts, church socials, and family brunches.</p>",
        "details": "<ul><li>One full-span arch with bunny-ear accents</li><li>Pastel palette: pinks, mints, lavenders, soft yellows</li><li>Indoor and outdoor capable</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0038": {  # Halloween Arch — Arches
        "brand": "<p>Orange, black, and purple in an arch that sets the mood. Built for trunk-or-treats, porch displays, and haunted-house entrances.</p>",
        "details": "<ul><li>One full-span Halloween arch</li><li>Standard palette is orange, black, purple — swap or add colors as you like</li><li>Indoor and outdoor capable</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0039": {  # Large Head Missionary — Bouquets
        "brand": "<p>A bouquet for the day someone leaves on a mission — a foil head with the colors and details that match where they're going. A send-off they'll see in every picture.</p>",
        "details": "<ul><li>Hand-tied missionary send-off bouquet with a large foil head topper</li><li>Customize the palette and accents to match the mission</li><li>Pickup or delivered locally</li></ul>",
    },
    "WEB-ITM-0040": {  # Premium Organic Garland — Garlands
        "brand": "<p>Balloons up to 24 inches — bolder, more dramatic. The scale creates depth and dimension that a standard garland can't.</p>",
        "details": "<ul><li>One organic garland built from larger latex, up to 24\"</li><li>Lengths sized to your space</li><li>Choose your palette</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0041": {  # Premium Organic Arch — Arches
        "brand": "<p>Balloons up to 24 inches built into an organic arch. The scale adds depth and dimension that a standard arch doesn't have.</p>",
        "details": "<ul><li>One full-span arch built from larger latex, up to 24\"</li><li>Custom palette</li><li>Indoor and outdoor friendly</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0042": {  # Pride Progress Rainbow Balloon Arch — Arches
        "brand": "<p>Full-spectrum rainbow in a statement arch. Bold, joyful, and built to celebrate exactly who you are.</p>",
        "details": "<ul><li>One full-span arch in the Progress Pride palette</li><li>Indoor and outdoor capable</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0043": {  # Classic Arch — Arches
        "brand": "<p>A full-span arch built by hand, sized to your space, designed around the colors you love. Structured spirals or layered bands — up to four colors, shaped to fit the entrance.</p>",
        "details": "<ul><li>One full-span balloon arch, balloons up to 11\"</li><li>Up to four colors</li><li>Indoor and outdoor capable</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0044": {  # Classic Column — Columns
        "brand": "<p>A freestanding column in classic balloon style — structured, balanced, and built around your palette. The piece that frames the entrance without making it about itself.</p>",
        "details": "<ul><li>One freestanding column, balloons up to 11\"</li><li>Choose your palette</li><li>Indoor and outdoor friendly</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0045": {  # Balloon Drop — Drops
        "brand": "<p>Hundreds of balloons tucked into a net overhead. We build it, you pull the cord, and the room erupts. Made for midnight and the moments that earn the same kind of cheer.</p>",
        "details": "<ul><li>One overhead balloon-drop net, sized to the venue</li><li>Color palette in your hands</li><li>Indoor use</li><li>Includes installation and the release mechanism — your team or ours pulls the cord on cue</li></ul>",
    },
    "WEB-ITM-0046": {  # Classic Organic Arch — Arches
        "brand": "<p>An organic-style arch — balloons up to 11 inches, varied sizes, a palette that feels grown rather than placed. The arch that anchors a wedding aisle, a graduation photo wall, or a backyard party.</p>",
        "details": "<ul><li>One full-span organic arch, balloons up to 11\"</li><li>Custom palette</li><li>Indoor and outdoor friendly</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0047": {  # Birthday Deliveries — Deliveries
        "brand": "<p>A pickup-or-delivery birthday set — balloons, a topper, and a card if you want one — left on the doorstep, the desk, or the dinner table. The little thing that becomes the picture of the day.</p>",
        "details": "<ul><li>Birthday delivery set</li><li>Choose the theme and palette</li><li>Local delivery along the Wasatch Front, or pickup at our West Jordan location</li></ul>",
    },
    "WEB-ITM-0048": {  # Star Column — Columns
        "brand": "<p>A column with star foils integrated — bright, structured, the kind of piece that earns a second look on the way in.</p>",
        "details": "<ul><li>One freestanding column with star foil accents</li><li>Custom palette</li><li>Indoor and outdoor friendly</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0049": {  # Sleepy Baby Column — Columns
        "brand": "<p>A column built around a sleepy-baby topper — soft tones, gentle scale, the welcome a baby shower deserves at the front door.</p>",
        "details": "<ul><li>One freestanding column with a sleepy-baby foil topper</li><li>Soft palette — neutrals, pinks, blues, or your colors</li><li>Indoor use</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0050": {  # 6 color rainbow arch — Arches
        "brand": "<p>A six-color rainbow in a full-span arch — every color of the spectrum, hand-blended, the kind of piece that makes a kid stop walking and stare.</p>",
        "details": "<ul><li>One full-span rainbow arch in six colors</li><li>Indoor and outdoor capable</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0051": {  # Easter Arch — Arches
        "brand": "<p>Soft pastels and spring greens in a garden-inspired arch. Designed for egg hunts, church socials, and family brunches.</p>",
        "details": "<ul><li>One full-span Easter arch in pastel tones — pinks, mints, lavenders, soft yellows</li><li>Indoor and outdoor capable</li><li>Setup and teardown included</li></ul>",
    },
    "WEB-ITM-0052": {  # Large Garland — Garlands
        "brand": "<p>Balloons up to 24 inches — bolder, more dramatic. The scale creates depth and dimension that a standard garland can't.</p>",
        "details": "<ul><li>One organic garland built from larger latex, up to 24\"</li><li>Lengths sized to your space</li><li>Choose your palette</li><li>Setup and teardown by our team</li></ul>",
    },
    "WEB-ITM-0053": {  # Pride Arch — Arches
        "brand": "<p>Full-spectrum rainbow in a statement arch. Bold, joyful, and built to celebrate exactly who you are.</p>",
        "details": "<ul><li>One full-span Pride arch</li><li>Standard rainbow palette or Progress Pride on request</li><li>Indoor and outdoor capable</li><li>Setup and teardown included</li></ul>",
    },
}


def run():
    written = 0
    missing = []
    for code, copy in COPY.items():
        if not frappe.db.exists("Website Item", code):
            missing.append(code)
            continue
        frappe.db.set_value("Website Item", code, {
            "lt_brand_description": copy["brand"],
            "lt_product_details": copy["details"],
        }, update_modified=False)
        written += 1
    frappe.db.commit()
    print(f"[done] wrote copy on {written} Website Items")
    if missing:
        print(f"[warn] {len(missing)} codes in seed not in DB: {missing}")
    expected = frappe.db.count("Website Item")
    if written < expected:
        print(f"[warn] DB has {expected} Website Items but seed only covers {written} — gaps remain")
