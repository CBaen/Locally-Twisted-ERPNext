import "./event-playground-styles.css";
import * as pc from "playcanvas";
import { CameraControls } from "playcanvas/scripts/esm/camera-controls.mjs";
import {
  createEventPlaygroundState,
  createEventPlaygroundPayload,
  addPiece,
  addProp,
  selectItem,
  getSelectedItem,
  moveSelectedItem,
  rotateSelectedPiece,
  setSelectedPieceColors,
  setSelectedPiecePattern,
  setSelectedPieceMaterial,
  setSelectedItemSize,
  setLevel,
  turnStage,
  duplicateSelectedPiece,
  deleteSelectedPiece,
  acceptSuggestion,
  ignoreSuggestion,
  getColorHex
} from "./event-playground-state.js";

const COLORS = {
  ink: "#0a0a0b",
  navy: "#0e2240",
  slate: "#2f3a4a",
  brass: "#b89a5b",
  berry: "#b31b34",
  wood: "#6f5439",
  gym: "#d9c7b3",
  patio: "#b7a58d",
  grass: "#8fa77f",
  paper: "#faf7f2",
  line: "#8b7d6b",
  glass: "#86a1ac"
};

const state = createEventPlaygroundState();
const shell = document.querySelector("[data-event-playground-ready]");
const canvas = document.getElementById("event-playground-canvas");
const levelSelect = document.querySelector('[data-control="level"]');
const materialSelect = document.querySelector('[data-control="material"]');
const selectedLabel = document.querySelector('[data-status="selected"]');
const pieceCount = document.querySelector('[data-status="piece-count"]');
const stageStatus = document.querySelector('[data-status="stage-turn"]');
const apiStatus = document.querySelector('[data-status="api"]');
const contactForm = document.querySelector("[data-contact-form]");
const LOCAL_DRAFT_KEY = "lt_event_playground_draft_v1";
const HANDOFF_ORIGIN = new URLSearchParams(window.location.search).get("handoff_origin") || "";

const app = new pc.Application(canvas, {
  graphicsDeviceOptions: {
    alpha: false,
    antialias: true,
    preserveDrawingBuffer: true
  }
});
app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);
window.addEventListener("resize", () => app.resizeCanvas());
app.start();
app.scene.ambientLight = new pc.Color(0.52, 0.53, 0.49);

const materialCache = new Map();
const meshToItem = new Map();
const entityByItem = new Map();
let selectedTool = "view";
let drag = null;

const stageRoot = new pc.Entity("event-playground-stage-root");
const stageGeometryRoot = new pc.Entity("stage-geometry-root");
const itemRoot = new pc.Entity("placed-item-root");
const marker = createSelectionMarker();
stageRoot.addChild(stageGeometryRoot);
stageRoot.addChild(itemRoot);
stageRoot.addChild(marker);
app.root.addChild(stageRoot);

const camera = createCamera();
createLights();
buildControls();
syncScene();
syncUi();
shell.dataset.eventPlaygroundReady = "true";

function buildControls() {
  state.levels.forEach((level) => {
    const option = document.createElement("option");
    option.value = level.id;
    option.textContent = level.label;
    levelSelect.appendChild(option);
  });
  levelSelect.value = state.level_id;
  levelSelect.addEventListener("change", () => {
    setLevel(state, levelSelect.value);
    syncScene();
    syncUi();
  });

  state.palette.materials.forEach((material) => {
    const option = document.createElement("option");
    option.value = material.id;
    option.textContent = material.label;
    materialSelect.appendChild(option);
  });
  materialSelect.addEventListener("change", () => {
    setSelectedPieceMaterial(state, materialSelect.value);
    syncScene();
    syncUi();
  });

  renderPalette("[data-palette='pieces']", state.palette.pieces, (id) => addPiece(state, id));
  renderPalette("[data-palette='props']", state.palette.props, (id) => addProp(state, id));
  renderColorControls();
  renderPatternControls();
  renderSuggestionControls();

  document.querySelectorAll("[data-tool]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedTool = button.dataset.tool;
      canvas.dataset.tool = selectedTool;
      syncUi();
    });
  });

  document.querySelectorAll("[data-size]").forEach((button) => {
    button.addEventListener("click", () => {
      setSelectedItemSize(state, button.dataset.size);
      syncScene();
      syncUi();
    });
  });

  document.querySelector('[data-action="rotate-left"]').addEventListener("click", () => {
    rotateSelectedPiece(state, -15);
    syncScene();
    syncUi();
  });
  document.querySelector('[data-action="rotate-right"]').addEventListener("click", () => {
    rotateSelectedPiece(state, 15);
    syncScene();
    syncUi();
  });
  document.querySelector('[data-action="duplicate"]').addEventListener("click", () => {
    duplicateSelectedPiece(state);
    syncScene();
    syncUi();
  });
  document.querySelector('[data-action="delete"]').addEventListener("click", () => {
    deleteSelectedPiece(state);
    syncScene();
    syncUi();
  });
  document.querySelector('[data-action="save-draft"]').addEventListener("click", () => saveDesign("draft"));
  document.querySelector('[data-action="submit-inquiry"]').addEventListener("click", () => saveDesign("inquiry"));
}

function renderPalette(selector, definitions, action) {
  const root = document.querySelector(selector);
  definitions.forEach((definition) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = definition.label;
    button.addEventListener("click", () => {
      action(definition.id);
      syncScene();
      syncUi();
    });
    root.appendChild(button);
  });
}

function renderColorControls() {
  const root = document.querySelector('[data-control="colors"]');
  state.palette.colors.forEach((color) => {
    const button = document.createElement("button");
    button.type = "button";
    button.title = color.name;
    button.dataset.color = color.name;
    button.style.background = color.hex;
    button.setAttribute("aria-label", color.name);
    button.addEventListener("click", () => {
      setSelectedPieceColors(state, [color.name]);
      syncScene();
      syncUi();
    });
    root.appendChild(button);
  });
}

function renderPatternControls() {
  const root = document.querySelector('[data-control="patterns"]');
  state.palette.patterns.forEach((pattern) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = pattern.label;
    button.dataset.pattern = pattern.id;
    button.addEventListener("click", () => {
      setSelectedPiecePattern(state, pattern.id);
      syncScene();
      syncUi();
    });
    root.appendChild(button);
  });
}

function renderSuggestionControls() {
  const root = document.querySelector('[data-control="suggestions"]');
  state.suggestions.forEach((suggestion) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = suggestion.label;
    button.dataset.suggestion = suggestion.id;
    button.addEventListener("click", () => {
      if (state.accepted_suggestions.includes(suggestion.id)) {
        ignoreSuggestion(state, suggestion.id);
      } else {
        acceptSuggestion(state, suggestion.id);
      }
      syncUi();
    });
    root.appendChild(button);
  });
}

function syncUi() {
  const selected = getSelectedItem(state);
  selectedLabel.textContent = selected?.label || "None";
  pieceCount.textContent = String(state.placedItems.length);
  stageStatus.textContent = `${Math.round(state.view.stage_rotation_deg)} deg`;
  levelSelect.value = state.level_id;
  materialSelect.value = selected?.material || "standard_latex";

  document.querySelectorAll("[data-tool]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.tool === selectedTool));
  });
  document.querySelectorAll("[data-pattern]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.pattern === selected?.pattern);
  });
  document.querySelectorAll("[data-size]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.size === selected?.size);
  });
  document.querySelectorAll("[data-color]").forEach((button) => {
    button.classList.toggle("is-active", !!selected?.selected_colors?.includes(button.dataset.color));
  });
  document.querySelectorAll("[data-suggestion]").forEach((button) => {
    button.classList.toggle("is-active", state.accepted_suggestions.includes(button.dataset.suggestion));
  });
}

function syncScene() {
  meshToItem.clear();
  entityByItem.clear();
  clearChildren(stageGeometryRoot);
  clearChildren(itemRoot);

  const level = state.levels.find((candidate) => candidate.id === state.level_id) || state.levels[0];
  buildLevel(level);

  for (const item of state.placedItems) {
    const root = new pc.Entity(item.id);
    root.setLocalPosition(item.placement.x_ft, 0, item.placement.z_ft);
    root.setLocalEulerAngles(0, item.placement.rotation_deg, 0);
    root.setLocalScale(item.scale, item.scale, item.scale);
    itemRoot.addChild(root);
    entityByItem.set(item.id, root);
    if (item.kind === "balloon_piece") buildBalloonPiece(item, root);
    if (item.kind === "prop") buildProp(item, root);
    collectMeshes(root, item.id);
  }

  stageRoot.setLocalEulerAngles(0, state.view.stage_rotation_deg, 0);
  updateSelectionMarker();
}

function buildLevel(level) {
  const width = level.dimensions_ft.width;
  const depth = level.dimensions_ft.depth;
  const floorColor = {
    gym_floor: COLORS.gym,
    polished_lobby: "#dfe3e4",
    patio: COLORS.patio,
    neutral_room: "#d7d2c7",
    showroom: "#e9edf0"
  }[level.surface] || COLORS.gym;

  stageGeometryRoot.addChild(box("venue-floor", [0, -0.12, 0], [width, 0.22, depth], floorColor));
  stageGeometryRoot.addChild(box("back-line", [0, 2.6, depth / 2 + 0.04], [width, 5.2, 0.08], "#c9d0cc"));
  stageGeometryRoot.addChild(box("front-edge", [0, 0.04, -depth / 2 - 0.07], [width, 0.18, 0.14], COLORS.navy));

  for (let x = -Math.floor(width / 2); x <= width / 2; x += 2) {
    stageGeometryRoot.addChild(box(`grid-x-${x}`, [x, 0.015, 0], [0.018, 0.02, depth], COLORS.line));
  }
  for (let z = -Math.floor(depth / 2); z <= depth / 2; z += 2) {
    stageGeometryRoot.addChild(box(`grid-z-${z}`, [0, 0.02, z], [width, 0.02, 0.018], COLORS.line));
  }

  if (level.id === "school_gym") {
    stageGeometryRoot.addChild(box("gym-key", [0, 0.03, -3.7], [7, 0.03, 0.08], COLORS.berry));
    stageGeometryRoot.addChild(box("bleachers", [-width / 2 + 1.2, 1.0, 1.2], [0.7, 2.0, 8], COLORS.slate));
  }
  if (level.id === "corporate_lobby") {
    stageGeometryRoot.addChild(box("glass-wall", [0, 3.1, depth / 2 + 0.12], [width - 2, 5.8, 0.08], COLORS.glass));
  }
  if (level.id === "backyard_patio") {
    stageGeometryRoot.addChild(box("grass-band", [0, -0.08, depth / 2 - 1.1], [width, 0.1, 2.2], COLORS.grass));
  }
  if (level.id === "community_room") {
    stageGeometryRoot.addChild(box("notice-board", [-width / 2 + 1.0, 2.8, depth / 2 + 0.16], [1.4, 2.4, 0.12], COLORS.brass));
  }
  if (level.id === "car_dealership_lite") {
    const car = new pc.Entity("showroom-car");
    stageGeometryRoot.addChild(car);
    car.setLocalPosition(-6.8, 0, 1.4);
    buildDisplayCar(car, COLORS.slate);
  }
}

function buildBalloonPiece(item, root) {
  if (item.product_family === "classic_arch") buildClassicArch(item, root);
  if (item.product_family === "classic_column_pair") buildColumnPair(item, root);
  if (item.product_family === "balloon_wall_photo_moment") buildBalloonWall(item, root);
  if (item.product_family === "table_centerpiece") buildCenterpiece(item, root);
  if (item.product_family === "welcome_sign_cluster") buildWelcomeSign(item, root);
}

function buildClassicArch(item, root) {
  const colors = colorsForItem(item);
  for (let i = 0; i < 24; i += 1) {
    const t = i / 23;
    const angle = Math.PI - Math.PI * t;
    const cluster = quadCluster(`arch-${item.id}-${i}`, colors, i % 2 ? 42 : 0);
    cluster.setLocalPosition(Math.cos(angle) * 6.6, 0.9 + Math.sin(angle) * 6.4, 0);
    cluster.setLocalEulerAngles(0, 0, (t - 0.5) * -42);
    root.addChild(cluster);
  }
}

function buildColumnPair(item, root) {
  const colors = colorsForItem(item);
  [-7.4, 7.4].forEach((x, side) => {
    for (let i = 0; i < 8; i += 1) {
      const cluster = quadCluster(`columns-${item.id}-${side}-${i}`, colors, i % 2 ? 42 : 0);
      cluster.setLocalPosition(x, 0.7 + i * 0.72, 0);
      root.addChild(cluster);
    }
  });
}

function buildBalloonWall(item, root) {
  const colors = colorsForItem(item);
  for (let row = 0; row < 7; row += 1) {
    for (let col = 0; col < 8; col += 1) {
      const color = colors[(row + col) % colors.length];
      const balloon = balloonEntity(`wall-${item.id}-${row}-${col}`, color);
      balloon.setLocalPosition((col - 3.5) * 0.9, 0.8 + row * 0.78, 0);
      root.addChild(balloon);
    }
  }
  root.addChild(box(`wall-frame-${item.id}`, [0, 3.4, 0.1], [7.8, 6.9, 0.08], COLORS.navy));
}

function buildCenterpiece(item, root) {
  const colors = colorsForItem(item);
  root.addChild(box(`centerpiece-stand-${item.id}`, [0, 1.25, 0], [0.12, 2.4, 0.12], COLORS.brass));
  const top = quadCluster(`centerpiece-${item.id}`, colors, 0);
  top.setLocalPosition(0, 2.8, 0);
  root.addChild(top);
}

function buildWelcomeSign(item, root) {
  const colors = colorsForItem(item);
  root.addChild(box(`sign-board-${item.id}`, [0, 2.4, 0.04], [2.3, 3.2, 0.12], COLORS.paper));
  root.addChild(box(`sign-stand-${item.id}`, [0, 1.0, 0.18], [0.16, 2.0, 0.16], COLORS.brass));
  [-1.35, 1.35].forEach((x, side) => {
    const cluster = quadCluster(`sign-cluster-${item.id}-${side}`, colors, side ? 45 : 0);
    cluster.setLocalPosition(x, 3.35, 0);
    root.addChild(cluster);
  });
}

function buildProp(item, root) {
  const color = getColorHex(item.selected_colors[0]);
  if (item.product_family === "linen_table") {
    root.addChild(box(`table-top-${item.id}`, [0, 1.35, 0], [5.5, 0.25, 2.5], color));
    root.addChild(box(`table-base-${item.id}`, [0, 0.65, 0], [5.2, 1.2, 2.25], "#ded5c6"));
  } else if (item.product_family === "chair") {
    root.addChild(box(`chair-seat-${item.id}`, [0, 0.55, 0], [1.4, 0.22, 1.3], color));
    root.addChild(box(`chair-back-${item.id}`, [0, 1.45, 0.56], [1.4, 1.6, 0.16], color));
  } else if (item.product_family === "sign_easel") {
    root.addChild(box(`easel-board-${item.id}`, [0, 2.2, 0], [1.9, 2.6, 0.1], COLORS.paper));
    root.addChild(box(`easel-left-${item.id}`, [-0.8, 1.5, 0.1], [0.1, 3.0, 0.1], color));
    root.addChild(box(`easel-right-${item.id}`, [0.8, 1.5, 0.1], [0.1, 3.0, 0.1], color));
  } else if (item.product_family === "scale_person") {
    root.addChild(sphere(`person-head-${item.id}`, [0, 5.15, 0], [0.55, 0.55, 0.55], color));
    root.addChild(box(`person-body-${item.id}`, [0, 2.55, 0], [0.8, 4.1, 0.45], color));
  } else if (item.product_family === "display_car") {
    buildDisplayCar(root, color);
  }
}

function buildDisplayCar(root, color) {
  root.addChild(box("car-body", [0, 0.7, 0], [6.8, 1.1, 3.2], color));
  root.addChild(box("car-cabin", [-0.4, 1.45, 0], [2.6, 1.0, 2.3], "#a9bac2"));
  [-2.2, 2.2].forEach((x) => {
    [-1.45, 1.45].forEach((z) => {
      root.addChild(sphere(`car-wheel-${x}-${z}`, [x, 0.35, z], [0.72, 0.72, 0.32], COLORS.ink));
    });
  });
}

function quadCluster(name, colors, phaseDeg) {
  const root = new pc.Entity(name);
  const phase = phaseDeg * Math.PI / 180;
  [0, Math.PI / 2, Math.PI, Math.PI * 1.5].forEach((angle, index) => {
    const x = Math.cos(angle + phase) * 0.31;
    const y = Math.sin(angle + phase) * 0.31;
    const balloon = balloonEntity(`${name}-balloon-${index}`, colors[index % colors.length]);
    balloon.setLocalPosition(x, y, index % 2 ? 0.08 : -0.08);
    root.addChild(balloon);
  });
  return root;
}

function balloonEntity(name, color) {
  const root = new pc.Entity(name);
  root.addChild(sphere(`${name}-body`, [0, 0, 0], [0.82, 0.9, 0.82], color, true));
  root.addChild(sphere(`${name}-neck`, [0, -0.48, 0], [0.16, 0.23, 0.16], color, true));
  root.addChild(sphere(`${name}-knot`, [0, -0.62, 0], [0.17, 0.09, 0.17], color, true));
  return root;
}

function colorsForItem(item) {
  const names = item.selected_colors?.length ? item.selected_colors : ["Pearl White"];
  if (item.pattern === "solid") return [getColorHex(names[0])];
  if (item.pattern === "color_blocks" && names.length === 1) return [getColorHex(names[0]), "#f8f1e6"];
  return names.map(getColorHex);
}

function updateSelectionMarker() {
  const selected = getSelectedItem(state);
  const entity = selected ? entityByItem.get(selected.id) : null;
  marker.enabled = !!entity;
  if (!entity) return;
  const pos = entity.getLocalPosition();
  marker.setLocalPosition(pos.x, 0.06, pos.z);
  marker.setLocalEulerAngles(0, selected.placement.rotation_deg, 0);
  const size = selected.kind === "prop" ? 2.4 : Math.max(3.2, selected.dimensions_ft.width * selected.scale);
  marker.setLocalScale(size, 1, selected.kind === "prop" ? 2.4 : 2.8);
}

async function pickItem(x, y) {
  const picker = new pc.Picker(app, Math.max(1, canvas.clientWidth / 2), Math.max(1, canvas.clientHeight / 2));
  const worldLayer = app.scene.layers.getLayerByName("World");
  if (!worldLayer) return null;
  picker.prepare(camera.camera, app.scene, [worldLayer]);
  const hits = await picker.getSelectionAsync(x / 2, y / 2, 1, 1);
  const hit = hits.find((mesh) => meshToItem.has(mesh));
  return hit ? meshToItem.get(hit) : null;
}

canvas.addEventListener("pointerdown", async (event) => {
  const itemId = await pickItem(event.offsetX, event.offsetY);
  if (itemId) {
    selectItem(state, itemId);
    syncUi();
    syncScene();
  }
  if (selectedTool === "view") return;
  event.preventDefault();
  canvas.setPointerCapture(event.pointerId);
  drag = { id: event.pointerId, x: event.offsetX, y: event.offsetY };
});

canvas.addEventListener("pointermove", (event) => {
  if (!drag || drag.id !== event.pointerId) return;
  event.preventDefault();
  const dx = event.offsetX - drag.x;
  const dy = event.offsetY - drag.y;
  drag.x = event.offsetX;
  drag.y = event.offsetY;
  if (selectedTool === "stage") {
    turnStage(state, dx * 0.32);
  } else if (selectedTool === "rotate") {
    rotateSelectedPiece(state, dx * 0.5);
  } else if (selectedTool === "move") {
    moveSelectedByScreenDelta(dx, dy);
  }
  syncScene();
  syncUi();
});

canvas.addEventListener("pointerup", (event) => {
  if (drag?.id === event.pointerId) {
    drag = null;
    canvas.releasePointerCapture(event.pointerId);
  }
});

function moveSelectedByScreenDelta(dx, dy) {
  const right = camera.right.clone();
  const forward = camera.forward.clone();
  forward.y = 0;
  if (forward.length() < 0.001) forward.set(0, 0, -1);
  forward.normalize();
  const delta = right.mulScalar(dx * 0.025).add(forward.mulScalar(-dy * 0.025));
  moveSelectedItem(state, delta.x, delta.z);
}

async function saveDesign(mode) {
  const contact = Object.fromEntries(new FormData(contactForm).entries());
  const screenshot = screenshotDataUrl();
  const payload = createEventPlaygroundPayload(state, {
    screenshotReference: screenshot,
    contact,
    handoffState: mode === "inquiry" ? "inquiry_submitted" : "draft"
  });

  if (mode === "draft") {
    try {
      window.localStorage.setItem(LOCAL_DRAFT_KEY, JSON.stringify({
        source: "event-playground",
        saved_at: new Date().toISOString(),
        payload
      }));
      apiStatus.textContent = "Draft saved locally in this browser preview.";
      apiStatus.className = "epg-note epg-status-ok";
    } catch (error) {
      apiStatus.textContent = "This browser blocked local draft storage.";
      apiStatus.className = "epg-note epg-status-error";
    }
    return;
  }

  const handoff = {
    source: "event-playground",
    customer: {
      name: contact.customer_name || "",
      email: contact.email || "",
      phone: contact.phone || ""
    },
    summary: summarizeHandoff(payload),
    payload
  };

  try {
    const targetOrigin = HANDOFF_ORIGIN || "*";
    window.parent.postMessage({
      type: "LT_EVENT_PLAYGROUND_CONTACT_HANDOFF",
      payload: handoff
    }, targetOrigin);
    apiStatus.textContent = "Opening the quote form with this design summary.";
    apiStatus.className = "epg-note epg-status-ok";
  } catch (error) {
    apiStatus.textContent = "Could not hand this design to the quote form from this preview.";
    apiStatus.className = "epg-note epg-status-error";
  }
}

function summarizeHandoff(payload) {
  const pieces = payload.placed_balloon_pieces || [];
  const props = payload.placed_props || [];
  const colorGroups = payload.selected_colors_materials_patterns || [];
  const colors = unique(colorGroups.flatMap((entry) => entry.colors || []));
  const accepted = payload.upsell_suggestions?.accepted || [];
  return {
    venue: payload.preset?.label || payload.level_id || "",
    pieces: pieces.map((piece) => piece.label).filter(Boolean),
    props: props.map((prop) => prop.label).filter(Boolean),
    colors,
    suggestions: accepted,
    note: payload.customer_note || ""
  };
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function screenshotDataUrl() {
  try {
    return canvas.toDataURL("image/png");
  } catch (_) {
    return "";
  }
}

function createCamera() {
  const entity = new pc.Entity("camera");
  entity.addComponent("camera", {
    clearColor: new pc.Color(0.72, 0.76, 0.73),
    fov: 45
  });
  entity.setPosition(11, 7, -14);
  entity.lookAt(0, 2.2, 0);
  app.root.addChild(entity);
  entity.addComponent("script");
  const controls = entity.script.create(CameraControls);
  controls.focusPoint = new pc.Vec3(0, 2, 0);
  controls.pitchRange = new pc.Vec2(-72, -14);
  controls.zoomRange = new pc.Vec2(6, 24);
  controls.rotateDamping = 0.88;
  controls.moveDamping = 0.88;
  controls.zoomDamping = 0.88;
  return entity;
}

function createLights() {
  const key = new pc.Entity("key-light");
  key.addComponent("light", { type: "directional", color: new pc.Color(1, 0.92, 0.76), intensity: 2.0 });
  key.setEulerAngles(45, 38, 0);
  app.root.addChild(key);
  const fill = new pc.Entity("fill-light");
  fill.addComponent("light", { type: "directional", color: new pc.Color(0.68, 0.78, 0.9), intensity: 0.72 });
  fill.setEulerAngles(20, -138, 0);
  app.root.addChild(fill);
}

function createSelectionMarker() {
  const root = new pc.Entity("selection-marker");
  root.enabled = false;
  root.addChild(box("select-front", [0, 0, -0.5], [1, 0.04, 0.08], COLORS.brass));
  root.addChild(box("select-back", [0, 0, 0.5], [1, 0.04, 0.08], COLORS.brass));
  root.addChild(box("select-left", [-0.5, 0, 0], [0.08, 0.04, 1], COLORS.brass));
  root.addChild(box("select-right", [0.5, 0, 0], [0.08, 0.04, 1], COLORS.brass));
  return root;
}

function sphere(name, position, scale, color, balloon = false) {
  const entity = new pc.Entity(name);
  entity.setLocalPosition(position[0], position[1], position[2]);
  entity.setLocalScale(scale[0], scale[1], scale[2]);
  entity.addComponent("render", { type: "sphere", material: material(color, balloon) });
  return entity;
}

function box(name, position, scale, color) {
  const entity = new pc.Entity(name);
  entity.setLocalPosition(position[0], position[1], position[2]);
  entity.setLocalScale(scale[0], scale[1], scale[2]);
  entity.addComponent("render", { type: "box", material: material(color, false) });
  return entity;
}

function material(hex, balloon) {
  hex = hex || "#f8f1e6";
  const key = `${hex}:${balloon}`;
  if (materialCache.has(key)) return materialCache.get(key);
  const mat = new pc.StandardMaterial();
  const color = toColor(hex);
  mat.diffuse.copy(color);
  mat.emissive = new pc.Color(color.r * 0.018, color.g * 0.018, color.b * 0.018);
  mat.specular = balloon ? new pc.Color(0.75, 0.69, 0.56) : new pc.Color(0.16, 0.15, 0.14);
  mat.shininess = balloon ? 64 : 18;
  mat.update();
  materialCache.set(key, mat);
  return mat;
}

function collectMeshes(entity, itemId) {
  entity.findComponents("render").forEach((render) => {
    render.meshInstances.forEach((mesh) => meshToItem.set(mesh, itemId));
  });
}

function clearChildren(entity) {
  [...entity.children].forEach((child) => child.destroy());
}

function toColor(hex) {
  const value = Number.parseInt(hex.slice(1), 16);
  return new pc.Color(((value >> 16) & 0xff) / 255, ((value >> 8) & 0xff) / 255, (value & 0xff) / 255);
}

window.eventPlayground = {
  getState: () => state,
  getPayload: () => createEventPlaygroundPayload(state, {
    screenshotReference: null,
    contact: Object.fromEntries(new FormData(contactForm).entries())
  })
};
