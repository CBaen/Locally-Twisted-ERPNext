frappe.ui.form.on("LT Product Blueprint", {
  refresh(frm) {
    if (frm.is_new()) return;

    add_catalog_readiness_button(frm);
    add_readiness_button(frm);
    add_target_buttons(frm);
    add_local_apply_buttons(frm);
  },
});

function add_catalog_readiness_button(frm) {
  frm.add_custom_button(__("Show Catalog Readiness"), () => {
    show_catalog_readiness();
  }, __("Product Setup"));
}

function add_readiness_button(frm) {
  frm.add_custom_button(__("Show Readiness"), () => {
    show_readiness(frm);
  }, __("Product Setup"));
}

function add_target_buttons(frm) {
  if (frm.doc.target_item_code) {
    frm.add_custom_button(__("Open Item"), () => {
      frappe.set_route("Form", "Item", frm.doc.target_item_code);
    }, __("Target Records"));
  }

  if (frm.doc.target_website_item) {
    frm.add_custom_button(__("Open Website Item"), () => {
      frappe.set_route("Form", "Website Item", frm.doc.target_website_item);
    }, __("Target Records"));
  }
}

function add_local_apply_buttons(frm) {
  frm.add_custom_button(__("Preview Local Apply"), () => {
    preview_local_apply(frm);
  }, __("Local Product Setup"));

  if (frm.doc.validation_status !== "Ready For Local Preview") return;

  frm.add_custom_button(__("Apply Locally"), () => {
    confirm_local_apply(frm);
  }, __("Local Product Setup"));
}

function show_readiness(frm) {
  const validation = parse_validation_json(frm);
  const readiness = validation.owner_publish_readiness || {};
  const approvals = validation.publish_apply_approval || {};
  const blockers = validation.blockers || [];
  const state = readiness.state || frm.doc.validation_status || __("Not checked");
  const next_step = readiness.next_owner_step || __("Review the validation summary before taking the next step.");
  const public_success = readiness.public_success_claim_allowed === true;
  const apply_allowed = readiness.publish_apply_allowed === true || approvals.live_apply_approved === true;
  const blocker_html = blockers.length
    ? `<p><strong>${__("Needs attention")}</strong></p><ul>${blockers.slice(0, 10).map((row) => `<li>${frappe.utils.escape_html(row)}</li>`).join("")}</ul>`
    : `<p>${__("No validation blockers are listed in the saved readiness packet.")}</p>`;

  frappe.msgprint({
    title: __("Product Setup Readiness"),
    indicator: apply_allowed ? "green" : "orange",
    message: `
      <p><strong>${frappe.utils.escape_html(state)}</strong></p>
      <p>${frappe.utils.escape_html(readiness.plain_message || "")}</p>
      <p>${frappe.utils.escape_html(next_step)}</p>
      <ul>
        <li>${__("Public success claim allowed")}: ${public_success ? __("Yes") : __("No")}</li>
        <li>${__("Live publish/apply allowed")}: ${apply_allowed ? __("Yes") : __("No")}</li>
      </ul>
      ${blocker_html}
    `,
  });
}

function parse_validation_json(frm) {
  if (!frm.doc.validation_json) return {};
  try {
    return JSON.parse(frm.doc.validation_json);
  } catch (error) {
    return {
      owner_publish_readiness: {
        state: __("Blocked - Proof Needed"),
        plain_message: __("The saved readiness packet could not be read. Re-save this Product Setup before treating it as ready."),
        public_success_claim_allowed: false,
        publish_apply_allowed: false,
      },
      blockers: [__("Saved validation JSON could not be read.")],
      publish_apply_approval: {
        live_apply_approved: false,
      },
    };
  }
}

function show_catalog_readiness() {
  frappe.call({
    method: "locally_twisted.locally_twisted.doctype.lt_product_blueprint.lt_product_blueprint.get_catalog_readiness_summary",
    freeze: true,
    freeze_message: __("Reading saved Product Setup readiness..."),
  }).then((response) => {
    const result = response.message || {};
    const counts = result.counts_by_owner_state || {};
    const rows = result.rows || [];
    const blocked = rows.filter((row) => row.is_blocked).slice(0, 10);
    const count_html = Object.keys(counts).length
      ? `<ul>${Object.keys(counts).sort().map((state) => `<li>${frappe.utils.escape_html(state)}: ${counts[state]}</li>`).join("")}</ul>`
      : `<p>${__("No saved readiness states were found.")}</p>`;
    const blocked_html = blocked.length
      ? `<ul>${blocked.map((row) => catalog_readiness_blocked_row_html(row)).join("")}</ul>`
      : `<p>${__("No blocked Product Setup rows were found in the saved readiness summary.")}</p>`;

    frappe.msgprint({
      title: __("Catalog Readiness"),
      indicator: result.blocked_count ? "orange" : "green",
      message: `
        <p>${__("Read-only summary from saved Product Setup validation rows. No product records were changed.")}</p>
        <p>${__("Proof mode")}: ${frappe.utils.escape_html(result.proof_mode || "source_saved_validation_only")}</p>
        <ul>
          <li>${__("Products checked")}: ${result.total_products || 0}</li>
          <li>${__("Blocked")}: ${result.blocked_count || 0}</li>
          <li>${__("Public success claim allowed")}: ${result.public_success_claim_allowed_count || 0}</li>
          <li>${__("Live publish/apply allowed")}: ${result.live_apply_allowed_count || 0}</li>
        </ul>
        <p><strong>${__("By saved readiness state")}</strong></p>
        ${count_html}
        <p><strong>${__("Top blocked products")}</strong></p>
        ${blocked_html}
      `,
    });
  });
}

function catalog_readiness_blocked_row_html(row) {
  const label = row.product_name || row.product_slug || row.name || __("Unnamed Product Setup");
  const blockers = row.blockers || [];
  const blocker_text = blockers.length ? blockers[0] : __("No blocker details saved.");
  return `
    <li>
      <strong>${frappe.utils.escape_html(label)}</strong>
      <br>${frappe.utils.escape_html(row.owner_state || __("Blocked - Proof Needed"))}
      <br>${frappe.utils.escape_html(blocker_text)}
      <br>${__("Next")}: ${frappe.utils.escape_html(row.next_owner_step || __("Review this Product Setup before taking action."))}
      <br>${__("Developer help")}: ${row.developer_help_needed ? __("Yes") : __("No")}
      <br>${__("Saved evidence")}: ${frappe.utils.escape_html(row.validation_modified_on || __("Unknown"))}
    </li>
  `;
}

function preview_local_apply(frm) {
  frappe.call({
    method: "locally_twisted.locally_twisted.doctype.lt_product_blueprint.lt_product_blueprint.get_local_apply_preview",
    args: { name: frm.doc.name },
    freeze: true,
    freeze_message: __("Checking local product records..."),
  }).then((response) => {
    const result = response.message || {};
    const counts = result.planned_counts || {};
    const blockers = result.blockers || [];
    const blocker_html = blockers.length
      ? `<p><strong>${__("Needs attention")}</strong></p><ul>${blockers.map((row) => `<li>${frappe.utils.escape_html(row)}</li>`).join("")}</ul>`
      : `<p>${__("This setup is ready for a guarded local apply.")}</p>`;

    frappe.msgprint({
      title: __("Local Apply Preview"),
      indicator: result.ok ? "green" : "red",
      message: `
        <p>${frappe.utils.escape_html(result.summary || "")}</p>
        <ul>
          <li>${__("Item attributes")}: ${counts.item_attributes || 0}</li>
          <li>${__("Variants")}: ${counts.item_variants || 0}</li>
          <li>${__("Item prices")}: ${counts.item_prices || 0}</li>
          <li>${__("Website items")}: ${counts.website_items || 0}</li>
        </ul>
        ${blocker_html}
      `,
    });
  });
}

function confirm_local_apply(frm) {
  const dialog = new frappe.ui.Dialog({
    title: __("Apply Local Product Records"),
    fields: [
      {
        fieldtype: "HTML",
        options: `
          <p>${__("This creates or updates unpublished local ERPNext product records for testing.")}</p>
          <p>${__("It does not publish the Website Item and does not create orders, invoices, payments, Stripe records, DNS changes, or live-site changes.")}</p>
        `,
      },
      {
        fieldname: "confirm_local_only",
        fieldtype: "Check",
        label: __("Create unpublished local records only"),
        reqd: 1,
      },
    ],
    primary_action_label: __("Apply Locally"),
    primary_action(values) {
      if (!values.confirm_local_only) {
        frappe.msgprint(__("Check the confirmation box before applying local product records."));
        return;
      }

      frappe.call({
        method: "locally_twisted.locally_twisted.doctype.lt_product_blueprint.lt_product_blueprint.apply_locally_from_desk",
        args: { name: frm.doc.name },
        freeze: true,
        freeze_message: __("Creating unpublished local product records..."),
      }).then((response) => {
        const result = response.message || {};
        dialog.hide();
        frm.reload_doc();
        frappe.show_alert({
          indicator: "green",
          message: result.summary || __("Local product records were created."),
        });
      });
    },
  });

  dialog.show();
}
