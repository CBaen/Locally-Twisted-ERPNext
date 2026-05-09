---
id: erpnext-ecommerce-receiving-architecture
name: ERPNext Ecommerce Receiving Architecture
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe ecommerce product import, product detail logic, cart, checkout, and invoice integration
currently_true: planned
verification_level: 1
last_verified: 2026-05-09
evidence_quality: GL decision + current code inspection
successful_uses: 0
failed_uses: 0
regressions: 0
depends_on:
  - erpnext-catalog-variant-price-parity
  - erpnext-checkout-commerce-rules
  - fail-loud-operating-law
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - ecommerce
  - Odoo
  - product import
  - variants
  - add-ons
  - checkout
  - invoice
---

# ERPNext Ecommerce Receiving Architecture

Use this before importing, repairing, or claiming completion for Odoo-derived products in ERPNext ecommerce.

## Rule

Do not treat product transfer as the goal. ERPNext must first be able to safely receive products and integrate their meaning everywhere: backend fields, product template type, variant logic, add-on logic, cascading dependencies, dynamic pricing, media visibility, product pages, cart, checkout, Sales Order, invoice, fulfillment/operator meaning, desktop/mobile customer journeys, and fail-loud verifiers.

Odoo is a conceptual witness for mature ecommerce behavior, not infrastructure to copy. Do not import Odoo fields into ERPNext unless the ERPNext destination field, behavior owner, and verifier exist.

## Current LT Contract

- No real product import until incomplete/awkward/missing logic is surfaced to GL and resolved.
- Test products are proof cases only: Unicorn Bouquet and Classic Arch.
- Product template types are logic/process classes:
  - `simple_product`: few options, little customization, but still backend-driven.
  - `complex_custom_product`: significant variants/options/customization/dependencies.
- Native ERPNext/Webshop ecommerce is insufficient and may need custom DocTypes, child tables, custom fields, APIs, template overrides, pricing services, and verifiers.
- Frontend must render backend truth. Missing backend field/logic cannot be hidden by polished UI.
- Variant images are conditional: only flag missing image mapping when the source says a variant has or should expose an image. Not every variant requires its own image.

## Required Gates

Before importing a product family, prove:

1. Product has a valid template type.
2. Every required source concept has a real ERPNext/custom destination.
3. Every destination exists and is executable, not just a label.
4. Required variant axes, optional add-ons, customization axes, backend-only fields, and needs-review axes are separated.
5. Server-side pricing resolves base variant, add-ons, and modifiers.
6. Product page, cart, checkout, Sales Order, invoice, and fulfillment/operator views preserve selected meaning.
7. Desktop and mobile journeys expose the needed choices for the template type.
8. Missing/incomplete/awkward data fails loudly through import blocker, verifier failure, admin report, customer-safe block, or GL review queue.

## Blast-Radius Checklist For Missing Features

Before building any missing ecommerce feature, write the feature's blast-radius note:

- What is missing?
- Why native ERPNext cannot handle it safely?
- What DocTypes, fields, child tables, templates, APIs, scripts, cart paths, checkout paths, invoices, and reports are affected?
- What silent failure would happen without the feature?
- What fail-loud behavior blocks fake success?
- What verifier proves the feature across backend/frontend/cart/checkout/invoice?
- What is the smallest safe proof slice?

Expected feature notes: add-on subsystem, server pricing resolver, variant/media visibility, cascading option dependencies, product-template classification, cart metadata, checkout validation, Sales Order / invoice payload preservation, mobile journey behavior, and import readiness gates.

## Research Requirement

Before implementation, draft a five-section research brief and dispatch `/expedition` only after GL approval. Research must cover both:

- ERPNext/Frappe implementation patterns and sharp edges for custom ecommerce logic.
- Odoo ecommerce concepts/behaviors that should be recreated safely inside ERPNext.

The brief must be stranger-ready and exact to the current stack; do not dispatch a history-heavy handoff.

## Verification Pattern

A future verifier suite must report per product and per feature:

- verified
- needs review
- broken
- unverifiable from source

It must check import contract, backend field existence, option/variant reachability, add-on rules, price parity/resolution, media mapping where source provides it, frontend visibility, cart payload, checkout totals, Sales Order/invoice preservation, and mobile/desktop customer journey exposure.

## Red Flags

- Product page looks correct but Sales Order/invoice loses selected choices.
- Imported field has no ERPNext/custom destination.
- Frontend JS owns price/option/add-on truth without backend validation.
- Add-on appears as a visual card but lacks cart/invoice behavior.
- ERPNext native dropdowns flatten Odoo-style dependencies or availability rules.
- A missing field produces empty UI instead of a blocker/report.
- A proof product works by hardcoding rather than reusable template contract.
- Product migration is described as complete because records exist.
