import {
  CLASSIC_SCENE_VERSION,
  CLASSIC_STAGE,
  clone,
  clamp,
  colorHexFor,
  createClassicArch,
  createClassicColumnPair,
  round
} from "./classic-construction.js";

export const CLASSIC_CAMERA = Object.freeze({
  mode: "fixed_isometric",
  orientation: "audience_side",
  position: { x: 16.5, y: 15.2, z: -16.5 },
  target: { x: 0, y: 3.5, z: 0 }
});

const PLACEMENT_LIMITS = Object.freeze({
  min_x: -11.5,
  max_x: 11.5,
  min_y: -5.5,
  max_y: 5.5
});

export function createClassicSceneState() {
  return {
    scene_version: CLASSIC_SCENE_VERSION,
    venue: CLASSIC_STAGE.venue,
    engine: "playcanvas",
    camera: CLASSIC_CAMERA.mode,
    stage: clone(CLASSIC_STAGE),
    grid: {
      tile_size_ft: CLASSIC_STAGE.tile_size_ft,
      visible: true
    },
    view: {
      stage_rotation_deg: 0,
      pan_x_ft: 0,
      pan_y_ft: 0
    },
    selected_piece_id: "arch_1",
    pieces: [
      createClassicArch({ id: "arch_1" }),
      createClassicColumnPair({ id: "column_pair_1" })
    ]
  };
}

export function selectPiece(state, pieceId) {
  if (state.pieces.some((piece) => piece.id === pieceId)) {
    state.selected_piece_id = pieceId;
  }
  return getSelectedPiece(state);
}

export function getSelectedPiece(state) {
  return state.pieces.find((piece) => piece.id === state.selected_piece_id) ?? state.pieces[0] ?? null;
}

export function movePiece(state, pieceId, { deltaXFt, deltaYFt }) {
  const piece = findPiece(state, pieceId);
  if (!piece) {
    return null;
  }
  piece.placement.x_ft = round(clamp(piece.placement.x_ft + deltaXFt, PLACEMENT_LIMITS.min_x, PLACEMENT_LIMITS.max_x), 2);
  piece.placement.y_ft = round(clamp(piece.placement.y_ft + deltaYFt, PLACEMENT_LIMITS.min_y, PLACEMENT_LIMITS.max_y), 2);
  return piece;
}

export function setPiecePlacement(state, pieceId, placement) {
  const piece = findPiece(state, pieceId);
  if (!piece) {
    return null;
  }
  piece.placement.x_ft = round(clamp(placement.x_ft, PLACEMENT_LIMITS.min_x, PLACEMENT_LIMITS.max_x), 2);
  piece.placement.y_ft = round(clamp(placement.y_ft, PLACEMENT_LIMITS.min_y, PLACEMENT_LIMITS.max_y), 2);
  return piece;
}

export function setPieceRotation(state, pieceId, rotationDeg) {
  const piece = findPiece(state, pieceId);
  if (!piece) {
    return null;
  }
  piece.placement.rotation_deg = normalizeRotation(rotationDeg);
  return piece;
}

export function setStageRotation(state, rotationDeg) {
  state.view.stage_rotation_deg = normalizeRotation(rotationDeg);
  return state.view.stage_rotation_deg;
}

export function turnStageByScreenDelta(state, deltaX) {
  return setStageRotation(state, state.view.stage_rotation_deg + deltaX * 0.5);
}

export function panStageByScreenDelta(state, deltaX, deltaY, rect) {
  const scale = Math.min(rect.width / 30, rect.height / 20);
  const isoX = deltaX / (scale * 0.86);
  const isoY = deltaY / (scale * 0.34);
  const deltaViewX = (isoX - isoY) / 2;
  const deltaViewY = (isoX + isoY) / 2;
  state.view.pan_x_ft = round(clamp(state.view.pan_x_ft + deltaViewX, -18, 18), 2);
  state.view.pan_y_ft = round(clamp(state.view.pan_y_ft + deltaViewY, -12, 12), 2);
  return state.view;
}

export function spinPieceByScreenDelta(state, pieceId, deltaX) {
  const piece = findPiece(state, pieceId);
  if (!piece) {
    return null;
  }
  return setPieceRotation(state, pieceId, piece.placement.rotation_deg + deltaX * 0.5);
}

export function duplicatePiece(state, pieceId) {
  const source = findPiece(state, pieceId);
  if (!source) {
    return null;
  }
  const duplicate = clone(source);
  duplicate.id = nextDuplicateId(state, source.product_family);
  duplicate.duplicated_from_id = source.id;
  duplicate.placement.x_ft = round(clamp(source.placement.x_ft + 1, PLACEMENT_LIMITS.min_x, PLACEMENT_LIMITS.max_x), 2);
  duplicate.placement.y_ft = round(clamp(source.placement.y_ft + 1, PLACEMENT_LIMITS.min_y, PLACEMENT_LIMITS.max_y), 2);
  state.pieces.push(duplicate);
  state.selected_piece_id = duplicate.id;
  return duplicate;
}

export function deletePiece(state, pieceId) {
  const index = state.pieces.findIndex((piece) => piece.id === pieceId);
  if (index === -1 || state.pieces.length <= 1) {
    return false;
  }
  const [removed] = state.pieces.splice(index, 1);
  if (state.selected_piece_id === removed.id) {
    const source = removed.duplicated_from_id ? findPiece(state, removed.duplicated_from_id) : null;
    state.selected_piece_id = source?.id ?? state.pieces[Math.max(0, index - 1)]?.id ?? state.pieces[0]?.id ?? null;
  }
  return true;
}

export function updatePiecePattern(state, pieceId, pattern) {
  const piece = findPiece(state, pieceId);
  if (!piece) {
    return null;
  }
  piece.pattern = pattern;
  piece.design_id = `${piece.product_family}_${pattern}`;
  piece.render_facts.pattern = pattern;
  return piece;
}

export function updatePieceColors(state, pieceId, selectedColorNames) {
  const piece = findPiece(state, pieceId);
  if (!piece) {
    return null;
  }
  piece.selected_color_names = selectedColorNames;
  return piece;
}

export function createClassicPayload(state) {
  const sceneWarnings = createSceneWarnings(state);
  return {
    scene_version: CLASSIC_SCENE_VERSION,
    venue: CLASSIC_STAGE.venue,
    engine: "playcanvas",
    camera: CLASSIC_CAMERA.mode,
    camera_orientation: CLASSIC_CAMERA.orientation,
    view: {
      stage_rotation_deg: state.view.stage_rotation_deg,
      pan_x_ft: round(state.view.pan_x_ft),
      pan_y_ft: round(state.view.pan_y_ft)
    },
    stage: {
      width_ft: CLASSIC_STAGE.width_ft,
      depth_ft: CLASSIC_STAGE.depth_ft,
      grid_size_ft: CLASSIC_STAGE.tile_size_ft
    },
    selected_piece_id: state.selected_piece_id,
    pieces: state.pieces.map((piece) => {
      const warnings = createPieceWarnings(piece, state);
      return {
        id: piece.id,
        product_family: piece.product_family,
        construction_engine: piece.construction_engine,
        design_id: piece.design_id,
        requested_dimensions: clone(piece.requested_dimensions),
        render_dimensions: clone(piece.render_dimensions),
        balloon_size_preset: piece.balloon_size_preset,
        pattern: piece.pattern,
        selected_color_names: [...piece.selected_color_names],
        display_colors: piece.selected_color_names.map((name) => ({ name, hex: colorHexFor(name) })),
        placement: {
          x_ft: round(piece.placement.x_ft),
          y_ft: round(piece.placement.y_ft),
          rotation_deg: round(piece.placement.rotation_deg, 1)
        },
        render_facts: clone(piece.render_facts),
        warnings
      };
    }),
    warnings: sceneWarnings,
    sales_summary: createSalesSummary(state, sceneWarnings)
  };
}

export function createClassicRenderObjects(state) {
  const objects = [...createStageObjects(state)];
  for (const piece of state.pieces) {
    if (piece.product_family === "classic_arch") {
      objects.push(...createArchObjects(piece, state.selected_piece_id === piece.id));
    }
    if (piece.product_family === "classic_column_pair") {
      objects.push(...createColumnPairObjects(piece, state.selected_piece_id === piece.id));
    }
  }
  return objects.map((object) => applyViewTransform(object, state.view)).sort((a, b) => {
    const az = a.position?.z ?? 0;
    const bz = b.position?.z ?? 0;
    const ay = a.position?.y ?? 0;
    const by = b.position?.y ?? 0;
    return bz - az || ay - by;
  });
}

export function getPieceAnchor(piece) {
  if (piece.product_family === "classic_arch") {
    return rotatePoint({ x: 0, y: 4.9, z: 0 }, piece.placement);
  }
  if (piece.product_family === "classic_column_pair") {
    return rotatePoint({ x: 0, y: 4.3, z: 0 }, piece.placement);
  }
  return { x: piece.placement.x_ft, y: 1, z: piece.placement.y_ft };
}

export function projectWorldToScreen(worldPoint, rect) {
  return projectViewPointToScreen(worldPoint, rect);
}

export function projectStagePointToScreen(worldPoint, rect, viewOrRotation) {
  const view = typeof viewOrRotation === "number" ? { stage_rotation_deg: viewOrRotation, pan_x_ft: 0, pan_y_ft: 0 } : viewOrRotation;
  const viewPoint = rotateStagePoint(worldPoint, view.stage_rotation_deg);
  viewPoint.x += view.pan_x_ft ?? 0;
  viewPoint.z += view.pan_y_ft ?? 0;
  return projectViewPointToScreen(viewPoint, rect);
}

export function movePieceByScreenDelta(state, pieceId, deltaX, deltaY, rect) {
  const scale = Math.min(rect.width / 30, rect.height / 20);
  const isoX = deltaX / (scale * 0.86);
  const isoY = deltaY / (scale * 0.34);
  const deltaViewX = (isoX - isoY) / 2;
  const deltaViewY = (isoX + isoY) / 2;
  const deltaStage = rotateStagePoint({ x: deltaViewX, y: 0, z: deltaViewY }, -state.view.stage_rotation_deg);
  const deltaStageX = deltaStage.x;
  const deltaStageY = deltaStage.z;
  return movePiece(state, pieceId, { deltaXFt: deltaStageX, deltaYFt: deltaStageY });
}

function createStageObjects() {
  const objects = [
    {
      id: "stage_floor",
      type: "box",
      color: "#d8caba",
      position: { x: 0, y: -0.07, z: 0 },
      scale: { x: CLASSIC_STAGE.width_ft, y: 0.12, z: CLASSIC_STAGE.depth_ft }
    },
    {
      id: "back_scrim",
      type: "box",
      color: "#becac4",
      position: { x: 0, y: 4.2, z: CLASSIC_STAGE.depth_ft / 2 + 0.08 },
      scale: { x: CLASSIC_STAGE.width_ft, y: 8.4, z: 0.14 }
    },
    {
      id: "front_lip",
      type: "box",
      color: "#8e7058",
      position: { x: 0, y: 0.15, z: -CLASSIC_STAGE.depth_ft / 2 - 0.12 },
      scale: { x: CLASSIC_STAGE.width_ft, y: 0.3, z: 0.24 }
    }
  ];

  for (let x = -CLASSIC_STAGE.width_ft / 2; x <= CLASSIC_STAGE.width_ft / 2; x += CLASSIC_STAGE.tile_size_ft) {
    objects.push({
      id: `grid_x_${x}`,
      type: "box",
      color: x % 5 === 0 ? "#9aa9a5" : "#c4d0cc",
      position: { x, y: 0.015, z: 0 },
      scale: { x: x % 5 === 0 ? 0.045 : 0.025, y: 0.035, z: CLASSIC_STAGE.depth_ft }
    });
  }

  for (let z = -CLASSIC_STAGE.depth_ft / 2; z <= CLASSIC_STAGE.depth_ft / 2; z += CLASSIC_STAGE.tile_size_ft) {
    objects.push({
      id: `grid_z_${z}`,
      type: "box",
      color: z % 5 === 0 ? "#9aa9a5" : "#c4d0cc",
      position: { x: 0, y: 0.02, z },
      scale: { x: CLASSIC_STAGE.width_ft, y: 0.035, z: z % 5 === 0 ? 0.045 : 0.025 }
    });
  }

  return objects;
}

function createArchObjects(piece, selected) {
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
      x: Math.cos(theta) * radius,
      y: 0.72 + Math.sin(theta) * radius,
      z: 0
    };
    clusterOffsets.forEach((offset, slot) => {
      const colorName = colorForSlot(piece, cluster, slot);
      const position = rotatePoint(
        {
          x: base.x + offset.x,
          y: base.y + offset.y,
          z: base.z + offset.z
        },
        piece.placement
      );
      addBalloon(objects, {
        id: `${piece.id}_c${cluster}_b${slot}`,
        pieceId: piece.id,
        colorName,
        position,
        radius: 0.9167 / 2,
        squash: { x: 1.02, y: 0.94, z: 0.88 },
        knot: slot !== 2
      });
    });
  }
  if (selected) {
    objects.push(createSelectionMarker(piece, radius * 2, 0.2));
  }
  return objects;
}

function createColumnPairObjects(piece, selected) {
  const objects = [];
  const columnXs = [-4.6, 4.6];
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
        const colorName = colorForSlot(piece, cluster + columnIndex, slot);
        const position = rotatePoint(
          {
            x: columnX + offset.x,
            y,
            z: offset.z
          },
          piece.placement
        );
        addBalloon(objects, {
          id: `${piece.id}_${columnIndex}_c${cluster}_b${slot}`,
          pieceId: piece.id,
          colorName,
          position,
          radius: 0.9167 / 2,
          squash: { x: 1, y: 0.95, z: 0.9 },
          knot: slot > 0
        });
      });
    }
  });
  if (selected) {
    objects.push(createSelectionMarker(piece, 10.2, 0.16));
  }
  return objects;
}

function addBalloon(objects, config) {
  objects.push({
    id: config.id,
    pieceId: config.pieceId,
    type: "balloon",
    color: colorHexFor(config.colorName),
    position: config.position,
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
      color: shadeColor(colorHexFor(config.colorName), -18),
      position: {
        x: config.position.x + 0.05,
        y: config.position.y - config.radius * 0.68,
        z: config.position.z - 0.04
      },
      scale: { x: config.radius * 0.28, y: config.radius * 0.38, z: config.radius * 0.24 }
    });
  }
}

function createSelectionMarker(piece, width, depth) {
  return {
    id: `${piece.id}_selection_marker`,
    pieceId: piece.id,
    type: "box",
    color: "#18323a",
    position: { x: piece.placement.x_ft, y: 0.08, z: piece.placement.y_ft },
    scale: { x: width, y: 0.08, z: depth },
    rotation_y_deg: piece.placement.rotation_deg
  };
}

function createPieceWarnings(piece, state) {
  const warnings = [];
  if (Math.abs(piece.placement.x_ft) > 9.5 || Math.abs(piece.placement.y_ft) > 4.4) {
    warnings.push({
      code: "near_stage_edge",
      message: "Piece is close to the usable stage edge; Jeff should confirm real placement."
    });
  }
  if (piece.product_family === "classic_arch" && piece.placement.rotation_deg % 180 !== 0) {
    warnings.push({
      code: "arch_sideways",
      message: "Arch is rotated sideways; it may not read as an entrance or stage feature."
    });
  }
  for (const other of state.pieces) {
    if (other.id === piece.id) {
      continue;
    }
    const distance = Math.hypot(piece.placement.x_ft - other.placement.x_ft, piece.placement.y_ft - other.placement.y_ft);
    if (distance < 1.25) {
      warnings.push({
        code: "piece_overlap",
        message: "Piece overlaps another piece in the planning view."
      });
      break;
    }
  }
  return warnings;
}

function createSceneWarnings(state) {
  return state.pieces.flatMap((piece) => createPieceWarnings(piece, state).map((warning) => ({ piece_id: piece.id, ...warning })));
}

function createSalesSummary(state, warnings) {
  const archCount = state.pieces.filter((piece) => piece.product_family === "classic_arch").length;
  const columnPairCount = state.pieces.filter((piece) => piece.product_family === "classic_column_pair").length;
  const parts = [];
  if (archCount) {
    parts.push(`${archCount} classic arch${archCount === 1 ? "" : "es"}`);
  }
  if (columnPairCount) {
    parts.push(`${columnPairCount} classic column pair${columnPairCount === 1 ? "" : "s"}`);
  }
  const warningText = warnings.length ? ` ${warnings.length} layout warning${warnings.length === 1 ? "" : "s"} need review.` : "";
  return `Corporate stage concept with ${parts.join(" and ")}.${warningText}`;
}

function colorForSlot(piece, cluster, slot) {
  if (piece.pattern === "solid") {
    return piece.selected_color_names[0];
  }
  if (piece.pattern === "band") {
    const band = Math.floor(cluster / 4);
    return piece.selected_color_names[band % piece.selected_color_names.length];
  }
  return piece.selected_color_names[(cluster + slot) % piece.selected_color_names.length];
}

function rotatePoint(point, placement) {
  const radians = (placement.rotation_deg * Math.PI) / 180;
  const cos = Math.cos(radians);
  const sin = Math.sin(radians);
  return {
    x: round(placement.x_ft + point.x * cos - point.z * sin, 4),
    y: round(point.y, 4),
    z: round(placement.y_ft + point.x * sin + point.z * cos, 4)
  };
}

function applyViewTransform(object, view) {
  const position = rotateStagePoint(object.position, view.stage_rotation_deg);
  position.x += view.pan_x_ft ?? 0;
  position.z += view.pan_y_ft ?? 0;
  return {
    ...object,
    position,
    rotation_y_deg: normalizeRotation((object.rotation_y_deg ?? 0) + view.stage_rotation_deg)
  };
}

function projectViewPointToScreen(viewPoint, rect) {
  const scale = Math.min(rect.width / 30, rect.height / 20);
  return {
    x: rect.left + rect.width * 0.5 + (viewPoint.x + viewPoint.z) * scale * 0.86,
    y: rect.top + rect.height * 0.6 + (-viewPoint.x + viewPoint.z) * scale * 0.34 - viewPoint.y * scale * 0.92
  };
}

function rotateStagePoint(point, rotationDeg) {
  const radians = (rotationDeg * Math.PI) / 180;
  const cos = Math.cos(radians);
  const sin = Math.sin(radians);
  return {
    x: round(point.x * cos - point.z * sin, 4),
    y: round(point.y, 4),
    z: round(point.x * sin + point.z * cos, 4)
  };
}

function findPiece(state, pieceId) {
  return state.pieces.find((piece) => piece.id === pieceId) ?? null;
}

function nextDuplicateId(state, productFamily) {
  const stem = productFamily.replace(/^classic_/, "");
  let index = state.pieces.length + 1;
  let candidate = `${stem}_${index}`;
  while (state.pieces.some((piece) => piece.id === candidate)) {
    index += 1;
    candidate = `${stem}_${index}`;
  }
  return candidate;
}

function normalizeRotation(rotationDeg) {
  return ((Math.round(rotationDeg) % 360) + 360) % 360;
}

function shadeColor(hex, amount) {
  const value = Number.parseInt(hex.slice(1), 16);
  const r = clamp((value >> 16) + amount, 0, 255);
  const g = clamp(((value >> 8) & 0xff) + amount, 0, 255);
  const b = clamp((value & 0xff) + amount, 0, 255);
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}
