"""Rollback-safe live contract for LT Product Blueprint records."""

from __future__ import annotations

import json

import frappe

from locally_twisted.product_blueprint_local_apply import (
    LOCAL_APPLY_CONFIRMATION,
    ProductBlueprintApplyError,
    apply_blueprint_locally,
    _route_for,
)
from locally_twisted.product_options import get_checkout_add_on_options
from locally_twisted.product_page_runtime import CONFIG_VERSION, sales_order_add_on_lines
from locally_twisted.locally_twisted.doctype.lt_product_blueprint.lt_product_blueprint import (
    apply_locally_from_desk,
    get_local_apply_preview,
)


class ContractFail(Exception):
    pass


GUARD_DOCTYPES = (
    "Item",
    "Website Item",
    "Item Price",
    "Item Attribute",
    "Website Slideshow",
    "Website Slideshow Item",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
)
BLUEPRINT_DOCTYPES = (
    "LT Product Blueprint",
    "LT Product Blueprint Option",
    "LT Product Blueprint Color Recipe",
    "LT Product Blueprint Add On",
    "LT Product Blueprint Conditional Price",
    "LT Product Blueprint Media Rule",
    "LT Product Blueprint Gallery Image",
    "LT Product Blueprint Content Rule",
)
OWNER_USER = "locallytwisted@gmail.com"


def run() -> dict[str, object]:
    original_commit = frappe.db.commit

    def no_commit(*args, **kwargs):
        return None

    try:
        frappe.db.commit = no_commit
        initial_counts = _counts()
        result = _run_contract()
        frappe.db.rollback()
        rollback_counts = _counts()
        if rollback_counts != initial_counts:
            changed = {
                doctype: {"before": initial_counts[doctype], "after": rollback_counts[doctype]}
                for doctype in GUARD_DOCTYPES
                if initial_counts.get(doctype) != rollback_counts.get(doctype)
            }
            raise ContractFail(f"Rollback did not restore product blueprint guard counts: {changed}")
        result["rolled_back"] = True
        result["rollback_guard_counts_unchanged"] = True
        return result
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.commit = original_commit
        frappe.db.rollback()


def _run_contract() -> dict[str, object]:
    _assert_doctypes_exist()
    before = _counts()
    doc = _insert_valid_quote_first_blueprint()
    _assert_validation_evidence(doc)
    staff_result = _assert_item_manager_staff_setup_flow()
    _assert_live_approval_blocks()
    _assert_preview_with_blockers_blocks()
    _assert_visible_shop_requires_customer_image()
    _assert_exact_price_rows_stay_in_product_family()
    after = _counts()
    _assert_no_business_mutation(before, after)
    apply_result = _assert_guarded_local_apply()
    existing_visibility_result = _assert_local_apply_preserves_existing_public_visibility()
    role_apply_result = _assert_product_create_role_apply_boundaries()
    owner_result = _assert_owner_profile_product_build_flow()
    complex_media_result = _assert_complex_variant_media_checkout_flow()
    return {
        "ok": True,
        "blueprint": doc.name,
        "validation_status": doc.validation_status,
        "staff_setup": staff_result,
        "role_apply": role_apply_result,
        "owner_setup": owner_result,
        "complex_variant_media": complex_media_result,
        "save_only_guard_counts_unchanged": True,
        "local_apply": apply_result,
        "existing_visibility": existing_visibility_result,
    }


def _assert_doctypes_exist() -> None:
    missing = [doctype for doctype in BLUEPRINT_DOCTYPES if not frappe.db.exists("DocType", doctype)]
    if missing:
        raise ContractFail(f"Missing product blueprint DocTypes after migrate: {missing}")


def _product_blueprint_create_roles() -> set[str]:
    meta = frappe.get_meta("LT Product Blueprint")
    return {
        row.role
        for row in meta.permissions or []
        if getattr(row, "create", 0) and getattr(row, "role", None)
    }


def _insert_valid_quote_first_blueprint():
    doc = frappe.get_doc(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "Contract Product Blueprint",
            "product_slug": "contract-product-blueprint",
            "item_group": _first_leaf_item_group(),
            "page_template": "Configurable product page",
            "buying_path": "Quote first",
            "publish_status": "Draft",
            "base_price": 0,
            "option_rows": [
                {
                    "axis_name": "Design",
                    "role": "Review only",
                    "values": "Swirl\nLayered",
                }
            ],
            "color_recipe_rows": [
                {
                    "recipe_name": "Main balloon colors",
                    "min_colors": 1,
                    "max_colors": 4,
                    "palette_source": "Operator review",
                }
            ],
            "conditional_price_rows": [
                {
                    "condition_label": "Large install",
                    "applies_when": "Customer needs a venue-scale install",
                    "price_behavior": "Quote only",
                }
            ],
        }
    ).insert(ignore_permissions=True)
    return doc


def _assert_validation_evidence(doc) -> None:
    if doc.validation_status != "Ready For Local Preview":
        raise ContractFail(f"Expected local preview status, found {doc.validation_status}: {doc.validation_summary}")
    if doc.ready_for_live:
        raise ContractFail("Blueprint marked ready_for_live even though live publishing is disabled.")
    if doc.target_item_code or doc.target_website_item:
        raise ContractFail("Blueprint save should not create or link ERPNext product target records.")
    payload = json.loads(doc.validation_json or "{}")
    apply_plan = json.loads(doc.apply_plan_json or "{}")
    if payload.get("contract", {}).get("commerce_lane") != "quote_first":
        raise ContractFail(f"Blueprint validation lost quote-first lane: {payload}")
    targets = payload.get("contract", {}).get("payload_target_counts") or {}
    if targets.get("quote_context") != 1:
        raise ContractFail(f"Blueprint validation did not route review-only option to quote_context: {targets}")
    if apply_plan.get("dry_run") is not True or apply_plan.get("writes_enabled") is not False:
        raise ContractFail(f"Blueprint apply plan is not a no-write dry run: {apply_plan}")
    if apply_plan.get("planned_records", {}).get("website_item", {}).get("published") != 0:
        raise ContractFail(f"Blueprint apply plan should keep Website Item unpublished: {apply_plan}")
    if apply_plan.get("planned_records", {}).get("item_prices"):
        raise ContractFail(f"Quote-first blueprint should not plan checkout Item Price rows: {apply_plan}")


def _assert_live_approval_blocks() -> None:
    error = _insert_expect_error(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "Unsafe Live Approval Blueprint",
            "product_slug": "unsafe-live-approval-blueprint",
            "item_group": _first_leaf_item_group(),
            "page_template": "Ready-to-order page",
            "buying_path": "Direct checkout",
            "publish_status": "Approved For Live",
            "base_price": 35,
        }
    )
    if "Live approval is not available" not in error:
        raise ContractFail(f"Live approval failure did not explain the live gate: {error}")


def _assert_preview_with_blockers_blocks() -> None:
    error = _insert_expect_error(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "Blocked Preview Blueprint",
            "product_slug": "Blocked Preview Slug",
            "item_group": _first_leaf_item_group(),
            "page_template": "Ready-to-order page",
            "buying_path": "Direct checkout",
            "publish_status": "Local Preview Ready",
        }
    )
    if "cannot move to preview/staging" not in error:
        raise ContractFail(f"Blocked preview failure did not explain the preview gate: {error}")


def _assert_visible_shop_requires_customer_image() -> None:
    error = _insert_expect_error(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "Visible Missing Image Blueprint",
            "product_slug": "visible-missing-image-blueprint",
            "item_group": _first_leaf_item_group(),
            "page_template": "Ready-to-order page",
            "buying_path": "Direct checkout",
            "publish_status": "Draft",
            "shop_visibility": "Visible in shop",
            "base_price": 35,
        }
    )
    if "fallback/main product photo" not in error:
        raise ContractFail(f"Visible product image guard did not fail loudly: {error}")


def _assert_exact_price_rows_stay_in_product_family() -> None:
    slug = "cross-product-price-blueprint"
    unrelated_item = _first_unrelated_item(slug)
    error = _insert_expect_error(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "Cross Product Price Blueprint",
            "product_slug": slug,
            "item_group": _first_leaf_item_group(),
            "page_template": "Ready-to-order page",
            "buying_path": "Direct checkout",
            "publish_status": "Draft",
            "base_price": 0,
            "price_rows": [
                {
                    "item_code": unrelated_item,
                    "price": 99,
                    "enabled_for_checkout": 1,
                }
            ],
        }
    )
    if "must belong to this Product Setup" not in error:
        raise ContractFail(f"Cross-product price guard did not fail loudly: {error}")


def _assert_guarded_local_apply() -> dict[str, object]:
    suffix = frappe.generate_hash(length=8).lower()
    slug = f"contract-local-apply-{suffix}"
    axis = f"Contract Size {suffix}"
    add_on_item = _insert_support_add_on_item(suffix)
    before = _counts()
    doc = frappe.get_doc(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "Contract Local Apply Blueprint",
            "product_slug": slug,
            "item_group": _first_leaf_item_group(),
            "page_template": "Ready-to-order page",
            "buying_path": "Direct checkout",
            "publish_status": "Draft",
            "shop_visibility": "Visible in shop",
            "base_price": 42,
            "product_summary": "Rollback-safe local apply contract product.",
            "primary_image": f"/files/{slug}-default.png",
            "option_rows": [
                {
                    "axis_name": axis,
                    "role": "Sale unit option",
                    "values": "Desk Small\nDesk Large",
                }
            ],
            "add_on_rows": [
                {
                    "add_on_name": "Contract sparkle upgrade",
                    "add_on_item": add_on_item,
                    "price_source": "Fixed Item Price",
                    "checkout_approved": 1,
                    "quantity_min": 0,
                    "quantity_max": 3,
                }
            ],
        }
    ).insert(ignore_permissions=True)

    _assert_desk_preview_guest_blocks(doc)
    preview = get_local_apply_preview(doc.name)
    if not preview.get("ok") or preview.get("writes_enabled"):
        raise ContractFail(f"Desk local apply preview should be no-write and ready: {preview}")
    if preview.get("planned_counts", {}).get("item_variants") != 2:
        raise ContractFail(f"Desk local apply preview did not count variants: {preview}")

    try:
        apply_blueprint_locally(doc)
    except ProductBlueprintApplyError as exc:
        message = str(exc)
    else:
        raise ContractFail("Local blueprint apply succeeded without explicit write confirmation.")
    if LOCAL_APPLY_CONFIRMATION not in message or "allow_writes=True" not in message:
        raise ContractFail(f"Local apply guard did not explain the explicit write gate: {message}")

    with _temporary_conf_flag("lt_allow_local_blueprint_apply", 0):
        disabled_error = _call_expect_error(lambda: apply_locally_from_desk(doc.name))
    if "Local product apply is disabled" not in disabled_error:
        raise ContractFail(f"Desk apply without local site flag did not fail loudly: {disabled_error}")

    with _temporary_conf_flag("lt_allow_local_blueprint_apply", 1):
        result = apply_locally_from_desk(doc.name)
    if not result.get("ok"):
        raise ContractFail(f"Local apply did not return ok: {result}")

    _assert_local_apply_records(doc, result, slug, axis)
    _assert_dynamic_blueprint_add_on(slug, add_on_item)
    after = _counts()
    _assert_expected_local_apply_delta(before, after)
    return {
        "item_code": result["item_code"],
        "website_item": result["website_item"],
        "variant_count": len(result.get("variants") or []),
        "item_price_count": len(result.get("item_prices") or []),
        "published": result.get("website_item_published"),
        "dynamic_add_on_checked": True,
    }


def _assert_item_manager_staff_setup_flow() -> dict[str, object]:
    suffix = frappe.generate_hash(length=8).lower()
    user = _insert_item_manager_user(suffix)
    current_user = frappe.session.user
    try:
        frappe.set_user(user)
        product_slug = f"staff-setup-proof-{suffix}"
        doc = frappe.get_doc(
            {
                "doctype": "LT Product Blueprint",
                "product_name": "Staff Setup Proof",
                "product_slug": product_slug,
                "item_group": _first_leaf_item_group(),
                "page_template": "Ready-to-order page",
                "buying_path": "Direct checkout",
                "publish_status": "Draft",
                "base_price": 35,
                "option_rows": [
                    {
                        "axis_name": "Proof Size",
                        "selection_behavior": "SKU-defining variant",
                        "control_type": "Single select",
                        "required": 1,
                        "values": "Small\nLarge",
                    },
                    {
                        "axis_name": "Design Choices",
                        "selection_behavior": "Configuration only",
                        "control_type": "Multi select",
                        "required": 0,
                        "min_selections": 0,
                        "max_selections": 9,
                        "values": "\n".join(f"Choice {idx:02d}" for idx in range(1, 61)),
                    },
                ],
                "media_rule_rows": [
                    {
                        "rule_name": "Choice media proof",
                        "rule_type": "Selection group",
                        "selection_group": "Design Choices",
                        "selection_value": "Choice 01",
                        "image": "/files/staff-setup-media-proof.png",
                        "approved_for_customer": 1,
                    }
                ],
            }
        ).insert()

        if doc.owner != user:
            raise ContractFail(f"Staff-created Product Setup owner should be the staff user, found {doc.owner}.")
        if doc.validation_status != "Ready For Local Preview":
            raise ContractFail(f"Staff setup should validate for local preview: {doc.validation_summary}")
        apply_plan = json.loads(doc.apply_plan_json or "{}")
        setup_schema = (apply_plan.get("planned_records") or {}).get("product_setup_schema") or {}
        generation = setup_schema.get("generation") or {}
        if generation.get("variant_combination_count") != 2:
            raise ContractFail(f"Staff setup should create only SKU-defining variants: {generation}")
        if generation.get("configuration_only_group_count") != 1:
            raise ContractFail(f"Staff setup should preserve one configuration-only group: {generation}")
        groups = {group.get("key"): group for group in setup_schema.get("selection_groups") or []}
        design_group = groups.get("design-choices") or {}
        if design_group.get("max_selections") != 9 or len(design_group.get("values") or []) != 60:
            raise ContractFail(f"Staff high-cardinality group was not preserved: {design_group}")
        if not setup_schema.get("media_rules"):
            raise ContractFail("Staff setup media rule was not present in the Product Setup schema.")

        preview = get_local_apply_preview(doc.name)
        if not preview.get("ok") or preview.get("writes_enabled"):
            raise ContractFail(f"Staff Desk preview should be readable and no-write: {preview}")
        return {
            "user": user,
            "blueprint": doc.name,
            "variant_combination_count": generation.get("variant_combination_count"),
            "configuration_choice_count": len(design_group.get("values") or []),
            "configuration_max": design_group.get("max_selections"),
            "media_rules": len(setup_schema.get("media_rules") or []),
        }
    finally:
        frappe.set_user(current_user)


def _insert_item_manager_user(suffix: str) -> str:
    return _insert_role_user(suffix, "Item Manager")


def _insert_role_user(suffix: str, role: str) -> str:
    email = f"lt-product-setup-{suffix}@example.invalid"
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": "Product",
            "last_name": "Setup Proof",
            "enabled": 1,
            "send_welcome_email": 0,
            "roles": [{"role": role}],
        }
    )
    user.insert(ignore_permissions=True)
    return email


def _assert_product_create_role_apply_boundaries() -> dict[str, object]:
    create_roles = _product_blueprint_create_roles()
    expected_roles = {"Item Manager", "System Manager"}
    if not expected_roles.issubset(create_roles):
        raise ContractFail(f"Product Setup create roles should include {expected_roles}, found {create_roles}")

    results = []
    for role in sorted(expected_roles):
        suffix = frappe.generate_hash(length=8).lower()
        user = _insert_role_user(suffix, role)
        current_user = frappe.session.user
        slug = f"{role.lower().replace(' ', '-')}-apply-proof-{suffix}"
        axis = f"{role} Proof Size {suffix}"
        try:
            frappe.set_user(user)
            doc = frappe.get_doc(
                {
                    "doctype": "LT Product Blueprint",
                    "product_name": f"{role} Apply Proof",
                    "product_slug": slug,
                    "item_group": _first_leaf_item_group(),
                    "page_template": "Ready-to-order page",
                    "buying_path": "Direct checkout",
                    "publish_status": "Draft",
                    "base_price": 45,
                    "option_rows": [
                        {
                            "axis_name": axis,
                            "selection_behavior": "SKU-defining variant",
                            "control_type": "Single select",
                            "required": 1,
                            "min_selections": 1,
                            "max_selections": 1,
                            "values": "Small\nLarge",
                        }
                    ],
                }
            ).insert()
            with _temporary_conf_flag("lt_allow_local_blueprint_apply", 1):
                result = apply_locally_from_desk(doc.name)
            if len(result.get("variants") or []) != 2 or len(result.get("item_prices") or []) != 2:
                raise ContractFail(f"{role} apply should create two priced variants, found {result}")
            results.append(
                {
                    "role": role,
                    "user": user,
                    "variant_count": 2,
                    "published": result.get("website_item_published"),
                }
            )
        finally:
            frappe.set_user(current_user)

    return {"create_roles": sorted(create_roles), "applied_roles": results}


def _assert_owner_profile_product_build_flow() -> dict[str, object]:
    if not frappe.db.exists("User", OWNER_USER):
        raise ContractFail(f"Owner product setup user does not exist: {OWNER_USER}")

    suffix = frappe.generate_hash(length=8).lower()
    slug = f"owner-profile-build-{suffix}"
    axis = f"Owner Proof Size {suffix}"
    current_user = frappe.session.user
    try:
        frappe.set_user(OWNER_USER)
        doc = frappe.get_doc(
            {
                "doctype": "LT Product Blueprint",
                "product_name": "Owner Profile Product Build Proof",
                "product_slug": slug,
                "item_group": _first_leaf_item_group(),
                "page_template": "Ready-to-order page",
                "buying_path": "Direct checkout",
                "publish_status": "Draft",
                "base_price": 55,
                "product_summary": "Rollback-safe owner-profile Product Setup proof.",
                "product_story": "<p>Default owner story.</p>",
                "product_details": "<p>Default owner details.</p>",
                "primary_image": "/files/owner-product-default.png",
                "option_rows": [
                    {
                        "axis_name": axis,
                        "selection_behavior": "SKU-defining variant",
                        "control_type": "Single select",
                        "required": 1,
                        "min_selections": 1,
                        "max_selections": 1,
                        "values": "Small\nLarge",
                    },
                    {
                        "axis_name": "Owner Style Notes",
                        "selection_behavior": "Configuration only",
                        "control_type": "Multi select",
                        "required": 0,
                        "min_selections": 0,
                        "max_selections": 2,
                        "values": "Classic\nBright\nSoft",
                    },
                ],
                "media_rule_rows": [
                    {
                        "rule_name": "Owner proof media",
                        "rule_type": "Selection group",
                        "selection_group": axis,
                        "selection_value": "Small",
                        "image": "/files/owner-product-setup-proof.png",
                        "approved_for_customer": 1,
                    }
                ],
                "gallery_image_rows": [
                    {
                        "image": "/files/owner-gallery-one.png",
                        "heading": "Owner gallery one",
                        "approved_for_customer": 1,
                    },
                    {
                        "image": "/files/owner-gallery-two.png",
                        "heading": "Owner gallery two",
                        "approved_for_customer": 1,
                    },
                ],
                "content_rule_rows": [
                    {
                        "rule_name": "Large owner copy",
                        "rule_type": "Selection group",
                        "selection_group": axis,
                        "selection_value": "Large",
                        "display_title": "Owner Large Proof Title",
                        "product_story": "<p>Large owner story.</p>",
                        "product_details": "<p>Large owner details.</p>",
                        "approved_for_customer": 1,
                    }
                ],
            }
        ).insert()

        if doc.owner != OWNER_USER:
            raise ContractFail(f"Owner Product Setup record should be owned by {OWNER_USER}, found {doc.owner}.")
        if doc.validation_status != "Ready For Local Preview":
            raise ContractFail(f"Owner Product Setup should validate for local preview: {doc.validation_summary}")

        preview = get_local_apply_preview(doc.name)
        if not preview.get("ok") or preview.get("writes_enabled"):
            raise ContractFail(f"Owner Desk preview should be readable and no-write: {preview}")
        if preview.get("planned_counts", {}).get("item_variants") != 2:
            raise ContractFail(f"Owner preview did not preserve two SKU variants: {preview}")
        _assert_owner_media_content_schema(doc, axis)

        with _temporary_conf_flag("lt_allow_local_blueprint_apply", 1):
            result = apply_locally_from_desk(doc.name)
        if not result.get("ok"):
            raise ContractFail(f"Owner local apply did not return ok: {result}")

        _assert_local_apply_records(doc, result, slug, axis)
        _assert_owner_gallery_records(result)
        return {
            "user": OWNER_USER,
            "blueprint": doc.name,
            "item_code": result.get("item_code"),
            "website_item": result.get("website_item"),
            "variant_count": len(result.get("variants") or []),
            "item_price_count": len(result.get("item_prices") or []),
            "gallery_image_count": (result.get("gallery") or {}).get("image_count"),
            "published": result.get("website_item_published"),
        }
    finally:
        frappe.set_user(current_user)


def _assert_owner_media_content_schema(doc, axis: str) -> None:
    from locally_twisted.product_setup_runtime import (
        build_product_setup_schema_doc,
        resolve_product_setup_content,
    )

    schema = build_product_setup_schema_doc(doc)
    if len(schema.get("gallery_images") or []) != 2:
        raise ContractFail(f"Owner Product Setup schema lost gallery images: {schema}")
    if len(schema.get("content_rules") or []) != 1:
        raise ContractFail(f"Owner Product Setup schema lost content rules: {schema}")
    selected = resolve_product_setup_content(
        schema,
        variant_item_code="",
        configuration={"selected_options": {axis: "Large"}},
    )
    if selected.get("display_title") != "Owner Large Proof Title":
        raise ContractFail(f"Owner selected content rule did not resolve: {selected}")


def _assert_owner_gallery_records(result: dict[str, object]) -> None:
    gallery = result.get("gallery") or {}
    if gallery.get("image_count") != 2 or not gallery.get("slideshow"):
        raise ContractFail(f"Owner local apply did not create the product gallery: {result}")
    slideshow = frappe.get_doc("Website Slideshow", gallery["slideshow"])
    images = [row.image for row in slideshow.slideshow_items or []]
    if images != ["/files/owner-gallery-one.png", "/files/owner-gallery-two.png"]:
        raise ContractFail(f"Owner Website Slideshow images drifted: {images}")
    linked = frappe.db.get_value("Website Item", result["website_item"], "slideshow")
    if linked != slideshow.name:
        raise ContractFail(f"Owner Website Item did not link the slideshow: {linked}")


def _assert_complex_variant_media_checkout_flow() -> dict[str, object]:
    """Prove Product Setup media choices survive from selection to checkout."""
    suffix = frappe.generate_hash(length=8).lower()
    slug = f"complex-media-proof-{suffix}"
    size_axis = "Proof Size"
    finish_axis = "Proof Finish"
    stand_axis = "Proof Stand"
    combo_image = f"/files/{slug}-large-chrome.png"
    size_image = f"/files/{slug}-small.png"
    fallback_image = f"/files/{slug}-fallback.png"
    combo_title = "Large Chrome Proof Title"

    doc = frappe.get_doc(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "Complex Variant Media Proof",
            "product_slug": slug,
            "item_group": _first_leaf_item_group(),
            "page_template": "Ready-to-order page",
            "buying_path": "Direct checkout",
            "publish_status": "Local Preview Ready",
            "base_price": 75,
            "product_summary": "Rollback-safe complex variant media checkout proof.",
            "option_rows": [
                {
                    "axis_name": size_axis,
                    "selection_behavior": "SKU-defining variant",
                    "control_type": "Single select",
                    "required": 1,
                    "min_selections": 1,
                    "max_selections": 1,
                    "values": "Small\nMedium\nLarge\nGrand",
                },
                {
                    "axis_name": finish_axis,
                    "selection_behavior": "SKU-defining variant",
                    "control_type": "Single select",
                    "required": 1,
                    "min_selections": 1,
                    "max_selections": 1,
                    "values": "Matte\nChrome\nSatin\nCrystal",
                },
                {
                    "axis_name": stand_axis,
                    "selection_behavior": "SKU-defining variant",
                    "control_type": "Single select",
                    "required": 1,
                    "min_selections": 1,
                    "max_selections": 1,
                    "values": "Tabletop\nWeighted\nHanging",
                },
                {
                    "axis_name": "Accent Pattern",
                    "selection_behavior": "Configuration only",
                    "control_type": "Single select",
                    "required": 0,
                    "min_selections": 0,
                    "max_selections": 1,
                    "values": "Confetti\nCloud\nSwirl",
                },
            ],
            "media_rule_rows": [
                {
                    "rule_name": "Small size media",
                    "rule_type": "Selection group",
                    "selection_group": size_axis,
                    "selection_value": "Small",
                    "image": size_image,
                    "approved_for_customer": 1,
                },
                {
                    "rule_name": "Large chrome media",
                    "rule_type": "Selection combination",
                    "selection_conditions": f"{size_axis}=Large\n{finish_axis}=Chrome",
                    "image": combo_image,
                    "approved_for_customer": 1,
                },
            ],
            "content_rule_rows": [
                {
                    "rule_name": "Large chrome content",
                    "rule_type": "Selection combination",
                    "selection_conditions": f"{size_axis}=Large\n{finish_axis}=Chrome",
                    "display_title": combo_title,
                    "product_story": "<p>Large chrome proof story.</p>",
                    "product_details": "<p>Large chrome proof details.</p>",
                    "approved_for_customer": 1,
                }
            ],
        }
    ).insert(ignore_permissions=True)

    preview = get_local_apply_preview(doc.name)
    if preview.get("planned_counts", {}).get("item_variants") != 48:
        raise ContractFail(f"Complex proof should plan 48 variants, found {preview}")

    with _temporary_conf_flag("lt_allow_local_blueprint_apply", 1):
        result = apply_locally_from_desk(doc.name)

    if len(result.get("variants") or []) != 48 or len(result.get("item_prices") or []) != 48:
        raise ContractFail(f"Complex proof did not apply 48 priced variants: {result}")

    frappe.db.set_value(
        "Website Item",
        result["website_item"],
        {"published": 1, "website_image": fallback_image},
        update_modified=False,
    )

    variant_item = f"{slug}-LARGE-CHROME-WEIGHT"
    configuration = {
        "schema_version": CONFIG_VERSION,
        "item_code": variant_item,
        "website_item_code": slug,
        "selected_options": {
            size_axis: "Large",
            finish_axis: "Chrome",
            stand_axis: "Weighted",
        },
        "configuration_groups": [
            {
                "key": "accent-pattern",
                "label": "Accent Pattern",
                "values": ["Confetti"],
            }
        ],
        "add_ons": [],
        "customizations": [],
    }

    from locally_twisted.api.cart import get_cart_items
    from locally_twisted.api.variant_media import get_variant_media
    from locally_twisted.www.checkout import _resolve_sale_lines

    media = get_variant_media(
        item_code=variant_item,
        template_item_code=slug,
        configuration=configuration,
    )
    if media.get("image") != combo_image:
        raise ContractFail(f"Combination media should win on the product page, found {media}")

    cart = get_cart_items(
        [
            {
                "item_code": variant_item,
                "qty": 1,
                "configuration": configuration,
            }
        ]
    )
    cart_items = cart.get("items") or []
    if len(cart_items) != 1 or cart_items[0].get("website_image") != combo_image:
        raise ContractFail(f"Cart should use the selected Product Setup image, found {cart}")

    sale_lines, _resolved_items = _resolve_sale_lines(
        [{"item_code": variant_item, "qty": 1, "configuration": configuration}]
    )
    if len(sale_lines) != 1:
        raise ContractFail(f"Complex proof should produce one base checkout line, found {sale_lines}")
    payload = json.loads(sale_lines[0].get("custom_lt_configuration_json") or "{}")
    if payload.get("selected_media", {}).get("image") != combo_image:
        raise ContractFail(f"Checkout payload should preserve selected image, found {payload}")
    if payload.get("selected_content", {}).get("display_title") != combo_title:
        raise ContractFail(f"Checkout payload should preserve selected Product Setup copy, found {payload}")

    return {
        "blueprint": doc.name,
        "item_code": result.get("item_code"),
        "variant_count": len(result.get("variants") or []),
        "item_price_count": len(result.get("item_prices") or []),
        "selected_image": combo_image,
        "selected_title": combo_title,
        "fallback_image": fallback_image,
    }


def _insert_support_add_on_item(suffix: str) -> str:
    item_code = f"contract-addon-{suffix}"
    item = frappe.get_doc(
        {
            "doctype": "Item",
            "item_code": item_code,
            "item_name": "Contract Blueprint Add-On",
            "item_group": _first_leaf_item_group(),
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "is_purchase_item": 0,
            "include_item_in_manufacturing": 0,
            "description": "Rollback-safe support add-on for product blueprint contract.",
        }
    )
    item.insert(ignore_permissions=True)
    frappe.get_doc(
        {
            "doctype": "Item Price",
            "item_code": item_code,
            "price_list": "Standard Selling",
            "price_list_rate": 9,
            "currency": "USD",
            "selling": 1,
        }
    ).insert(ignore_permissions=True)
    return item_code


def _assert_desk_preview_guest_blocks(doc) -> None:
    current_user = frappe.session.user
    try:
        frappe.set_user("Guest")
        error = _call_expect_error(lambda: get_local_apply_preview(doc.name))
    finally:
        frappe.set_user(current_user)
    if "Please sign in" not in error:
        raise ContractFail(f"Desk preview should reject Guest users: {error}")


class _temporary_conf_flag:
    def __init__(self, key: str, value):
        self.key = key
        self.value = value
        self.previous = None
        self.had_key = False

    def __enter__(self):
        self.had_key = self.key in frappe.conf
        self.previous = frappe.conf.get(self.key)
        frappe.conf[self.key] = self.value

    def __exit__(self, exc_type, exc, tb):
        if self.had_key:
            frappe.conf[self.key] = self.previous
        else:
            frappe.conf.pop(self.key, None)


def _assert_local_apply_records(doc, result: dict[str, object], slug: str, axis: str) -> None:
    if result.get("live_publish_enabled"):
        raise ContractFail(f"Local apply attempted to enable live publish: {result}")
    if result.get("website_item_published") != 0:
        raise ContractFail(f"Local apply published a Website Item: {result}")
    target_item_code = frappe.db.get_value(doc.doctype, doc.name, "target_item_code")
    target_website_item = frappe.db.get_value(doc.doctype, doc.name, "target_website_item")
    if target_item_code != result.get("item_code"):
        raise ContractFail(f"Blueprint target_item_code was not linked after local apply: {target_item_code}")
    if target_website_item != result.get("website_item"):
        raise ContractFail(f"Blueprint target_website_item was not linked after local apply: {target_website_item}")

    item = frappe.get_doc("Item", slug)
    if not item.has_variants:
        raise ContractFail(f"Local apply template Item should use variants: {slug}")
    attrs = [row.attribute for row in item.attributes or []]
    if attrs != [axis]:
        raise ContractFail(f"Local apply template attributes did not match blueprint axis: {attrs}")
    if frappe.db.exists("Item Price", {"item_code": slug, "price_list": "Standard Selling", "selling": 1}):
        raise ContractFail("Local apply created a template Item Price for a variant product.")

    wi = frappe.get_doc("Website Item", result["website_item"])
    if wi.item_code != slug:
        raise ContractFail(f"Local apply Website Item points at wrong Item: {wi.item_code}")
    if wi.published:
        raise ContractFail("Local apply Website Item must stay unpublished.")
    if wi.lt_product_page_type != "simple_product" or wi.lt_commerce_lane != "checkout":
        raise ContractFail(
            "Local apply Website Item lost ecommerce contract fields: "
            f"{wi.lt_product_page_type}|{wi.lt_commerce_lane}"
        )

    prices = result.get("item_prices") or []
    variants = result.get("variants") or []
    if len(variants) != 2 or len(prices) != 2:
        raise ContractFail(f"Local apply expected 2 variants and 2 prices, got {result}")


def _assert_dynamic_blueprint_add_on(slug: str, add_on_item: str) -> None:
    options = get_checkout_add_on_options(slug)
    match = next((row for row in options if row.get("item_code") == add_on_item), None)
    if not match:
        raise ContractFail(f"Blueprint add-on was not exposed by product options for {slug}: {options}")
    if not str(match.get("key") or "").startswith("blueprint_"):
        raise ContractFail(f"Blueprint add-on key should be namespaced, got {match}")
    lines = sales_order_add_on_lines(
        resolved_item={"item_code": slug, "website_item_code": slug},
        client_configuration={
            "schema_version": CONFIG_VERSION,
            "add_ons": [
                {
                    "key": match["key"],
                    "label": match["label"],
                    "quantity": 2,
                }
            ]
        },
        parent_qty=1,
    )
    if len(lines) != 1 or lines[0].get("item_code") != add_on_item or lines[0].get("qty") != 2:
        raise ContractFail(f"Blueprint add-on did not produce the expected checkout line: {lines}")
    max_error = _call_expect_error(
        lambda: sales_order_add_on_lines(
            resolved_item={"item_code": slug, "website_item_code": slug},
            client_configuration={
                "schema_version": CONFIG_VERSION,
                "add_ons": [
                    {
                        "key": match["key"],
                        "label": match["label"],
                        "quantity": 4,
                    }
                ]
            },
            parent_qty=1,
        )
    )
    if "higher than this product allows" not in max_error:
        raise ContractFail(f"Blueprint add-on quantity limit did not fail loudly: {max_error}")


def _assert_local_apply_preserves_existing_public_visibility() -> dict[str, object]:
    suffix = frappe.generate_hash(length=8).lower()
    slug = f"contract-existing-public-{suffix}"
    item_group = _first_leaf_item_group()
    item = frappe.get_doc(
        {
            "doctype": "Item",
            "item_code": slug,
            "item_name": f"Contract Existing Public {suffix}",
            "item_group": item_group,
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "is_purchase_item": 0,
            "include_item_in_manufacturing": 0,
        }
    ).insert(ignore_permissions=True)
    from webshop.webshop.doctype.website_item.website_item import make_website_item

    website_item = make_website_item(item, save=False)
    website_item.web_item_name = item.item_name
    website_item.item_group = item_group
    expected_route = _route_for(frappe, slug, item_group)
    website_item.route = expected_route
    website_item.published = 1
    website_item.website_image = f"/files/{slug}.png"
    if hasattr(website_item, "lt_product_page_type"):
        website_item.lt_product_page_type = "simple_product"
    if hasattr(website_item, "lt_commerce_lane"):
        website_item.lt_commerce_lane = "checkout"
    website_item.insert(ignore_permissions=True)

    doc = frappe.get_doc(
        {
            "doctype": "LT Product Blueprint",
            "product_name": f"Contract Existing Public {suffix}",
            "product_slug": slug,
            "target_item_code": slug,
            "target_website_item": website_item.name,
            "item_group": item_group,
            "page_template": "Ready-to-order page",
            "buying_path": "Direct checkout",
            "publish_status": "Draft",
            "shop_visibility": "Keep current",
            "base_price": 25,
            "product_summary": "Existing public Product Setup preservation proof.",
            "primary_image": f"/files/{slug}.png",
        }
    ).insert(ignore_permissions=True)

    result = apply_blueprint_locally(
        doc,
        allow_writes=True,
        confirmation=LOCAL_APPLY_CONFIRMATION,
    )
    published_after = int(frappe.db.get_value("Website Item", website_item.name, "published") or 0)
    route_after = frappe.db.get_value("Website Item", website_item.name, "route")
    if result.get("website_item_published") != 1 or published_after != 1:
        raise ContractFail(f"Existing public Website Item was not preserved during local apply: {result}")
    if route_after != expected_route:
        raise ContractFail(f"Existing public Website Item route changed during local apply: {route_after}")

    doc.shop_visibility = "Hidden from shop"
    hide_error = _call_expect_error(
        lambda: apply_blueprint_locally(
            doc,
            allow_writes=True,
            confirmation=LOCAL_APPLY_CONFIRMATION,
        )
    )
    if "cannot hide an existing public Website Item" not in hide_error:
        raise ContractFail(f"Existing public hide request did not fail loudly: {hide_error}")

    doc.shop_visibility = "Keep current"
    legacy_route = f"shop-items/legacy-{slug}"
    frappe.db.set_value("Website Item", website_item.name, "route", legacy_route, update_modified=False)
    route_error = _call_expect_error(
        lambda: apply_blueprint_locally(
            doc,
            allow_writes=True,
            confirmation=LOCAL_APPLY_CONFIRMATION,
        )
    )
    if "cannot reroute an existing public Website Item" not in route_error:
        raise ContractFail(f"Existing public route change did not fail loudly: {route_error}")

    return {
        "item_code": slug,
        "website_item": website_item.name,
        "published_after_apply": published_after,
        "hide_request_blocked": True,
        "route_change_blocked": True,
    }


def _assert_expected_local_apply_delta(before: dict[str, int], after: dict[str, int]) -> None:
    expected = {
        "Item": 3,
        "Website Item": 1,
        "Item Price": 2,
        "Item Attribute": 1,
        "Website Slideshow": 0,
        "Website Slideshow Item": 0,
        "Sales Order": 0,
        "Sales Invoice": 0,
        "Payment Request": 0,
    }
    actual = {doctype: after[doctype] - before[doctype] for doctype in expected}
    if actual != expected:
        raise ContractFail(f"Unexpected local apply record delta: expected {expected}, got {actual}")


def _insert_expect_error(payload: dict[str, object]) -> str:
    try:
        frappe.get_doc(payload).insert(ignore_permissions=True)
    except Exception as exc:
        return str(exc)
    raise ContractFail(f"Expected insert to fail, but it succeeded: {payload.get('product_slug')}")


def _call_expect_error(fn) -> str:
    try:
        fn()
    except Exception as exc:
        return str(exc)
    raise ContractFail("Expected call to fail, but it succeeded.")


def _assert_no_business_mutation(before: dict[str, int], after: dict[str, int]) -> None:
    changed = {
        doctype: {"before": before[doctype], "after": after[doctype]}
        for doctype in GUARD_DOCTYPES
        if before.get(doctype) != after.get(doctype)
    }
    if changed:
        raise ContractFail(f"Product blueprint contract mutated business records: {changed}")


def _first_leaf_item_group() -> str:
    value = frappe.db.get_value("Item Group", {"is_group": 0}, "name") or frappe.db.get_value("Item Group", {}, "name")
    if not value:
        raise ContractFail("No Item Group exists for product blueprint contract.")
    return value


def _first_unrelated_item(slug: str) -> str:
    rows = frappe.get_all(
        "Item",
        filters={"item_code": ["not like", f"{slug}%"]},
        pluck="item_code",
        limit_page_length=1,
    )
    if not rows:
        raise ContractFail(f"No unrelated Item exists for price-target guard test: {slug}")
    return rows[0]


def _counts() -> dict[str, int]:
    return {doctype: int(frappe.db.count(doctype)) for doctype in GUARD_DOCTYPES}
