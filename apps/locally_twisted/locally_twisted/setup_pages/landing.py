"""
Landing page seed for the LT site.

Run via:
    bench --site frontend execute locally_twisted.setup_pages.landing.build

Architecture:
  - One Web Page record (name=locally-twisted, route=home)
  - content_type = "Page Builder"
  - page_blocks Table populated with native Web Templates:
      1. Hero with Right Image
      2. Section with Cards (3 services snapshot)
      3. Section with Cards (1 card — social proof)
      4. Section with CTA (closing)
  - JSON-LD LocalBusiness schema in the header field
  - meta_title + meta_description
  - NO custom Web Templates, NO Jinja overrides, NO !important CSS

Re-running overwrites the homepage to the latest spec.
"""

from __future__ import annotations

import json
import os

import frappe

# Image filenames must already be present at /tmp/lt-img-<filename> (staged by build_landing_page.sh)
IMAGES = {
    "home-hero.png": "LT Homepage Hero",
    "home-service-decor.png": "Balloon Decor Service",
    "home-service-twisting.png": "Balloon Twisting Service",
    "home-service-painting.png": "Face Painting Service",
    "home-social-proof.png": "Trusted by Utah Since 1998",
}


def upload_images() -> None:
    """Upload staged images to ERPNext as public File records."""
    print("\n=== Uploading images ===")
    for filename in IMAGES:
        src_path = f"/tmp/lt-img-{filename}"
        if not os.path.exists(src_path):
            print(f"  ! source missing: {src_path} -- skipping")
            continue
        existing = frappe.db.exists("File", {"file_name": filename, "is_private": 0})
        if existing:
            print(f"  = already uploaded: {filename}")
            continue
        with open(src_path, "rb") as f:
            content = f.read()
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "is_private": 0,
            "content": content,
            "decode": False,
        }).insert(ignore_permissions=True)
        print(f"  + uploaded: {filename} -> {file_doc.file_url}")


def hero_values() -> dict:
    return {
        "title": "Make Your Celebration Unforgettable",
        "subtitle": "Custom balloon decor, twisting, and face painting for events on the Wasatch Front. Crafted by hand. Delivered with care.",
        "image": "/files/home-hero.png",
        "contain_image": 1,
        "primary_action_label": "Browse What We Make",
        "primary_action": "/all-products",
        "secondary_action_label": "Tell Us About Your Event",
        "secondary_action": "/contact",
    }


def services_values() -> dict:
    return {
        "title": "What We Make",
        "subtitle": "Three services. One promise: you get the moment, we handle the magic.",
        "card_size": "Medium",
        "card_1_title": "Balloon Decor",
        "card_1_content": "Arches, garlands, walls, drops. Designed to your color story and installed before guests arrive.",
        "card_1_image": "/files/home-service-decor.png",
        "card_1_url": "/all-products",
        "card_2_title": "Balloon Twisting",
        "card_2_content": "Hours of joyful, hand-twisted creations. Any character, any request. Perfect for parties, fairs, and corporate events.",
        "card_2_image": "/files/home-service-twisting.png",
        "card_2_url": "/balloon-twisting-and-face-painting",
        "card_3_title": "Face Painting",
        "card_3_content": "Professional face painters bringing every imagination to life. Hypoallergenic, FDA-compliant paints.",
        "card_3_image": "/files/home-service-painting.png",
        "card_3_url": "/balloon-twisting-and-face-painting",
    }


def social_values() -> dict:
    # Section with Cards skips a card row whose card_N_title is empty.
    # We use a single card with a brief title + content as our social-proof block.
    return {
        "title": "Trusted by Utah's best since 1998",
        "subtitle": "Twenty-seven years of celebrations across Davis, Weber, Salt Lake, and Utah counties.",
        "card_size": "Large",
        "card_1_title": "From small parties to corporate events",
        "card_1_content": "Hundreds of weddings, birthdays, baby showers, holidays, and corporate events. Every celebration handled with care.",
        "card_1_image": "/files/home-social-proof.png",
        "card_1_url": "/all-products",
    }


def cta_values() -> dict:
    return {
        "title": "Ready to plan something unforgettable?",
        "subtitle": "",
        "cta_label": "Tell Us About Your Event",
        "cta_url": "/contact",
        "cta_description": "Free delivery in Davis, Weber, Salt Lake, and Utah counties. Quick response on every inquiry.",
        "show_confetti": 0,
    }


def jsonld_html() -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "Locally Twisted",
        "image": "https://locallytwisted.com/files/home-hero.png",
        "description": "Custom balloon decor, balloon twisting, and face painting for events on Utah's Wasatch Front.",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "8969 S 2700 W",
            "addressLocality": "West Jordan",
            "addressRegion": "UT",
            "postalCode": "84088",
            "addressCountry": "US",
        },
        "telephone": "+18012850860",
        "email": "hi@locallytwisted.com",
        "url": "https://locallytwisted.com",
        "areaServed": [
            {"@type": "AdministrativeArea", "name": "Davis County, Utah"},
            {"@type": "AdministrativeArea", "name": "Weber County, Utah"},
            {"@type": "AdministrativeArea", "name": "Salt Lake County, Utah"},
            {"@type": "AdministrativeArea", "name": "Utah County, Utah"},
        ],
        "priceRange": "$$",
        "foundingDate": "1998",
    }
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(schema, indent=2)
        + "\n</script>"
    )


def build() -> None:
    """Idempotent landing-page seed. Re-runnable."""
    upload_images()

    print("\n=== Updating Web Page ===")
    page_name = "locally-twisted"
    page = frappe.get_doc("Web Page", page_name)

    page.content_type = "Page Builder"
    page.title = "Locally Twisted - Utah Balloon Decor + Twisting + Face Painting Since 1998"
    page.meta_title = "Locally Twisted | Utah Balloon Decor + Twisting + Face Painting Since 1998"
    page.meta_description = (
        "Custom balloon arches, garlands, walls, drops, balloon twisting, and face painting "
        "for events across Utah's Wasatch Front. Trusted by Utah's best since 1998."
    )
    page.published = 1
    page.show_title = 0
    page.full_width = 1

    page.header = jsonld_html()

    blocks_spec = [
        {"web_template": "Hero with Right Image", "values": hero_values(), "padding": True},
        {"web_template": "Section with Cards", "values": services_values(), "padding": True, "shade": True},
        {"web_template": "Section with Cards", "values": social_values(), "padding": True},
        {"web_template": "Section with CTA", "values": cta_values(), "padding": True, "shade": True},
    ]

    page.page_blocks = []
    for spec in blocks_spec:
        block = page.append("page_blocks", {})
        block.web_template = spec["web_template"]
        block.web_template_values = json.dumps(spec["values"])
        block.add_top_padding = 1 if spec.get("padding") else 0
        block.add_bottom_padding = 1 if spec.get("padding") else 0
        block.add_shade = 1 if spec.get("shade") else 0
        block.add_container = 1

    page.save(ignore_permissions=True)
    frappe.db.commit()

    print(f"\n  Saved Web Page: {page_name}")
    print(f"    content_type:  {page.content_type}")
    print(f"    page_blocks:   {len(page.page_blocks)}")
    print(f"    header schema: {len(page.header)} chars")
    print(f"    meta_title:    {page.meta_title[:80]}")
    print(f"    full_width:    {page.full_width}")
