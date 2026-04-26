#!/usr/bin/env bash
# build_landing_page.sh -- Build LT landing page using Frappe's native Web Page DocType.
#
# Architecture (per system-native rule + GL directive 2026-04-26):
#   - Web Page record (name=locally-twisted, route=home)
#   - content_type = "Page Builder"
#   - page_blocks Table populated with native Web Templates
#   - JSON-LD LocalBusiness schema in the header field
#   - meta_title + meta_description
#   - NO custom Web Templates, NO Jinja overrides, NO !important CSS
#   - Visual styling via existing lt-theme.css (loaded by web_include_css)
#
# Re-running overwrites the homepage to the latest spec.
#
# Usage:  bash scripts/setup/build_landing_page.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER="locally-twisted-erpnext-v15-backend-1"
SITE="frontend"
IMAGES_SRC="${PROJECT_ROOT}/_resources/images"

IMAGES=(
  home-hero.png
  home-service-decor.png
  home-service-twisting.png
  home-service-painting.png
  home-social-proof.png
)

echo "=== Staging images into backend container ==="
for fn in "${IMAGES[@]}"; do
  src="${IMAGES_SRC}/${fn}"
  if [[ ! -f "${src}" ]]; then
    echo "  ! source missing: ${src} -- skipping"
    continue
  fi
  docker cp "${src}" "${CONTAINER}:/tmp/lt-img-${fn}"
  echo "  + staged: ${fn}"
done

echo ""
echo "=== Building landing page via bench execute ==="
docker exec "${CONTAINER}" bash -lc "cd /home/frappe/frappe-bench && bench --site ${SITE} execute locally_twisted.setup_pages.landing.build"

echo ""
echo "=== Clearing website cache ==="
docker exec "${CONTAINER}" bash -lc "cd /home/frappe/frappe-bench && bench --site ${SITE} clear-website-cache"

echo ""
echo "Done. Verify at http://localhost:8081/"
