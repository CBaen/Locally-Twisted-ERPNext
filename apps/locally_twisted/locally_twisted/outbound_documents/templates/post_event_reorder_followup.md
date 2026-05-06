---
id: post_event_reorder_followup
title: Post-event Reorder Follow-up
audience: Event buyer, office manager, school admin, or dealership marketing contact
owner: Sales / customer success
stage: post_event
status: source_template_ready
automation_ready: generator_ready_review_required
trigger: Event is completed and follow-up is ready for review
delivery_channel: draft email | reviewed email
record_source: Sales Order | Sales Invoice | Customer | Lead | Portfolio proof
policy_lanes: event_balloon_decor | corporate_invoicing | privacy
required_fields: event_name | event_date | thank_you_note | proof_photos_if_approved | repeat_event_prompt | annual_support_prompt | referral_or_review_path
do_not_send_without: human_timing_review | approved_photo_use | correct_contact | no_open_service_issue
verification: outbound_documents_contract
template_type: outbound_markdown_v1
---

## Audience

The event buyer needs a professional thank-you for `{{ sales_order.name }}` plus an easy path to repeat, recommend, or plan next year's event.

## Answer First

Put the completed event, thank-you, approved photo status, repeat/annual support path, and reply contact at the top so the customer immediately sees why the follow-up matters.

## Required Data

- Event name/date and customer contact
- Short thank-you tied to the delivered event
- Approved proof photos or no-photo fallback
- Repeat-order, annual-event, or contract-support prompt
- Review/referral path if appropriate

## Recipient Outcome

The customer can recommend Locally Twisted, order again, or start a recurring event conversation without hunting for the right contact.

## Automation Notes

Generate as a draft after event completion or invoice/payment closure.

Do not auto-send from this registry. Timing, photo permission, open service issues, and tone must be reviewed.

## Boundaries

Keep this helpful and relationship-focused. Do not send after a complaint, unresolved balance dispute, or unapproved photo situation.
