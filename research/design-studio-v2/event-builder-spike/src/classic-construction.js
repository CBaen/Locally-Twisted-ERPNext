export const CLASSIC_SCENE_VERSION = "playcanvas-classic-stage-builder-v1";

export const CLASSIC_STAGE = Object.freeze({
  venue: "corporate_stage",
  width_ft: 24,
  depth_ft: 12,
  tile_size_ft: 1,
  unit_rule: "1 engine unit = 1 ft"
});

export const CLASSIC_COLOR_HEX = Object.freeze({
  "Reflex Gold": "#c89d34",
  "Deep Teal": "#087b83",
  "Pearl White": "#f4efe4",
  "Sage": "#8fa77f",
  "Blush": "#d58f92",
  "Charcoal": "#30373b",
  "Copper": "#ba6f42",
  "Navy": "#1d3557"
});

const BALLOON_PRESETS = Object.freeze({
  11: {
    label: "11_in",
    diameter_ft: 0.9167,
    render_balloons_per_foot: 8,
    render_clusters_per_foot: 2,
    production_arch_balloons_per_foot: 6,
    production_column_balloons_per_foot: 4,
    production_overage_rate: 0.12,
    production_formula_status: "candidate_pending_lt_approval",
    production_formula_sources: [
      "burton_and_burton_spiral_arch_11in_6_per_ft",
      "public_column_guidance_11in_4_per_tier_1_tier_per_ft"
    ]
  }
});

const STRUCTURED_QUAD = "structured_quad";
const QUAD_BASIS = "classic_4_balloon_quad_cluster";
const CLUSTER_SIZE = 4;

export function createClassicArch({
  id,
  lengthFt = 25,
  balloonSizeIn = 11,
  pattern = "two_color_spiral",
  selectedColorNames = ["Reflex Gold", "Deep Teal"],
  placement = { x_ft: 0, y_ft: -3.2, rotation_deg: 0 }
}) {
  const preset = getBalloonPreset(balloonSizeIn);
  const renderBalloons = wholeQuadBalloonCount(lengthFt * preset.render_balloons_per_foot);
  const renderClusters = renderBalloons / CLUSTER_SIZE;
  const productionEstimate = createProductionEstimate({
    pieceType: "classic_arch",
    measureFt: lengthFt,
    preset
  });

  return {
    id,
    product_family: "classic_arch",
    design_id: `classic_arch_${pattern}`,
    construction_engine: STRUCTURED_QUAD,
    requested_dimensions: {
      length_ft: round(lengthFt, 2)
    },
    render_dimensions: {
      length_ft: round(lengthFt, 2)
    },
    balloon_size_preset: preset.label,
    pattern,
    selected_color_names: normalizeColorNames(selectedColorNames),
    placement: normalizePlacement(placement),
    render_facts: {
      construction_basis: QUAD_BASIS,
      length_ft: round(lengthFt, 2),
      balloon_diameter_ft: preset.diameter_ft,
      render_balloon_count: renderBalloons,
      render_cluster_count: renderClusters,
      visual_density_basis: "render_density_not_quote_math",
      render_balloons_per_foot: preset.render_balloons_per_foot,
      estimated_balloons: renderBalloons,
      estimated_clusters: renderClusters,
      cluster_size: CLUSTER_SIZE,
      balloons_per_foot: preset.render_balloons_per_foot,
      pattern,
      pattern_basis: pattern === "two_color_spiral" ? "one_slot_phase_advance" : "piece_level_classic_pattern"
    },
    production_estimate: productionEstimate
  };
}

export function createClassicColumnPair({
  id,
  heightFt = 8,
  balloonSizeIn = 11,
  pattern = "two_color_spiral",
  selectedColorNames = ["Pearl White", "Reflex Gold"],
  placement = { x_ft: 0, y_ft: 1.8, rotation_deg: 0 }
}) {
  const preset = getBalloonPreset(balloonSizeIn);
  const renderBalloonsPerColumn = wholeQuadBalloonCount(heightFt * preset.render_balloons_per_foot);
  const renderClustersPerColumn = renderBalloonsPerColumn / CLUSTER_SIZE;
  const columns = 2;
  const productionEstimate = createProductionEstimate({
    pieceType: "classic_column_pair",
    measureFt: heightFt,
    preset,
    columns
  });

  return {
    id,
    product_family: "classic_column_pair",
    design_id: `classic_column_pair_${pattern}`,
    construction_engine: STRUCTURED_QUAD,
    requested_dimensions: {
      height_ft: round(heightFt, 2),
      columns
    },
    render_dimensions: {
      height_ft: round(heightFt, 2),
      pair_width_ft: 18.4
    },
    balloon_size_preset: preset.label,
    pattern,
    selected_color_names: normalizeColorNames(selectedColorNames),
    placement: normalizePlacement(placement),
    render_facts: {
      construction_basis: QUAD_BASIS,
      height_ft: round(heightFt, 2),
      columns,
      balloon_diameter_ft: preset.diameter_ft,
      render_balloons_per_column: renderBalloonsPerColumn,
      render_clusters_per_column: renderClustersPerColumn,
      render_balloon_count: renderBalloonsPerColumn * columns,
      render_cluster_count: renderClustersPerColumn * columns,
      visual_density_basis: "render_density_not_quote_math",
      estimated_balloons_per_column: renderBalloonsPerColumn,
      estimated_clusters_per_column: renderClustersPerColumn,
      estimated_balloons: renderBalloonsPerColumn * columns,
      estimated_clusters: renderClustersPerColumn * columns,
      cluster_size: CLUSTER_SIZE,
      render_balloons_per_foot: preset.render_balloons_per_foot,
      balloons_per_foot: preset.render_balloons_per_foot,
      pattern,
      pattern_basis: pattern === "two_color_spiral" ? "quarter_turn_phase_advance" : "piece_level_classic_pattern"
    },
    production_estimate: productionEstimate
  };
}

function createProductionEstimate({ pieceType, measureFt, preset, columns = 1 }) {
  const density = pieceType === "classic_column_pair"
    ? preset.production_column_balloons_per_foot
    : preset.production_arch_balloons_per_foot;
  const baseBalloonsEach = wholeQuadBalloonCount(measureFt * density);
  const baseBalloons = baseBalloonsEach * columns;
  const overageBalloons = wholeQuadBalloonCount(baseBalloons * preset.production_overage_rate);
  return {
    status: preset.production_formula_status,
    quote_ready: false,
    customer_visible: false,
    formula_basis: pieceType === "classic_column_pair"
      ? "candidate_11in_column_4_balloons_per_ft_per_column"
      : "candidate_11in_classic_spiral_arch_6_balloons_per_ft",
    formula_sources: [...preset.production_formula_sources],
    production_balloons_per_foot: density,
    base_balloon_count: baseBalloons,
    overage_rate: preset.production_overage_rate,
    overage_balloon_count: overageBalloons,
    planning_balloon_count_with_overage: baseBalloons + overageBalloons,
    cluster_size: CLUSTER_SIZE,
    fill_method: "air",
    support_required: pieceType === "classic_column_pair" ? "pole_base_and_weight" : "frame_or_monofilament_with_weights",
    venue_review_required: true,
    disclaimer: "Planning visualization only. Balloon counts, install method, pricing, and safety details are confirmed by Locally Twisted before booking."
  };
}

export function colorHexFor(name) {
  return CLASSIC_COLOR_HEX[name] ?? "#d8d2c7";
}

export function round(value, places = 2) {
  const factor = 10 ** places;
  return Math.round(value * factor) / factor;
}

export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function getBalloonPreset(sizeIn) {
  const preset = BALLOON_PRESETS[sizeIn];
  if (!preset) {
    throw new Error(`Unsupported classic balloon size: ${sizeIn}`);
  }
  return preset;
}

function wholeQuadBalloonCount(rawCount) {
  return Math.ceil(rawCount / CLUSTER_SIZE) * CLUSTER_SIZE;
}

function normalizeColorNames(colorNames) {
  const fallback = ["Reflex Gold", "Deep Teal"];
  const names = colorNames.length ? colorNames : fallback;
  return names.map((name) => (CLASSIC_COLOR_HEX[name] ? name : "Pearl White"));
}

function normalizePlacement(placement) {
  return {
    x_ft: round(placement.x_ft ?? 0, 2),
    y_ft: round(placement.y_ft ?? 0, 2),
    rotation_deg: normalizeRotation(placement.rotation_deg ?? 0)
  };
}

function normalizeRotation(rotationDeg) {
  return ((Math.round(rotationDeg / 90) * 90) % 360 + 360) % 360;
}
