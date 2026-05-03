export const STAGE = Object.freeze({
  venue: "corporate_stage",
  width_ft: 24,
  depth_ft: 12,
  tile_size_ft: 1,
  unit_rule: "1 engine unit = 1 ft"
});

export const BALLOON = Object.freeze({
  diameter_11_in_ft: 0.9167,
  radius_11_in_ft: 0.9167 / 2
});

export const COLOR_HEX = Object.freeze({
  "Reflex Gold": "#c89d34",
  "Deep Teal": "#087b83",
  "Pearl White": "#f4efe4",
  "Sage": "#8fa77f",
  "Blush": "#d58f92",
  "Charcoal": "#30373b",
  "Copper": "#ba6f42"
});

const ARCH_FACTS = Object.freeze({
  construction_basis: "classic_4_balloon_quad_cluster",
  length_ft: 25,
  balloon_diameter_ft: BALLOON.diameter_11_in_ft,
  estimated_balloons: 200,
  estimated_clusters: 50,
  cluster_size: 4,
  balloons_per_foot: 8,
  swirl_color_model: "two_color_candy_cane_spiral",
  swirl_phase_model: "one_slot_phase_advance",
  camera_depth_sorting: "fixed_isometric_front_to_back"
});

const COLUMN_FACTS = Object.freeze({
  construction_basis: "classic_4_balloon_quad_cluster",
  height_ft: 8,
  columns: 2,
  balloon_diameter_ft: BALLOON.diameter_11_in_ft,
  estimated_balloons_per_column: 64,
  estimated_clusters_per_column: 16,
  estimated_balloons: 128,
  estimated_clusters: 32,
  pair_count_represented: true
});

const GARLAND_FACTS = Object.freeze({
  construction_basis: "organic_strip_backbone_with_filler",
  length_ft: 9,
  balloon_diameter_ft: BALLOON.diameter_11_in_ft,
  base_balloons: 86,
  estimated_balloons: 97,
  overage_percent_used: 12.5,
  size_mix: {
    body_11: 70,
    accent_16: 8,
    hero_24: 3,
    filler_5: 16
  },
  size_layers: ["11_inch_body", "16_24_inch_anchors", "5_inch_filler"],
  visual_layers: ["primary_structure", "massing_clusters", "filler_detail"],
  constraints: ["no_touching_twins", "anchors_break_symmetry", "filler_closes_gaps"]
});

const WALL_FACTS = Object.freeze({
  construction_basis: "whole_cell_dense_balloon_grid",
  width_ft: 10,
  height_ft: 8,
  cells_wide: 10,
  cells_high: 8,
  balloon_diameter_ft: BALLOON.diameter_11_in_ft,
  estimated_clusters: 80,
  estimated_balloons: 320,
  placeholder: true
});

export const BASE_PIECES = Object.freeze([
  {
    id: "arch_1",
    product_family: "arch",
    design_id: "arch_swirl",
    placement: { x_ft: 0, y_ft: -3.2, rotation_deg: 0 },
    selected_color_names: ["Reflex Gold", "Deep Teal"],
    render_facts: ARCH_FACTS
  },
  {
    id: "column_pair_1",
    product_family: "column_pair",
    design_id: "classic_column_pair",
    placement: { x_ft: 0, y_ft: 1.7, rotation_deg: 0 },
    selected_color_names: ["Pearl White", "Reflex Gold"],
    render_facts: COLUMN_FACTS
  },
  {
    id: "garland_1",
    product_family: "garland",
    design_id: "organic_stage_swag",
    placement: { x_ft: 0, y_ft: 4.4, rotation_deg: 0 },
    selected_color_names: ["Sage", "Pearl White", "Blush"],
    render_facts: GARLAND_FACTS
  },
  {
    id: "backdrop_wall_1",
    product_family: "backdrop_wall",
    design_id: "whole_cell_balloon_wall",
    placement: { x_ft: 0, y_ft: 5.25, rotation_deg: 0 },
    selected_color_names: ["Deep Teal", "Reflex Gold", "Pearl White"],
    render_facts: WALL_FACTS
  }
]);

export function createSceneState() {
  return {
    scene_version: "event-builder-spike-v1",
    venue: STAGE.venue,
    camera: "fixed_isometric",
    pieces: clone(BASE_PIECES)
  };
}

export function createPayload(state, engine) {
  return {
    scene_version: "event-builder-spike-v1",
    venue: STAGE.venue,
    engine,
    camera: "fixed_isometric",
    pieces: state.pieces.map((piece) => ({
      id: piece.id,
      product_family: piece.product_family,
      design_id: piece.design_id,
      placement: {
        x_ft: round(piece.placement.x_ft, 2),
        y_ft: round(piece.placement.y_ft, 2),
        rotation_deg: round(piece.placement.rotation_deg, 1)
      },
      selected_color_names: [...piece.selected_color_names],
      render_facts: clone(piece.render_facts)
    })),
    sales_summary: "Corporate stage concept with arch, columns, and garland."
  };
}

export function createRuntimeState(engine, lastRenderMs = 0) {
  return {
    engine,
    camera: "fixed_isometric",
    camera_controls: "disabled",
    stage: {
      venue: STAGE.venue,
      width_ft: STAGE.width_ft,
      depth_ft: STAGE.depth_ft,
      unit_rule: STAGE.unit_rule
    },
    grid: {
      tile_size_ft: STAGE.tile_size_ft,
      visible: true
    },
    performance: {
      last_render_ms: round(lastRenderMs, 2)
    }
  };
}

export function createStageObjects() {
  const objects = [
    {
      id: "stage_floor",
      type: "box",
      color: "#d8caba",
      position: { x: 0, y: -0.07, z: 0 },
      scale: { x: STAGE.width_ft, y: 0.12, z: STAGE.depth_ft }
    },
    {
      id: "back_scrim",
      type: "box",
      color: "#becac4",
      position: { x: 0, y: 4.2, z: STAGE.depth_ft / 2 + 0.08 },
      scale: { x: STAGE.width_ft, y: 8.4, z: 0.14 }
    },
    {
      id: "front_lip",
      type: "box",
      color: "#8e7058",
      position: { x: 0, y: 0.15, z: -STAGE.depth_ft / 2 - 0.12 },
      scale: { x: STAGE.width_ft, y: 0.3, z: 0.24 }
    }
  ];

  for (let x = -STAGE.width_ft / 2; x <= STAGE.width_ft / 2; x += STAGE.tile_size_ft) {
    objects.push({
      id: `grid_x_${x}`,
      type: "box",
      color: x % 5 === 0 ? "#9aa9a5" : "#c4d0cc",
      position: { x, y: 0.015, z: 0 },
      scale: { x: x % 5 === 0 ? 0.045 : 0.025, y: 0.035, z: STAGE.depth_ft }
    });
  }

  for (let z = -STAGE.depth_ft / 2; z <= STAGE.depth_ft / 2; z += STAGE.tile_size_ft) {
    objects.push({
      id: `grid_z_${z}`,
      type: "box",
      color: z % 5 === 0 ? "#9aa9a5" : "#c4d0cc",
      position: { x: 0, y: 0.02, z },
      scale: { x: STAGE.width_ft, y: 0.035, z: z % 5 === 0 ? 0.045 : 0.025 }
    });
  }

  return objects;
}

export function createSceneObjects(state) {
  const objects = [...createStageObjects()];
  for (const piece of state.pieces) {
    if (piece.id === "arch_1") {
      objects.push(...createArchObjects(piece));
    }
    if (piece.id === "column_pair_1") {
      objects.push(...createColumnPairObjects(piece));
    }
    if (piece.id === "garland_1") {
      objects.push(...createGarlandObjects(piece));
    }
    if (piece.id === "backdrop_wall_1") {
      objects.push(...createBackdropWallObjects(piece));
    }
  }
  return objects.sort((a, b) => {
    const az = a.position?.z ?? 0;
    const bz = b.position?.z ?? 0;
    const ay = a.position?.y ?? 0;
    const by = b.position?.y ?? 0;
    return bz - az || ay - by;
  });
}

export function getPieceAnchor(piece) {
  if (piece.id === "arch_1") {
    return { x: piece.placement.x_ft, y: 4.9, z: piece.placement.y_ft };
  }
  if (piece.id === "column_pair_1") {
    return { x: piece.placement.x_ft, y: 4.3, z: piece.placement.y_ft };
  }
  if (piece.id === "garland_1") {
    return { x: piece.placement.x_ft, y: 7.7, z: piece.placement.y_ft };
  }
  return { x: piece.placement.x_ft, y: 4.6, z: piece.placement.y_ft };
}

export function projectWorldToScreen(worldPoint, rect) {
  const scale = Math.min(rect.width / 30, rect.height / 20);
  return {
    x: rect.left + rect.width * 0.5 + (worldPoint.x - worldPoint.z) * scale * 0.86,
    y: rect.top + rect.height * 0.6 + (worldPoint.x + worldPoint.z) * scale * 0.34 - worldPoint.y * scale * 0.92
  };
}

export function movePieceByScreenDelta(piece, deltaX, deltaY, rect) {
  const scale = Math.min(rect.width / 30, rect.height / 20);
  const isoX = deltaX / (scale * 0.86);
  const isoY = deltaY / (scale * 0.34);
  const deltaStageX = (isoX + isoY) / 2;
  const deltaStageZ = (isoY - isoX) / 2;
  piece.placement.x_ft = clamp(piece.placement.x_ft + deltaStageX, -5.5, 5.5);
  piece.placement.y_ft = clamp(piece.placement.y_ft + deltaStageZ, -4.8, 4.8);
}

function createArchObjects(piece) {
  const objects = [];
  const radius = piece.render_facts.length_ft / Math.PI;
  const clusterOffsets = [
    { x: -0.26, y: 0.02, z: -0.28 },
    { x: 0.26, y: 0.02, z: 0.28 },
    { x: -0.02, y: 0.33, z: 0.02 },
    { x: 0.02, y: -0.3, z: -0.02 }
  ];
  for (let cluster = 0; cluster < piece.render_facts.estimated_clusters; cluster += 1) {
    const t = cluster / (piece.render_facts.estimated_clusters - 1);
    const theta = Math.PI - t * Math.PI;
    const base = {
      x: piece.placement.x_ft + Math.cos(theta) * radius,
      y: 0.72 + Math.sin(theta) * radius,
      z: piece.placement.y_ft
    };
    clusterOffsets.forEach((offset, slot) => {
      const colorName = (cluster + Math.floor(slot / 2)) % 2 === 0 ? piece.selected_color_names[0] : piece.selected_color_names[1];
      addBalloon(objects, {
        id: `${piece.id}_c${cluster}_b${slot}`,
        pieceId: piece.id,
        colorName,
        x: base.x + offset.x,
        y: base.y + offset.y,
        z: base.z + offset.z,
        radius: BALLOON.radius_11_in_ft,
        squash: { x: 1.02, y: 0.94, z: 0.88 },
        knot: slot !== 2
      });
    });
  }
  return objects;
}

function createColumnPairObjects(piece) {
  const objects = [];
  const columnXs = [-9.2, 9.2];
  const slotOffsets = [
    { x: -0.27, z: -0.27 },
    { x: 0.27, z: -0.27 },
    { x: -0.27, z: 0.27 },
    { x: 0.27, z: 0.27 }
  ];
  columnXs.forEach((columnX, columnIndex) => {
    for (let cluster = 0; cluster < piece.render_facts.estimated_clusters_per_column; cluster += 1) {
      const y = 0.55 + cluster * 0.5;
      slotOffsets.forEach((offset, slot) => {
        const colorName = (cluster + slot + columnIndex) % 2 === 0 ? piece.selected_color_names[0] : piece.selected_color_names[1];
        addBalloon(objects, {
          id: `${piece.id}_${columnIndex}_c${cluster}_b${slot}`,
          pieceId: piece.id,
          colorName,
          x: piece.placement.x_ft + columnX + offset.x,
          y,
          z: piece.placement.y_ft + offset.z,
          radius: BALLOON.radius_11_in_ft,
          squash: { x: 1, y: 0.95, z: 0.9 },
          knot: slot > 0
        });
      });
    }
  });
  return objects;
}

function createGarlandObjects(piece) {
  const objects = [];
  const sizeTokens = [
    ...Array.from({ length: piece.render_facts.size_mix.hero_24 }, () => ({ label: "hero_24", radius: 1 })),
    ...Array.from({ length: piece.render_facts.size_mix.accent_16 }, () => ({ label: "accent_16", radius: 0.6667 })),
    ...Array.from({ length: piece.render_facts.size_mix.filler_5 }, () => ({ label: "filler_5", radius: 0.2083 })),
    ...Array.from({ length: piece.render_facts.size_mix.body_11 }, () => ({ label: "body_11", radius: BALLOON.radius_11_in_ft }))
  ];
  const ordered = interleaveGarlandSizes(sizeTokens);
  ordered.forEach((size, index) => {
    const t = index / (ordered.length - 1);
    const x = piece.placement.x_ft - piece.render_facts.length_ft / 2 + t * piece.render_facts.length_ft;
    const wave = Math.sin(t * Math.PI * 2.7);
    const mass = Math.cos(t * Math.PI * 5.2);
    const colorName = piece.selected_color_names[index % piece.selected_color_names.length];
    addBalloon(objects, {
      id: `${piece.id}_${size.label}_${index}`,
      pieceId: piece.id,
      colorName,
      x,
      y: 7.25 + wave * 0.38 + (size.label === "hero_24" ? 0.18 : 0),
      z: piece.placement.y_ft + mass * 0.36,
      radius: size.radius,
      squash: { x: 1.05, y: 0.92, z: 0.9 },
      knot: size.label !== "filler_5" && index % 3 !== 0
    });
  });
  return objects;
}

function createBackdropWallObjects(piece) {
  const objects = [];
  const xStart = -piece.render_facts.width_ft / 2 + 0.5;
  const yStart = 0.7;
  const slotOffsets = [
    { x: -0.18, y: -0.18 },
    { x: 0.18, y: -0.18 },
    { x: -0.18, y: 0.18 },
    { x: 0.18, y: 0.18 }
  ];
  for (let row = 0; row < piece.render_facts.cells_high; row += 1) {
    for (let column = 0; column < piece.render_facts.cells_wide; column += 1) {
      slotOffsets.forEach((offset, slot) => {
        const colorName = piece.selected_color_names[(row + column + slot) % piece.selected_color_names.length];
        addBalloon(objects, {
          id: `${piece.id}_r${row}_c${column}_b${slot}`,
          pieceId: piece.id,
          colorName,
          x: piece.placement.x_ft + xStart + column + offset.x,
          y: yStart + row * 0.84 + offset.y,
          z: piece.placement.y_ft,
          radius: 0.38,
          squash: { x: 1.04, y: 0.96, z: 0.78 },
          knot: false
        });
      });
    }
  }
  return objects;
}

function addBalloon(objects, config) {
  objects.push({
    id: config.id,
    pieceId: config.pieceId,
    type: "balloon",
    color: COLOR_HEX[config.colorName],
    position: { x: config.x, y: config.y, z: config.z },
    scale: {
      x: config.radius * 2 * config.squash.x,
      y: config.radius * 2 * config.squash.y,
      z: config.radius * 2 * config.squash.z
    }
  });
  if (config.knot) {
    objects.push({
      id: `${config.id}_knot`,
      pieceId: config.pieceId,
      type: "knot",
      color: shadeColor(COLOR_HEX[config.colorName], -18),
      position: { x: config.x + 0.05, y: config.y - config.radius * 0.68, z: config.z - 0.04 },
      scale: { x: config.radius * 0.28, y: config.radius * 0.38, z: config.radius * 0.24 }
    });
  }
}

function interleaveGarlandSizes(tokens) {
  const groups = {
    hero_24: tokens.filter((token) => token.label === "hero_24"),
    accent_16: tokens.filter((token) => token.label === "accent_16"),
    filler_5: tokens.filter((token) => token.label === "filler_5"),
    body_11: tokens.filter((token) => token.label === "body_11")
  };
  const ordered = [];
  for (let index = 0; index < tokens.length; index += 1) {
    if (index % 32 === 0 && groups.hero_24.length) {
      ordered.push(groups.hero_24.pop());
    } else if (index % 10 === 0 && groups.accent_16.length) {
      ordered.push(groups.accent_16.pop());
    } else if (index % 5 === 0 && groups.filler_5.length) {
      ordered.push(groups.filler_5.pop());
    } else if (groups.body_11.length) {
      ordered.push(groups.body_11.pop());
    } else if (groups.filler_5.length) {
      ordered.push(groups.filler_5.pop());
    } else if (groups.accent_16.length) {
      ordered.push(groups.accent_16.pop());
    } else {
      ordered.push(groups.hero_24.pop());
    }
  }
  return ordered;
}

function shadeColor(hex, amount) {
  const value = Number.parseInt(hex.slice(1), 16);
  const r = clamp((value >> 16) + amount, 0, 255);
  const g = clamp(((value >> 8) & 0xff) + amount, 0, 255);
  const b = clamp((value & 0xff) + amount, 0, 255);
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

export function round(value, places) {
  const factor = 10 ** places;
  return Math.round(value * factor) / factor;
}

export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}
