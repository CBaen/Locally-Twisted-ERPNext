"""SEO, social preview, and structured-data helpers for public pages."""

from __future__ import annotations

from urllib.parse import urlparse

import frappe


SITE_NAME = "Locally Twisted"
BUSINESS_NAME = "Locally Twisted"
PHONE = "+1-801-285-0860"
EMAIL = "hi@locallytwisted.com"

DEFAULT_SOCIAL_IMAGE_PATH = "/assets/locally_twisted/images/heroes/home-generated-lifestyle-desktop.webp"
SOCIAL_IMAGE_PATHS = {
    "/about": "/assets/locally_twisted/images/heroes/about-generated-lifestyle-desktop.webp",
}

CANONICAL_PATH_MAP = {
    "/home": "/",
    "/about-us": "/about",
    "/book": "/contact",
    "/civic_community": "/civic-community",
    "/corporate_events": "/corporate-events",
    "/schools_campuses": "/schools-campuses",
    "/private_celebrations": "/private-celebrations",
    "/event_playground": "/event-playground",
    "/balloon_twisting_and_face_painting": "/balloon-twisting-and-face-painting",
    "/refund_policy": "/refund-policy",
    "/terms_of_service": "/terms-of-service",
    "/thank_you": "/thank-you",
    "/payment_success": "/payment-success",
    "/ready_to_order_paused": "/ready-to-order-paused",
    "/quote_accept": "/quote-accept",
}


def normalize_path(path: str | None) -> str:
    raw = str(path or "/").strip()
    if "://" in raw:
        raw = urlparse(raw).path or "/"
    raw = raw.split("?", 1)[0].split("#", 1)[0]
    if not raw.startswith("/"):
        raw = f"/{raw}"
    if len(raw) > 1:
        raw = raw.rstrip("/")
    return raw or "/"


def canonical_path(path: str | None) -> str:
    normalized = normalize_path(path)
    return CANONICAL_PATH_MAP.get(normalized, normalized)


def site_base_url() -> str:
    configured = str(frappe.utils.get_url() or "").rstrip("/")
    request = getattr(frappe.local, "request", None)
    if request and getattr(request, "host_url", None):
        request_base = str(request.host_url).rstrip("/")
        request_url = urlparse(request_base)
        configured_url = urlparse(configured)
        if (
            configured
            and request_url.hostname == configured_url.hostname
            and configured_url.port
            and not request_url.port
        ):
            return configured
        return request_base
    if configured:
        return configured
    return ""


def absolute_url(path: str | None = "/") -> str:
    normalized = normalize_path(path)
    base = site_base_url()
    if normalized == "/":
        return f"{base}/"
    return f"{base}{normalized}"


def request_path() -> str:
    request = getattr(frappe.local, "request", None)
    if request and getattr(request, "path", None):
        return normalize_path(request.path)
    return normalize_path(getattr(frappe.local, "request_path", "/"))


def social_image_path(path: str | None = None) -> str:
    page_path = canonical_path(path or request_path())
    return SOCIAL_IMAGE_PATHS.get(page_path, DEFAULT_SOCIAL_IMAGE_PATH)


def apply_seo_context(context):
    page_path = canonical_path(request_path())
    image_path = social_image_path(page_path)
    context["lt_canonical_url"] = absolute_url(page_path)
    context["lt_social_image_url"] = absolute_url(image_path)
    context["lt_og_url"] = absolute_url(page_path)
    context["lt_site_name"] = SITE_NAME
    context["lt_twitter_card"] = "summary_large_image"
    metatags = context.get("metatags") or {}
    metatags["twitter:card"] = "summary_large_image"
    context["metatags"] = metatags
    return context


def _area_served() -> list[dict[str, str]]:
    return [
        {"@type": "Place", "name": "Wasatch Front"},
        {"@type": "Place", "name": "Utah"},
        {"@type": "City", "name": "West Jordan"},
        {"@type": "City", "name": "Riverdale"},
    ]


def _address() -> dict[str, str]:
    return {
        "@type": "PostalAddress",
        "streetAddress": "8969 S 2700 W",
        "addressLocality": "West Jordan",
        "addressRegion": "UT",
        "postalCode": "84088",
        "addressCountry": "US",
    }


def organization_schema() -> dict:
    return {
        "@type": "Organization",
        "@id": f"{absolute_url('/')}#organization",
        "name": BUSINESS_NAME,
        "url": absolute_url("/"),
        "logo": absolute_url("/assets/locally_twisted/icons/lt-logo.png"),
        "image": absolute_url(DEFAULT_SOCIAL_IMAGE_PATH),
        "telephone": PHONE,
        "email": EMAIL,
        "address": _address(),
        "areaServed": _area_served(),
        "description": (
            "Utah balloon company creating custom balloon decor, event installations, "
            "balloon twisting, and face painting for Wasatch Front events."
        ),
    }


def local_business_schema(page_path: str = "/") -> dict:
    return {
        "@type": "LocalBusiness",
        "@id": f"{absolute_url('/')}#localbusiness",
        "name": BUSINESS_NAME,
        "url": absolute_url(page_path),
        "image": absolute_url(social_image_path(page_path)),
        "telephone": PHONE,
        "email": EMAIL,
        "address": _address(),
        "areaServed": _area_served(),
        "parentOrganization": {"@id": f"{absolute_url('/')}#organization"},
        "description": (
            "Custom balloon decor, delivery and installation support, balloon twisting, "
            "and face painting for corporate, school, civic, and private Utah events."
        ),
    }


def business_graph(page_path: str = "/") -> dict:
    return {
        "@context": "https://schema.org",
        "@graph": [
            organization_schema(),
            local_business_schema(page_path),
        ],
    }


def service_schema(
    name: str,
    description: str,
    page_path: str,
    service_type: str = "Balloon decor",
) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": f"{absolute_url(page_path)}#service",
        "name": name,
        "description": description,
        "serviceType": service_type,
        "url": absolute_url(page_path),
        "provider": {
            "@type": "LocalBusiness",
            "@id": f"{absolute_url('/')}#localbusiness",
            "name": BUSINESS_NAME,
            "url": absolute_url("/"),
        },
        "areaServed": _area_served(),
    }


def faq_schema(questions: list[dict[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                },
            }
            for item in questions
        ],
    }
