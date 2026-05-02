(function () {
  const {
    PIECES,
    SCALES,
    estimateArchClusters,
    estimateBackdropClusters,
    estimateColumnClusters,
    labelFor,
    pieceForId,
    scaleForId
  } = window.LTDesignStudio;

  function labelsForPieceIds(pieceIds) {
    return pieceIds.map((pieceId) => labelFor(PIECES, pieceId));
  }

  function renderFactsFor(state) {
    const scale = scaleForId(state.scale);
    if (state.piece_type === "classic_columns") {
      const heightFt = scale.id === "gym" ? 10 : scale.id === "stage" ? 8 : 7;
      return {
        construction_engine: "structured_cluster",
        count_basis: "minimum_estimate",
        estimated_clusters: estimateColumnClusters(heightFt) * 2,
        customer_visible_precision: "planning_visual"
      };
    }
    if (state.piece_type === "backdrop_wall") {
      const dimensions = scale.id === "gym" ? [12, 8] : scale.id === "stage" ? [10, 8] : [8, 8];
      return {
        construction_engine: "structured_cluster",
        count_basis: "prototype_grid",
        estimated_clusters: estimateBackdropClusters(dimensions[0], dimensions[1]),
        customer_visible_precision: "planning_visual"
      };
    }
    return {
      construction_engine: "structured_cluster",
      count_basis: "prototype_length",
      estimated_clusters: estimateArchClusters(scale.feet),
      customer_visible_precision: "planning_visual"
    };
  }

  function buildDesignPayload(state) {
    const selectedPiece = pieceForId(state.piece_type);
    const consideredLabels = labelsForPieceIds(state.pieces_considered);
    return {
      schema_version: state.schema_version,
      source: "research_prototype",
      customer_facing_path: "Plan Custom Decor",
      event_context: state.event_context,
      selected_pieces: [
        {
          piece_type: state.piece_type,
          display_label: selectedPiece.label,
          style: state.style,
          scale: labelFor(SCALES, state.scale),
          selected_color_names: state.selected_color_names,
          render_facts: renderFactsFor(state)
        }
      ],
      pieces_considered: state.pieces_considered,
      declined_suggestions: state.pieces_considered.map((pieceId) => ({
        piece_type: pieceId,
        display_label: labelFor(PIECES, pieceId),
        reason: "Shown as a complementary planning option in the prototype."
      })),
      render_summary: {
        type: "planning_visualization",
        disclaimer: state.disclaimer
      },
      sales_summary: `${state.event_context} decor starting point with ${selectedPiece.label} using ${state.selected_color_names.join(", ")}.`,
      customer_summary: `Selected ${selectedPiece.label}. Also considered: ${consideredLabels.join(", ") || "none yet"}.`
    };
  }

  function renderSummaryHtml(state) {
    const payload = buildDesignPayload(state);
    const selected = payload.selected_pieces[0];
    const consideredLabels = labelsForPieceIds(payload.pieces_considered);
    return `
      <dl class="summary-list">
        <dt>Event context</dt><dd>${payload.event_context}</dd>
        <dt>Starting piece</dt><dd>${selected.display_label}</dd>
        <dt>Style and scale</dt><dd>${selected.style}; ${selected.scale}</dd>
        <dt>Colors</dt><dd>${selected.selected_color_names.join(", ")}</dd>
        <dt>Pieces considered</dt><dd>${consideredLabels.join(", ") || "None yet"}</dd>
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
