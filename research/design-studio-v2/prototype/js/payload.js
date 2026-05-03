(function () {
  const {
    ENGINE_LABELS,
    PRODUCT_FAMILIES,
    calculateRenderFacts,
    designForId,
    familyForId,
    labelFor,
    scenarioForId,
    selectedVariantAxes,
    sourceVariantCount
  } = window.LTDesignStudio;

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function labelsForFamilyIds(familyIds) {
    return familyIds.map((familyId) => labelFor(PRODUCT_FAMILIES, familyId));
  }

  function buildSelectedPiece(state) {
    const family = familyForId(state.product_family);
    const design = designForId(family.id, state.design_id);
    const renderFacts = calculateRenderFacts(state);
    return {
      product_family: family.id,
      display_label: family.label,
      product_label: family.product_label,
      source_products: family.source_products.map((product) => ({ ...product })),
      variant_count: sourceVariantCount(family),
      selected_variant_axes: selectedVariantAxes(state),
      design: design.label,
      selected_color_names: [...state.selected_color_names],
      render_facts: {
        ...renderFacts,
        construction_basis: renderFacts.construction_basis,
        engine_label: ENGINE_LABELS[renderFacts.render_engine] || renderFacts.render_engine
      }
    };
  }

  function buildDesignPayload(state) {
    const scenario = scenarioForId(state.review_scenario);
    const selectedPiece = buildSelectedPiece(state);
    const consideredLabels = labelsForFamilyIds(state.pieces_considered);

    return {
      schema_version: state.schema_version,
      source: "research_prototype",
      customer_facing_path: "Plan Custom Decor",
      review_scenario: scenario ? scenario.id : "custom_review_state",
      review_scenario_label: scenario ? scenario.label : "Custom review state",
      event_context: state.event_context,
      selected_pieces: [selectedPiece],
      pieces_considered: [...state.pieces_considered],
      declined_suggestions: state.pieces_considered.map((familyId) => ({
        product_family: familyId,
        display_label: labelFor(PRODUCT_FAMILIES, familyId),
        reason: "Shown as a complementary planning option in the prototype."
      })),
      render_summary: {
        type: "planning_visualization",
        disclaimer: state.disclaimer,
        renderer: "inline_svg_2d_construction_model"
      },
      sales_summary: `${state.event_context} decor starting point with ${selectedPiece.display_label} using ${selectedPiece.selected_color_names.join(", ")}.`,
      customer_summary: `Selected ${selectedPiece.display_label}. Also considered: ${consideredLabels.join(", ") || "none yet"}.`
    };
  }

  function formatAxes(axes) {
    return Object.entries(axes)
      .map(([key, value]) => `${key.replaceAll("_", " ")}: ${value}`)
      .join("; ");
  }

  function renderSummaryHtml(state) {
    const payload = buildDesignPayload(state);
    const selected = payload.selected_pieces[0];
    const facts = selected.render_facts;
    const consideredLabels = labelsForFamilyIds(payload.pieces_considered);
    const clusterText = facts.estimated_clusters === null
      ? "Not a fixed-cluster build"
      : `${facts.estimated_clusters} clusters`;
    const variantText = selected.variant_count > 0
      ? `${selected.variant_count} catalog variants represented`
      : "Rule-based custom size from product specs";

    return `
      <dl class="summary-list">
        <dt>Event context</dt><dd>${escapeHtml(payload.event_context)}</dd>
        <dt>Product family</dt><dd>${escapeHtml(selected.display_label)}</dd>
        <dt>Source variants</dt><dd>${escapeHtml(variantText)}</dd>
        <dt>Design axes</dt><dd>${escapeHtml(formatAxes(selected.selected_variant_axes))}</dd>
        <dt>Construction</dt><dd>${escapeHtml(selected.render_facts.engine_label)}; ${escapeHtml(clusterText)}</dd>
        <dt>Balloon estimate</dt><dd>${escapeHtml(selected.render_facts.estimated_balloons)} balloons before final production review</dd>
        <dt>Colors</dt><dd>${escapeHtml(selected.selected_color_names.join(", "))}</dd>
        <dt>Pieces considered</dt><dd>${escapeHtml(consideredLabels.join(", ") || "None yet")}</dd>
        <dt>Status</dt><dd>Prototype only. No Lead, quote, save, or share action is created.</dd>
      </dl>
    `;
  }

  window.LTDesignStudio = {
    ...(window.LTDesignStudio || {}),
    buildDesignPayload,
    renderSummaryHtml
  };
})();
