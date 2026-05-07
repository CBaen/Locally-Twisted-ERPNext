export const EVENT_PLAYGROUND_SCHEMA_VERSION = "event-playground-v2";
export const DESIGN_STUDIO_CONTRACT_VERSION = "design-studio-v1";

export const PLANNING_DISCLAIMER =
  "Planning visualization only. Balloon counts, install method, pricing, and safety details are confirmed by Locally Twisted before booking.";

export const LEVELS = Object.freeze([
  {
    id: "school_gym",
    label: "School Gym",
    dimensions_ft: { width: 28, depth: 18, height: 12 },
    surface: "gym_floor",
    audience: "school and graduation events"
  },
  {
    id: "corporate_lobby",
    label: "Corporate Lobby",
    dimensions_ft: { width: 26, depth: 16, height: 11 },
    surface: "polished_lobby",
    audience: "business entrances and branded events"
  },
  {
    id: "backyard_patio",
    label: "Backyard Patio",
    dimensions_ft: { width: 24, depth: 16, height: 10 },
    surface: "patio",
    audience: "private parties and family celebrations"
  },
  {
    id: "community_room",
    label: "Community Room",
    dimensions_ft: { width: 26, depth: 18, height: 10 },
    surface: "neutral_room",
    audience: "church, city, and HOA gatherings"
  },
  {
    id: "car_dealership_lite",
    label: "Car Dealership",
    dimensions_ft: { width: 30, depth: 18, height: 13 },
    surface: "showroom",
    audience: "showroom and grand-opening displays"
  }
]);

export const COLOR_SWATCHES = Object.freeze([
  { name: "Berry", hex: "#b31b34" },
  { name: "Pearl White", hex: "#f8f1e6" },
  { name: "Reflex Gold", hex: "#c89d34" },
  { name: "Deep Navy", hex: "#0e2240" },
  { name: "Slate", hex: "#2f3a4a" },
  { name: "Sage", hex: "#8fa77f" },
  { name: "Coral", hex: "#d96c58" },
  { name: "Sky", hex: "#84a9c0" }
]);

export const MATERIAL_OPTIONS = Object.freeze([
  { id: "standard_latex", label: "Standard latex" },
  { id: "pearl_latex", label: "Pearl latex" },
  { id: "reflex_latex", label: "Reflex latex" },
  { id: "jewel_latex", label: "Jewel latex" }
]);

export const PATTERN_OPTIONS = Object.freeze([
  { id: "solid", label: "Solid" },
  { id: "two_color_spiral", label: "Two-color spiral" },
  { id: "color_blocks", label: "Color blocks" }
]);

export const PIECE_DEFINITIONS = Object.freeze([
  {
    id: "classic_arch",
    label: "Classic Arch",
    kind: "balloon_piece",
    product_family: "classic_arch",
    construction_engine: "structured_quad",
    physical_status: "production-plausible",
    default_colors: ["Berry", "Pearl White"],
    default_pattern: "two_color_spiral",
    default_material: "standard_latex",
    default_size: "medium",
    dimensions_ft: { width: 13.5, depth: 1.4, height: 7.4 },
    render_facts: {
      balloon_size_in: 11,
      construction_basis: "classic_4_balloon_quad_cluster",
      orientation_basis: "neck_and_knot_point_to_shared_quad_tie_center",
      render_cluster_count: 50,
      render_balloon_count: 200,
      visual_density_basis: "8 balloons/ft render density; not quote math",
      estimated_clusters: 50,
      estimated_balloons: 200,
      knots_visible: true
    },
    production_estimate: {
      status: "candidate_pending_lt_approval",
      quote_ready: false,
      customer_visible: false,
      formula_basis: "candidate_11in_classic_spiral_arch_6_balloons_per_ft",
      production_balloons_per_foot: 6,
      base_balloon_count: 152,
      overage_rate: 0.12,
      planning_balloon_count_with_overage: 172,
      fill_method: "air",
      support_required: "frame_or_monofilament_with_weights",
      venue_review_required: true,
      disclaimer: PLANNING_DISCLAIMER
    }
  },
  {
    id: "column_pair",
    label: "Column Pair",
    kind: "balloon_piece",
    product_family: "classic_column_pair",
    construction_engine: "structured_quad",
    physical_status: "production-plausible",
    default_colors: ["Reflex Gold", "Pearl White"],
    default_pattern: "two_color_spiral",
    default_material: "standard_latex",
    default_size: "medium",
    dimensions_ft: { width: 16.8, depth: 1.2, height: 7.2 },
    render_facts: {
      balloon_size_in: 11,
      construction_basis: "classic_4_balloon_quad_cluster",
      orientation_basis: "neck_and_knot_point_to_shared_quad_tie_center",
      render_cluster_count: 32,
      render_balloon_count: 128,
      visual_density_basis: "8 balloons/ft render density; not quote math",
      estimated_clusters: 32,
      estimated_balloons: 128,
      knots_visible: true
    },
    production_estimate: {
      status: "candidate_pending_lt_approval",
      quote_ready: false,
      customer_visible: false,
      formula_basis: "candidate_11in_column_4_balloons_per_ft_per_column",
      production_balloons_per_foot: 4,
      base_balloon_count: 64,
      overage_rate: 0.12,
      planning_balloon_count_with_overage: 72,
      fill_method: "air",
      support_required: "pole_base_and_weight",
      venue_review_required: true,
      disclaimer: PLANNING_DISCLAIMER
    }
  },
  {
    id: "balloon_wall",
    label: "Balloon Wall",
    kind: "balloon_piece",
    product_family: "balloon_wall_photo_moment",
    construction_engine: "classic_grid",
    physical_status: "production-plausible",
    default_colors: ["Deep Navy", "Berry"],
    default_pattern: "color_blocks",
    default_material: "standard_latex",
    default_size: "large",
    dimensions_ft: { width: 8, depth: 0.8, height: 7 },
    render_facts: {
      balloon_size_in: 11,
      construction_basis: "packed_grid",
      orientation_basis: "not_modeled_for_public_manufacturing_yet",
      render_cluster_count: 45,
      render_balloon_count: 180,
      visual_density_basis: "packed visual wall density; not quote math",
      estimated_clusters: 45,
      estimated_balloons: 180,
      knots_visible: true
    },
    production_estimate: {
      status: "lt_recipe_required",
      quote_ready: false,
      customer_visible: false,
      formula_basis: "wall_recipe_pending_lt_approval",
      fill_method: "air",
      support_required: "backdrop_frame_or_wall_system",
      venue_review_required: true,
      disclaimer: PLANNING_DISCLAIMER
    }
  },
  {
    id: "table_centerpiece",
    label: "Centerpiece",
    kind: "balloon_piece",
    product_family: "table_centerpiece",
    construction_engine: "small_classic_cluster",
    physical_status: "production-plausible",
    default_colors: ["Reflex Gold", "Pearl White"],
    default_pattern: "solid",
    default_material: "standard_latex",
    default_size: "small",
    dimensions_ft: { width: 2.2, depth: 2.2, height: 3.5 },
    render_facts: {
      balloon_size_in: 11,
      construction_basis: "small_cluster",
      orientation_basis: "neck_and_knot_point_to_shared_quad_tie_center",
      render_cluster_count: 3,
      render_balloon_count: 12,
      visual_density_basis: "small cluster visual count; not quote math",
      estimated_clusters: 3,
      estimated_balloons: 12,
      knots_visible: true
    },
    production_estimate: {
      status: "lt_recipe_required",
      quote_ready: false,
      customer_visible: false,
      formula_basis: "centerpiece_recipe_pending_lt_approval",
      fill_method: "air",
      support_required: "table_safe_base",
      venue_review_required: true,
      disclaimer: PLANNING_DISCLAIMER
    }
  },
  {
    id: "welcome_sign_cluster",
    label: "Welcome Sign",
    kind: "balloon_piece",
    product_family: "welcome_sign_cluster",
    construction_engine: "small_classic_cluster",
    physical_status: "production-plausible",
    default_colors: ["Berry", "Reflex Gold"],
    default_pattern: "solid",
    default_material: "pearl_latex",
    default_size: "medium",
    dimensions_ft: { width: 4, depth: 1.6, height: 5.2 },
    render_facts: {
      balloon_size_in: 11,
      construction_basis: "sign_cluster",
      orientation_basis: "neck_and_knot_point_to_shared_quad_tie_center",
      render_cluster_count: 7,
      render_balloon_count: 28,
      visual_density_basis: "sign cluster visual count; not quote math",
      estimated_clusters: 7,
      estimated_balloons: 28,
      knots_visible: true
    },
    production_estimate: {
      status: "lt_recipe_required",
      quote_ready: false,
      customer_visible: false,
      formula_basis: "sign_cluster_recipe_pending_lt_approval",
      fill_method: "air",
      support_required: "weighted_easel_or_sign_base",
      venue_review_required: true,
      disclaimer: PLANNING_DISCLAIMER
    }
  }
]);

export const PROP_DEFINITIONS = Object.freeze([
  {
    id: "linen_table",
    label: "Linen Table",
    kind: "prop",
    product_family: "linen_table",
    default_color: "Pearl White",
    dimensions_ft: { width: 5.5, depth: 2.5, height: 2.5 }
  },
  {
    id: "chair",
    label: "Chair",
    kind: "prop",
    product_family: "chair",
    default_color: "Slate",
    dimensions_ft: { width: 1.5, depth: 1.5, height: 3 }
  },
  {
    id: "sign_easel",
    label: "Sign Easel",
    kind: "prop",
    product_family: "sign_easel",
    default_color: "Reflex Gold",
    dimensions_ft: { width: 2.2, depth: 1.1, height: 4.5 }
  },
  {
    id: "scale_person",
    label: "Scale Person",
    kind: "prop",
    product_family: "scale_person",
    default_color: "Deep Navy",
    dimensions_ft: { width: 1.2, depth: 0.6, height: 5.7 }
  },
  {
    id: "display_car",
    label: "Display Car",
    kind: "prop",
    product_family: "display_car",
    default_color: "Slate",
    dimensions_ft: { width: 7, depth: 3.4, height: 2.6 }
  }
]);

export const SUGGESTIONS = Object.freeze([
  { id: "complete_entrance", label: "Complete the entrance" },
  { id: "add_matching_columns", label: "Add matching columns" },
  { id: "carry_colors_to_tables", label: "Carry the colors to tables" },
  { id: "add_photo_moment", label: "Add a photo moment" }
]);

const STARTING_ITEMS = Object.freeze([
  { definitionId: "classic_arch", x_ft: 0, z_ft: 2.8, rotation_deg: 0 },
  { definitionId: "column_pair", x_ft: 0, z_ft: -1.8, rotation_deg: 0 },
  { definitionId: "linen_table", x_ft: -5.8, z_ft: -3.4, rotation_deg: 0 }
]);

export function createEventPlaygroundState() {
  const state = {
    levels: clone(LEVELS),
    level_id: "school_gym",
    palette: {
      pieces: clone(PIECE_DEFINITIONS),
      props: clone(PROP_DEFINITIONS),
      colors: clone(COLOR_SWATCHES),
      materials: clone(MATERIAL_OPTIONS),
      patterns: clone(PATTERN_OPTIONS)
    },
    suggestions: clone(SUGGESTIONS),
    accepted_suggestions: [],
    ignored_suggestions: [],
    placedItems: [],
    selectedItemId: null,
    view: {
      stage_rotation_deg: 0,
      pan_x_ft: 0,
      pan_z_ft: 0
    },
    sequence: 1
  };

  for (const item of STARTING_ITEMS) {
    addItemFromDefinition(state, item.definitionId, item);
  }
  state.selectedItemId = "classic_arch_1";
  return state;
}

export function getCurrentLevel(state) {
  return state.levels.find((level) => level.id === state.level_id) || state.levels[0];
}

export function setLevel(state, levelId) {
  if (state.levels.some((level) => level.id === levelId)) {
    state.level_id = levelId;
  }
  return getCurrentLevel(state);
}

export function addPiece(state, definitionId) {
  return addItemFromDefinition(state, definitionId, {
    x_ft: 1.2,
    z_ft: 0.8,
    rotation_deg: 0
  });
}

export function addProp(state, definitionId) {
  return addItemFromDefinition(state, definitionId, {
    x_ft: -2.6,
    z_ft: -2.2,
    rotation_deg: 0
  });
}

export function selectItem(state, itemId) {
  if (state.placedItems.some((item) => item.id === itemId)) {
    state.selectedItemId = itemId;
  }
  return getSelectedItem(state);
}

export function getSelectedItem(state) {
  return state.placedItems.find((item) => item.id === state.selectedItemId) || state.placedItems[0] || null;
}

export function moveSelectedItem(state, deltaXFt, deltaZFt) {
  const item = getSelectedItem(state);
  if (!item) return null;
  const level = getCurrentLevel(state);
  const halfWidth = level.dimensions_ft.width / 2;
  const halfDepth = level.dimensions_ft.depth / 2;
  item.placement.x_ft = round(clamp(item.placement.x_ft + deltaXFt, -halfWidth + 0.8, halfWidth - 0.8));
  item.placement.z_ft = round(clamp(item.placement.z_ft + deltaZFt, -halfDepth + 0.8, halfDepth - 0.8));
  updateWarnings(state);
  return item;
}

export function setSelectedPieceRotation(state, rotationDeg) {
  const item = getSelectedItem(state);
  if (!item) return null;
  item.placement.rotation_deg = normalizeRotation(rotationDeg);
  return item;
}

export function rotateSelectedPiece(state, deltaDeg) {
  const item = getSelectedItem(state);
  if (!item) return null;
  return setSelectedPieceRotation(state, item.placement.rotation_deg + deltaDeg);
}

export function setSelectedPieceColors(state, colorNames) {
  const item = getSelectedItem(state);
  if (!item || item.kind !== "balloon_piece") return null;
  const validNames = new Set(COLOR_SWATCHES.map((color) => color.name));
  item.selected_colors = colorNames.filter((name) => validNames.has(name));
  if (!item.selected_colors.length) item.selected_colors = ["Pearl White"];
  return item;
}

export function setSelectedPiecePattern(state, patternId) {
  const item = getSelectedItem(state);
  if (!item || item.kind !== "balloon_piece") return null;
  if (PATTERN_OPTIONS.some((pattern) => pattern.id === patternId)) {
    item.pattern = patternId;
  }
  return item;
}

export function setSelectedPieceMaterial(state, materialId) {
  const item = getSelectedItem(state);
  if (!item || item.kind !== "balloon_piece") return null;
  if (MATERIAL_OPTIONS.some((material) => material.id === materialId)) {
    item.material = materialId;
  }
  return item;
}

export function setSelectedItemSize(state, size) {
  const item = getSelectedItem(state);
  if (!item) return null;
  if (["small", "medium", "large"].includes(size)) {
    item.size = size;
    item.scale = size === "small" ? 0.78 : size === "large" ? 1.18 : 1;
  }
  return item;
}

export function duplicateSelectedPiece(state) {
  const selected = getSelectedItem(state);
  if (!selected) return null;
  const duplicate = clone(selected);
  duplicate.id = `${selected.definition_id}_${state.sequence++}`;
  duplicate.duplicated_from_id = selected.id;
  duplicate.placement.x_ft = round(selected.placement.x_ft + 1);
  duplicate.placement.z_ft = round(selected.placement.z_ft - 0.8);
  state.placedItems.push(duplicate);
  state.selectedItemId = duplicate.id;
  return duplicate;
}

export function deleteSelectedPiece(state) {
  if (state.placedItems.length <= 1) return false;
  const selected = getSelectedItem(state);
  if (!selected) return false;
  const index = state.placedItems.findIndex((item) => item.id === selected.id);
  if (index === -1) return false;
  const [removed] = state.placedItems.splice(index, 1);
  const source = removed.duplicated_from_id
    ? state.placedItems.find((item) => item.id === removed.duplicated_from_id)
    : null;
  state.selectedItemId = source?.id || state.placedItems[Math.max(0, index - 1)]?.id || state.placedItems[0]?.id || null;
  return true;
}

export function setStageRotation(state, rotationDeg) {
  state.view.stage_rotation_deg = normalizeRotation(rotationDeg);
  return state.view.stage_rotation_deg;
}

export function turnStage(state, deltaDeg) {
  return setStageRotation(state, state.view.stage_rotation_deg + deltaDeg);
}

export function acceptSuggestion(state, suggestionId) {
  if (!SUGGESTIONS.some((suggestion) => suggestion.id === suggestionId)) return state.accepted_suggestions;
  state.ignored_suggestions = state.ignored_suggestions.filter((id) => id !== suggestionId);
  if (!state.accepted_suggestions.includes(suggestionId)) state.accepted_suggestions.push(suggestionId);
  return state.accepted_suggestions;
}

export function ignoreSuggestion(state, suggestionId) {
  if (!SUGGESTIONS.some((suggestion) => suggestion.id === suggestionId)) return state.ignored_suggestions;
  state.accepted_suggestions = state.accepted_suggestions.filter((id) => id !== suggestionId);
  if (!state.ignored_suggestions.includes(suggestionId)) state.ignored_suggestions.push(suggestionId);
  return state.ignored_suggestions;
}

export function createEventPlaygroundPayload(state, options = {}) {
  updateWarnings(state);
  const level = getCurrentLevel(state);
  const contact = options.contact || {};
  const screenshotReference = options.screenshotReference || null;
  const handoffState = options.handoffState || "not_started";
  const placedBalloonPieces = state.placedItems.filter((item) => item.kind === "balloon_piece");
  const placedProps = state.placedItems.filter((item) => item.kind === "prop");
  const payload = {
    schema_version: EVENT_PLAYGROUND_SCHEMA_VERSION,
    level_id: state.level_id,
    venue_dimensions: clone(level.dimensions_ft),
    preset: {
      label: level.label,
      surface: level.surface,
      audience: level.audience
    },
    placed_balloon_pieces: placedBalloonPieces.map(payloadForItem),
    placed_props: placedProps.map(payloadForItem),
    positions_rotations_scales: state.placedItems.map((item) => ({
      id: item.id,
      x_ft: round(item.placement.x_ft),
      z_ft: round(item.placement.z_ft),
      rotation_deg: round(item.placement.rotation_deg, 1),
      scale: round(item.scale, 2)
    })),
    selected_colors_materials_patterns: placedBalloonPieces.map((item) => ({
      id: item.id,
      colors: [...item.selected_colors],
      material: item.material,
      pattern: item.pattern,
      size: item.size
    })),
    screenshot_reference: screenshotReference,
    upsell_suggestions: {
      accepted: [...state.accepted_suggestions],
      ignored: [...state.ignored_suggestions]
    },
    customer_contact_handoff_state: handoffState,
    customer_contact: {
      customer_name: contact.customer_name || "",
      email: contact.email || "",
      phone: contact.phone || "",
      event_date: contact.event_date || "",
      event_city: contact.event_city || ""
    },
    customer_note: PLANNING_DISCLAIMER,
    warnings: collectWarnings(state),
    integration_adapter: {
      target_contract: DESIGN_STUDIO_CONTRACT_VERSION,
      frappe_route_recommendation: "/plan-custom-decor",
      submit_endpoint_recommendation: "locally_twisted.api.design_studio.submit_design_inquiry",
      save_endpoint_recommendation: "locally_twisted.api.design_studio.save_design",
      lead_creation_policy: "create_exactly_one_lead_after_server_validation",
      source_channel: "Plan Custom Decor"
    },
    generated_at: new Date().toISOString()
  };
  payload.design_studio_contract = createDesignStudioContract(payload, contact, level);
  return payload;
}

function addItemFromDefinition(state, definitionId, placement = {}) {
  const definition = findDefinition(definitionId);
  if (!definition) {
    throw new Error(`Unknown Event Playground item: ${definitionId}`);
  }
  const countForDefinition = state.placedItems.filter((item) => item.definition_id === definitionId).length + 1;
  const item = {
    id: `${definitionId}_${countForDefinition === 1 ? 1 : state.sequence}`,
    definition_id: definition.id,
    label: definition.label,
    kind: definition.kind,
    product_family: definition.product_family,
    construction_engine: definition.construction_engine || "context_prop",
    physical_status: definition.physical_status || "context-only",
    selected_colors: [...(definition.default_colors || [definition.default_color || "Pearl White"])],
    material: definition.default_material || "context_material",
    pattern: definition.default_pattern || "context",
    size: definition.default_size || "medium",
    scale: definition.default_size === "small" ? 0.78 : definition.default_size === "large" ? 1.18 : 1,
    dimensions_ft: clone(definition.dimensions_ft),
    render_facts: clone(definition.render_facts || {}),
    production_estimate: clone(definition.production_estimate || { status: "not_applicable", quote_ready: false }),
    placement: {
      x_ft: round(placement.x_ft ?? 0),
      z_ft: round(placement.z_ft ?? 0),
      rotation_deg: normalizeRotation(placement.rotation_deg ?? 0)
    },
    warnings: []
  };
  state.sequence += 1;
  state.placedItems.push(item);
  state.selectedItemId = item.id;
  return item;
}

function payloadForItem(item) {
  return {
    id: item.id,
    label: item.label,
    product_family: item.product_family,
    construction_engine: item.construction_engine,
    physical_status: item.physical_status,
    selected_colors: [...item.selected_colors],
    material: item.material,
    pattern: item.pattern,
    size: item.size,
    dimensions_ft: clone(item.dimensions_ft),
    render_facts: clone(item.render_facts),
    production_estimate: clone(item.production_estimate),
    placement: {
      x_ft: round(item.placement.x_ft),
      z_ft: round(item.placement.z_ft),
      rotation_deg: round(item.placement.rotation_deg, 1)
    },
    scale: round(item.scale, 2),
    warnings: [...(item.warnings || [])]
  };
}

export function updateWarnings(state) {
  const level = getCurrentLevel(state);
  const halfWidth = level.dimensions_ft.width / 2;
  const halfDepth = level.dimensions_ft.depth / 2;
  state.placedItems.forEach((item) => {
    const warnings = [];
    const nearEdge = Math.abs(item.placement.x_ft) > halfWidth - 2.5 || Math.abs(item.placement.z_ft) > halfDepth - 2.5;
    if (nearEdge) {
      warnings.push({
        code: "venue_edge_review",
        severity: "review",
        message: "Close to a venue edge; Locally Twisted should confirm walkways, exits, weights, and install clearance."
      });
    }
    if (item.kind === "balloon_piece" && item.production_estimate?.quote_ready === false) {
      warnings.push({
        code: "quote_math_pending_lt_approval",
        severity: "info",
        message: "Render density is separate from quote math; final balloon count and install method require LT approval."
      });
    }
    item.warnings = warnings;
  });
  return collectWarnings(state);
}

function collectWarnings(state) {
  const byCode = new Map();
  state.placedItems.forEach((item) => {
    (item.warnings || []).forEach((warning) => {
      const key = `${warning.code}:${warning.message}`;
      if (!byCode.has(key)) byCode.set(key, { ...warning, item_ids: [] });
      byCode.get(key).item_ids.push(item.id);
    });
  });
  return [...byCode.values()];
}

function createDesignStudioContract(payload, contact, level) {
  return {
    schema_version: DESIGN_STUDIO_CONTRACT_VERSION,
    source: "event-playground-preview",
    event: {
      venue_preset: payload.level_id,
      venue_label: payload.preset.label,
      venue_dimensions_ft: payload.venue_dimensions,
      audience: payload.preset.audience,
      event_date: contact.event_date || "",
      event_city: contact.event_city || "",
      indoor_outdoor: level.id === "backyard_patio" ? "outdoor_review_required" : "indoor_or_covered"
    },
    customer: {
      name: contact.customer_name || "",
      email: contact.email || "",
      phone: contact.phone || ""
    },
    palette: {
      selected_color_names: unique(payload.selected_colors_materials_patterns.flatMap((entry) => entry.colors || [])),
      colors_are_supplier_actionable_names: true,
      hex_values_are_approximate: true
    },
    pieces: payload.placed_balloon_pieces.map((piece) => ({
      piece_id: piece.id,
      piece_type: piece.product_family,
      display_label: piece.label,
      dimensions_ft: piece.dimensions_ft,
      style: piece.pattern,
      selected_colors: piece.selected_colors,
      material: piece.material,
      placement: piece.placement,
      rules_summary: {
        construction_engine: piece.construction_engine,
        render_facts: piece.render_facts,
        production_estimate: piece.production_estimate
      },
      warnings: piece.warnings
    })),
    suggestions: payload.upsell_suggestions,
    render: {
      renderer: "playcanvas-preview",
      screenshot_reference: payload.screenshot_reference,
      alt_summary: summarizePieces(payload.placed_balloon_pieces)
    },
    sales_summary: {
      short_summary: summarizePieces(payload.placed_balloon_pieces),
      props_considered: payload.placed_props.map((prop) => prop.label),
      warnings: payload.warnings,
      follow_up_questions: [
        "Confirm event date, venue access, and indoor/outdoor conditions.",
        "Confirm approved color matches and whether quote should include install, strike, and weights.",
        "Confirm final production formulas with Locally Twisted before pricing."
      ]
    },
    disclaimers: {
      planning_visualization_only: true,
      quote_requires_lt_review: true,
      no_customer_visible_final_balloon_count: true,
      text: PLANNING_DISCLAIMER
    }
  };
}

function summarizePieces(pieces) {
  if (!pieces.length) return "No balloon decor pieces selected yet.";
  return pieces.map((piece) => `${piece.label} (${piece.selected_colors.join(" + ")})`).join("; ");
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function findDefinition(definitionId) {
  return PIECE_DEFINITIONS.find((definition) => definition.id === definitionId)
    || PROP_DEFINITIONS.find((definition) => definition.id === definitionId);
}

function colorHexFor(name) {
  return COLOR_SWATCHES.find((color) => color.name === name)?.hex || "#f8f1e6";
}

export function getColorHex(name) {
  return colorHexFor(name);
}

export function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function round(value, places = 2) {
  const factor = 10 ** places;
  return Math.round(value * factor) / factor;
}

function normalizeRotation(value) {
  return ((value % 360) + 360) % 360;
}
