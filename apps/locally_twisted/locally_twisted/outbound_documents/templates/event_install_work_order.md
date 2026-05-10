---
id: event_install_work_order
title: Event Install Work Order
audience: Venue contact, client day-of contact, and install crew
owner: Operations / production
stage: event_execution
status: source_template_ready
automation_ready: generator_ready_review_required
trigger: Booking is approved and install details are ready for production review
delivery_channel: PDF | internal print | reviewed email
record_source: Sales Order | Lead | Customer | Address | Item | Task
policy_lanes: event_balloon_decor | ready_to_order_pickup_delivery | privacy
required_fields: event_date | install_window | teardown_window | venue_address | onsite_contact | decor_scope | access_notes | weather_plan | crew_notes
do_not_send_without: approved_booking | venue_access_review | day_of_contact | weather_or_outdoor_review
verification: outbound_documents_contract
template_type: outbound_markdown_v1
---

## Audience

The venue, client day-of contact, and crew need a shared practical plan for `{{ booking.reference }}`.

## Answer First

Put event date, install/teardown windows, venue address, onsite contact, access notes, and open assumptions at the top so everyone knows where to go and what still needs confirmation.

## Required Data

- Event date, install window, and teardown window
- Venue address, access notes, loading details, and onsite contact
- Decor scope, counts, color notes, and placement notes
- Weather, shade, outdoor, attachment, and cleanup assumptions
- Crew notes and internal-only production checks

## Recipient Outcome

Everyone knows where to go, when to arrive, what is being installed, what access is needed, and which assumptions still need confirmation.

## Automation Notes

This can be generated from an approved booking and then reviewed by production before sharing.

Do not auto-send from this registry. Venue rules, outdoor assumptions, and day-of contacts need review first.

## Boundaries

Separate client-safe notes from internal production notes before sending outside the company.
