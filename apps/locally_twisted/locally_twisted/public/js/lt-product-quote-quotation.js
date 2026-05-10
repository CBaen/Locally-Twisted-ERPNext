(function () {
  const STATUS_READY = "Ready For Customer Review";
  const SOURCE_LEAD_FIELD = "custom_lt_source_lead";
  const COMMERCE_LANE_FIELD = "custom_lt_commerce_lane";
  const QUOTE_STATUS_FIELD = "custom_lt_product_quote_status";
  const SEND_METHOD =
    "locally_twisted.product_quote_operator_send.send_reviewed_product_quote_to_customer";
  const BUSINESS_COPY = "locallytwisted@gmail.com";

  function isProductQuote(frm) {
    return Boolean(
      frm.doc &&
        frm.doc[SOURCE_LEAD_FIELD] &&
        frm.doc[COMMERCE_LANE_FIELD] === "quote_first",
    );
  }

  function isSendReady(frm) {
    return frm.doc.docstatus === 1 && frm.doc[QUOTE_STATUS_FIELD] === STATUS_READY;
  }

  function sendApprovalLink(frm) {
    frappe.confirm(
      __(
        "Send this reviewed quote to the customer and copy {0}?",
        [BUSINESS_COPY],
      ),
      () => {
        frappe.call({
          method: SEND_METHOD,
          args: {
            quotation_name: frm.doc.name,
          },
          freeze: true,
          freeze_message: __("Sending approval link"),
          callback: (response) => {
            const result = response.message || {};
            if (!result.ok) {
              frappe.throw(
                __("Tiny snag: the quote approval link did not send."),
              );
            }
            frm.reload_doc();
            frappe.show_alert({
              message: __("Quote approval link sent with business copy."),
              indicator: "green",
            });
          },
        });
      },
    );
  }

  frappe.ui.form.on("Quotation", {
    refresh(frm) {
      if (!isProductQuote(frm) || !isSendReady(frm)) {
        return;
      }
      frm.add_custom_button(
        __("Send Approval Link"),
        () => sendApprovalLink(frm),
        __("Product Quote"),
      );
    },
  });
})();
