frappe.ui.form.on("LT Product Blueprint", {
  refresh(frm) {
    if (frm.is_new()) return;

    add_target_buttons(frm);
    add_local_apply_buttons(frm);
  },
});

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
