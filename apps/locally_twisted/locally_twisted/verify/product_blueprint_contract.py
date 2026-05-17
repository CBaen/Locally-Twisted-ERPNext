"""Rollback-safe live contract for LT Product Blueprint records."""

from __future__ import annotations

import json

import frappe

from locally_twisted.product_blueprint_local_apply import (
    LOCAL_APPLY_CONFIRMATION,
    ProductBlueprintApplyError,
    apply_blueprint_locally,
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
    after = _counts()
    _assert_no_business_mutation(before, after)
    apply_result = _assert_guarded_local_apply()
    owner_result = _assert_owner_profile_product_build_flow()
    return {
        "ok": True,
        "blueprint": doc.name,
        "validation_status": doc.validation_status,
        "staff_setup": staff_result,
        "owner_setup": owner_result,
        "save_only_guard_counts_unchanged": True,
        "local_apply": apply_result,
    }


def _assert_doctypes_exist() -> None:
    missing = [doctype for doctype in BLUEPRINT_DOCTYPES if not frappe.db.exists("DocType", doctype)]
    if missing:
        raise ContractFail(f"Missing product blueprint DocTypes after migrate: {missing}")


def _insert_valid_quote_first_blueprint():
    doc = frappe.get_doc(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "Contract Product Blueprint",
            "product_slug": "contract-product-blueprint",
            "item_group": _first_leaf_item_group(),
            "page_template": "Custom quote page",
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
            "base_price": 42,
            "product_summary": "Rollback-safe local apply contract product.",
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
    email = f"lt-product-setup-{suffix}@example.invalid"
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": "Product",
            "last_name": "Setup Proof",
            "enabled": 1,
            "send_welcome_email": 0,
            "roles": [{"role": "Item Manager"}],
        }
    )
    user.insert(ignore_permissions=True)
    return email


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

        with _temporary_conf_flag("lt_allow_local_blueprint_apply", 1):
            result = apply_locally_from_desk(doc.name)
        if not result.get("ok"):
            raise ContractFail(f"Owner local apply did not return ok: {result}")

        _assert_local_apply_records(doc, result, slug, axis)
        return {
            "user": OWNER_USER,
            "blueprint": doc.name,
            "item_code": result.get("item_code"),
            "website_item": result.get("website_item"),
            "variant_count": len(result.get("variants") or []),
            "item_price_count": len(result.get("item_prices") or []),
            "published": result.get("website_item_published"),
        }
    finally:
        frappe.set_user(current_user)


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


def _assert_expected_local_apply_delta(before: dict[str, int], after: dict[str, int]) -> None:
    expected = {
        "Item": 3,
        "Website Item": 1,
        "Item Price": 2,
        "Item Attribute": 1,
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


def _counts() -> dict[str, int]:
    return {doctype: int(frappe.db.count(doctype)) for doctype in GUARD_DOCTYPES}
