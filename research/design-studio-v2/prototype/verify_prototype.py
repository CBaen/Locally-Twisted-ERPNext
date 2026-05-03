from pathlib import Path


ROOT = Path(__file__).resolve().parent

EXPECTED_FILES = [
    "README.md",
    "REVIEW-QA.md",
    "index.html",
    "styles.css",
    "verify_prototype.py",
    "verify_review_grade.js",
    "js/app.js",
    "js/colors.js",
    "js/payload.js",
    "js/renderer-svg.js",
    "js/rules.js",
    "js/state.js",
]

REQUIRED_INDEX_SNIPPETS = [
    'href="./styles.css"',
    'src="./js/app.js"',
    "data-lt-design-studio",
    'data-control="eventContext"',
    'data-control="reviewScenario"',
    'data-control="productFamily"',
    'data-control="design"',
    'data-control="dimension"',
    'data-control="balloonSize"',
    'data-control="densityTier"',
    'data-control="colors"',
    "data-rule-output",
    "data-summary-line",
    "data-review-status",
    "data-preview",
    "data-summary",
    "data-payload-output",
    "Planning visualization. Final design and installation details are confirmed by Locally Twisted.",
    "Classic arch",
    "Classic column",
    "Organic garland",
    "Backdrop wall",
    "Balloon drop",
    "Open review decisions",
]

REQUIRED_RULES_SNIPPETS = [
    "PRODUCT_FAMILIES",
    "source_products",
    "variant_count",
    "classic-arch",
    "classic-column",
    "classic-organic-balloon-garland",
    "balloon-drop",
    "structured_cluster",
    "organic_recipe",
    "drop_mix",
    "BALLOON_SIZES",
    "DENSITY_TIERS",
    "calculateRenderFacts",
    "minimumClusterRepeat",
    "two_color_two_balloon_bands",
    "one_slot_phase_advance",
    "overage_balloon_range",
    "visual_layers",
    "no_touching_twins",
]

REQUIRED_RENDERER_SNIPPETS = [
    "generateStructuredArchBalloons",
    "generateStructuredColumnBalloons",
    "organicPathPoint",
    "primary_structure",
    "massing_clusters",
    "filler_detail",
    "renderOrganicGarland",
    "renderBackdropWall",
    "renderBalloonDrop",
    "visible_render_count",
]

REQUIRED_PAYLOAD_SNIPPETS = [
    "source_products",
    "variant_count",
    "render_engine",
    "estimated_balloons",
    "estimated_clusters",
    "construction_basis",
    "selected_variant_axes",
]

FORBIDDEN_COUPLING = [
    "apps/",
    "apps\\",
    "locally_twisted/locally_twisted/www",
    "locally_twisted\\locally_twisted\\www",
    "web_include_css",
    "web_include_js",
    "website_route_rules",
]

FORBIDDEN_JS = [
    "frappe.call",
    "/api/method",
    "fetch(",
]

FORBIDDEN_PROJECT_STATE_SHORTHAND = [
    "dirty",
]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def fail(message):
    raise SystemExit(message)


def assert_expected_files():
    missing = [relative_path for relative_path in EXPECTED_FILES if not (ROOT / relative_path).is_file()]
    if missing:
        fail("Missing prototype files: " + ", ".join(missing))


def assert_index_contract():
    index = read_text("index.html")
    missing = [snippet for snippet in REQUIRED_INDEX_SNIPPETS if snippet not in index]
    if missing:
        fail("index.html is missing required snippets: " + ", ".join(missing))


def assert_no_forbidden_coupling():
    checked_suffixes = {".html", ".css", ".js", ".md"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in checked_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        normalized = text.lower()
        for forbidden in FORBIDDEN_COUPLING:
            if forbidden.lower() in normalized:
                fail(f"{path.relative_to(ROOT)} references forbidden production coupling: {forbidden}")
        for shorthand in FORBIDDEN_PROJECT_STATE_SHORTHAND:
            if shorthand in normalized.split():
                fail(f"{path.relative_to(ROOT)} uses loaded project-state shorthand: {shorthand}")


def assert_js_has_no_network_or_frappe_calls():
    for path in (ROOT / "js").glob("*.js"):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_JS:
            if forbidden in text:
                fail(f"{path.relative_to(ROOT)} contains forbidden runtime call: {forbidden}")


def assert_product_family_contract():
    checks = [
        ("js/rules.js", REQUIRED_RULES_SNIPPETS),
        ("js/renderer-svg.js", REQUIRED_RENDERER_SNIPPETS),
        ("js/payload.js", REQUIRED_PAYLOAD_SNIPPETS),
    ]
    for relative_path, snippets in checks:
        text = read_text(relative_path)
        missing = [snippet for snippet in snippets if snippet not in text]
        if missing:
            fail(f"{relative_path} is missing product-family contract snippets: " + ", ".join(missing))


def main():
    assert_expected_files()
    assert_index_contract()
    assert_no_forbidden_coupling()
    assert_js_has_no_network_or_frappe_calls()
    assert_product_family_contract()
    print("Design Studio prototype static verification passed.")


if __name__ == "__main__":
    main()
