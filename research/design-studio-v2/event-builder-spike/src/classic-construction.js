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
    balloons_per_foot: 8,
    clusters_per_foot: 2
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
  const estimatedBalloons = wholeQuadBalloonCount(lengthFt * preset.balloons_per_foot);
  const estimatedClusters = estimatedBalloons / CLUSTER_SIZE;

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
      estimated_balloons: estimatedBalloons,
      estimated_clusters: estimatedClusters,
      cluster_size: CLUSTER_SIZE,
      balloons_per_foot: preset.balloons_per_foot,
      pattern,
      pattern_basis: pattern === "two_color_spiral" ? "one_slot_phase_advance" : "piece_level_classic_pattern"
    }
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
  const estimatedBalloonsPerColumn = wholeQuadBalloonCount(heightFt * preset.balloons_per_foot);
  const estimatedClustersPerColumn = estimatedBalloonsPerColumn / CLUSTER_SIZE;
  const columns = 2;

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
      estimated_balloons_per_column: estimatedBalloonsPerColumn,
      estimated_clusters_per_column: estimatedClustersPerColumn,
      estimated_balloons: estimatedBalloonsPerColumn * columns,
      estimated_clusters: estimatedClustersPerColumn * columns,
      cluster_size: CLUSTER_SIZE,
      balloons_per_foot: preset.balloons_per_foot,
      pattern,
      pattern_basis: pattern === "two_color_spiral" ? "quarter_turn_phase_advance" : "piece_level_classic_pattern"
    }
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
