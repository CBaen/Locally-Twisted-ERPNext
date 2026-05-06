import "./classic-v2-styles.css";
import * as pc from "playcanvas";
import { CameraControls } from "playcanvas/scripts/esm/camera-controls.mjs";

const STAGE_WIDTH_FT = 24;
const STAGE_DEPTH_FT = 12;
const BALLOON_DIAMETER_FT = 10 / 12;
const BALLOON_CONTACT_DISTANCE_FT = BALLOON_DIAMETER_FT * 0.92;

const COLORS = {
  berry: "#b7354a",
  white: "#fff4e5",
  gold: "#d2a642",
  slate: "#33433f",
  charcoal: "#171b1d",
  wood: "#6f5439",
  line: "#8b7d6b",
  brass: "#b7934d"
};

const shell = document.querySelector("[data-builder-ready]");
const canvas = document.getElementById("application-canvas");
const modeButtons = [...document.querySelectorAll("[data-mode]")];
const selectedEl = document.querySelector('[data-status="selected"]');
const modeEl = document.querySelector('[data-status="mode"]');
const countEl = document.querySelector('[data-status="count"]');
const stageEl = document.querySelector('[data-status="stage"]');

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
app.scene.ambientLight = new pc.Color(0.46, 0.47, 0.44);

const materialCache = new Map();
const pieces = new Map();
const meshToPiece = new Map();
let sequence = 1;
let selectedId = null;
let mode = "view";
let stageYawDeg = 0;
let drag = null;

const stageRoot = new pc.Entity("stage-root");
const decorRoot = new pc.Entity("decor-root");
const marker = createSelectionMarker();
stageRoot.addChild(decorRoot);
stageRoot.addChild(marker);
app.root.addChild(stageRoot);

const camera = createCamera();
createLights();
buildStage(stageRoot);

const picker = new pc.Picker(app, 1, 1);
const worldLayer = app.scene.layers.getLayerByName("World");

function state() {
  return {
    mode,
    selectedLabel: selectedId ? pieces.get(selectedId)?.label || "Selected" : "None",
    pieceCount: pieces.size,
    stageYawDeg: Math.round(stageYawDeg)
  };
}

function notify() {
  const current = state();
  selectedEl.textContent = current.selectedLabel;
  modeEl.textContent = titleCase(current.mode);
  countEl.textContent = String(current.pieceCount);
  stageEl.textContent = `${current.stageYawDeg} deg`;
  modeButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.mode === current.mode));
  });
}

function selectPiece(id) {
  selectedId = id;
  const piece = selectedId ? pieces.get(selectedId) : null;
  marker.enabled = !!piece;
  if (piece) {
    marker.setLocalPosition(piece.root.getLocalPosition());
    marker.setLocalEulerAngles(0, piece.yawDeg, 0);
    marker.setLocalScale(piece.kind === "classic_arch" ? 1.28 : 0.72, 1, piece.kind === "classic_arch" ? 0.62 : 0.86);
  }
  notify();
}

function registerPiece(piece) {
  pieces.set(piece.id, piece);
  piece.meshes.forEach((mesh) => meshToPiece.set(mesh, piece.id));
  selectPiece(piece.id);
}

function addPiece(kind, source) {
  const id = `${kind}_${sequence++}`;
  const root = new pc.Entity(id);
  const piece = {
    id,
    kind,
    root,
    yawDeg: source?.yawDeg ?? 0,
    label: kind === "classic_arch" ? "Classic Arch" : "Column Pair",
    meshes: new Set()
  };

  if (kind === "classic_arch") {
    buildClassicArch(piece);
    root.setLocalPosition(source ? source.root.getLocalPosition().clone().add(new pc.Vec3(1.2, 0, -0.6)) : new pc.Vec3(0, 0, 1.2));
  } else {
    buildColumnPair(piece);
    root.setLocalPosition(source ? source.root.getLocalPosition().clone().add(new pc.Vec3(1.2, 0, 0.6)) : new pc.Vec3(0, 0, 0.8));
  }

  root.setLocalEulerAngles(0, piece.yawDeg, 0);
  decorRoot.addChild(root);
  registerPiece(piece);
}

async function pickPiece(x, y) {
  if (!camera.camera || !worldLayer) {
    return null;
  }
  const scale = 0.5;
  picker.resize(canvas.clientWidth * scale, canvas.clientHeight * scale);
  picker.prepare(camera.camera, app.scene, [worldLayer]);
  const hits = await picker.getSelectionAsync(x * scale, y * scale, 1, 1);
  const mesh = hits.find((hit) => meshToPiece.has(hit));
  return mesh ? meshToPiece.get(mesh) || null : null;
}

function moveSelected(dx, dy) {
  if (!selectedId) {
    return;
  }
  const piece = pieces.get(selectedId);
  if (!piece) {
    return;
  }
  const right = camera.right.clone();
  const forward = camera.forward.clone();
  forward.y = 0;
  if (forward.length() < 0.0001) {
    forward.set(0, 0, -1);
  }
  forward.normalize();
  const delta = right.mulScalar(dx * 0.023).add(forward.mulScalar(-dy * 0.023));
  delta.y = 0;
  const next = piece.root.getLocalPosition().clone().add(delta);
  next.x = clamp(next.x, -STAGE_WIDTH_FT / 2 + 1, STAGE_WIDTH_FT / 2 - 1);
  next.z = clamp(next.z, -STAGE_DEPTH_FT / 2 + 0.7, STAGE_DEPTH_FT / 2 - 0.7);
  piece.root.setLocalPosition(next);
  selectPiece(piece.id);
}

function spinSelected(dx) {
  if (!selectedId) {
    return;
  }
  const piece = pieces.get(selectedId);
  if (!piece) {
    return;
  }
  piece.yawDeg = normalizeDeg(piece.yawDeg + dx * 0.45);
  piece.root.setLocalEulerAngles(0, piece.yawDeg, 0);
  selectPiece(piece.id);
}

function spinStage(dx) {
  stageYawDeg = normalizeDeg(stageYawDeg + dx * 0.32);
  stageRoot.setLocalEulerAngles(0, stageYawDeg, 0);
  notify();
}

canvas.addEventListener("pointerdown", async (event) => {
  const pieceId = await pickPiece(event.offsetX, event.offsetY);
  if (pieceId) {
    selectPiece(pieceId);
  }
  if (mode === "view") {
    return;
  }
  event.preventDefault();
  canvas.setPointerCapture(event.pointerId);
  drag = { pointerId: event.pointerId, x: event.offsetX, y: event.offsetY };
});

canvas.addEventListener("pointermove", (event) => {
  if (!drag || drag.pointerId !== event.pointerId) {
    return;
  }
  event.preventDefault();
  const dx = event.offsetX - drag.x;
  const dy = event.offsetY - drag.y;
  drag.x = event.offsetX;
  drag.y = event.offsetY;
  if (mode === "stage") {
    spinStage(dx);
  } else if (mode === "move") {
    moveSelected(dx, dy);
  } else if (mode === "spin") {
    spinSelected(dx);
  }
});

canvas.addEventListener("pointerup", (event) => {
  if (drag?.pointerId === event.pointerId) {
    drag = null;
    canvas.releasePointerCapture(event.pointerId);
  }
});

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    mode = button.dataset.mode;
    canvas.dataset.mode = mode;
    notify();
  });
});

document.querySelector('[data-action="add-arch"]').addEventListener("click", () => addPiece("classic_arch"));
document.querySelector('[data-action="add-columns"]').addEventListener("click", () => addPiece("classic_columns"));
document.querySelector('[data-action="duplicate"]').addEventListener("click", () => {
  const piece = selectedId ? pieces.get(selectedId) : null;
  if (piece) {
    addPiece(piece.kind, piece);
  }
});
document.querySelector('[data-action="delete"]').addEventListener("click", () => {
  if (!selectedId || pieces.size <= 1) {
    return;
  }
  const piece = pieces.get(selectedId);
  piece.meshes.forEach((mesh) => meshToPiece.delete(mesh));
  piece.root.destroy();
  pieces.delete(selectedId);
  selectPiece(pieces.keys().next().value || null);
});
document.querySelector('[data-action="reset-view"]').addEventListener("click", () => {
  camera.setPosition(9, 5.4, -12);
  camera.lookAt(0, 2, 0);
});

addPiece("classic_arch");
addPiece("classic_columns");
selectPiece("classic_arch_1");
mode = "view";
canvas.dataset.mode = mode;
notify();

window.balloonBuilderV2 = {
  getState: state
};
shell.dataset.builderReady = "true";

function createCamera() {
  const entity = new pc.Entity("camera");
  entity.addComponent("camera", {
    clearColor: new pc.Color(0.77, 0.79, 0.77),
    fov: 45
  });
  entity.setPosition(9, 5.4, -12);
  entity.lookAt(0, 2, 0);
  app.root.addChild(entity);
  entity.addComponent("script");
  const controls = entity.script.create(CameraControls);
  controls.focusPoint = new pc.Vec3(0, 2, 0);
  controls.pitchRange = new pc.Vec2(-72, -12);
  controls.zoomRange = new pc.Vec2(5, 20);
  controls.rotateDamping = 0.9;
  controls.moveDamping = 0.9;
  controls.zoomDamping = 0.9;
  return entity;
}

function createLights() {
  const key = new pc.Entity("key-light");
  key.addComponent("light", { type: "directional", color: new pc.Color(1, 0.92, 0.76), intensity: 2.1 });
  key.setEulerAngles(48, 38, 0);
  app.root.addChild(key);
  const fill = new pc.Entity("fill-light");
  fill.addComponent("light", { type: "directional", color: new pc.Color(0.66, 0.76, 0.86), intensity: 0.72 });
  fill.setEulerAngles(20, -132, 0);
  app.root.addChild(fill);
}

function buildStage(root) {
  root.addChild(box("stage-deck", [0, -0.12, 0], [STAGE_WIDTH_FT, 0.24, STAGE_DEPTH_FT], COLORS.wood));
  root.addChild(box("front-lip", [0, 0.12, -STAGE_DEPTH_FT / 2 - 0.12], [STAGE_WIDTH_FT, 0.34, 0.22], COLORS.charcoal));
  root.addChild(box("back-truss", [0, 5.95, STAGE_DEPTH_FT / 2 + 0.05], [STAGE_WIDTH_FT, 0.22, 0.18], COLORS.slate));
  root.addChild(box("back-left-upright", [-STAGE_WIDTH_FT / 2 + 0.14, 3.0, STAGE_DEPTH_FT / 2 + 0.05], [0.22, 5.9, 0.18], COLORS.slate));
  root.addChild(box("back-right-upright", [STAGE_WIDTH_FT / 2 - 0.14, 3.0, STAGE_DEPTH_FT / 2 + 0.05], [0.22, 5.9, 0.18], COLORS.slate));
  for (let x = -12; x <= 12; x += 2) {
    root.addChild(box(`grid-x-${x}`, [x, 0.015, 0], [0.018, 0.018, STAGE_DEPTH_FT], COLORS.line));
  }
  for (let z = -6; z <= 6; z += 2) {
    root.addChild(box(`grid-z-${z}`, [0, 0.02, z], [STAGE_WIDTH_FT, 0.018, 0.018], COLORS.line));
  }
}

function buildClassicArch(piece) {
  const colors = [COLORS.berry, COLORS.white, COLORS.gold, COLORS.white];
  for (let i = 0; i < 24; i += 1) {
    const t = i / 23;
    const angle = Math.PI - Math.PI * t;
    const cluster = quadCluster(`arch-${piece.id}-${i}`, colors, i % 2 ? 45 : 0);
    cluster.setLocalPosition(Math.cos(angle) * 6.7, 0.8 + Math.sin(angle) * 6.6, -1.2);
    cluster.setLocalEulerAngles(0, 0, (t - 0.5) * -42);
    piece.root.addChild(cluster);
    collectMeshes(cluster, piece.meshes);
  }
}

function buildColumnPair(piece) {
  const colors = [COLORS.gold, COLORS.white, COLORS.berry, COLORS.white];
  [-7.7, 7.7].forEach((x, side) => {
    for (let i = 0; i < 8; i += 1) {
      const cluster = quadCluster(`column-${piece.id}-${side}-${i}`, colors, i % 2 ? 45 : 0);
      cluster.setLocalPosition(x, 0.68 + i * 0.68, 0.6);
      piece.root.addChild(cluster);
      collectMeshes(cluster, piece.meshes);
    }
  });
}

function quadCluster(name, colors, phaseDeg) {
  const root = new pc.Entity(name);
  const phase = (phaseDeg * Math.PI) / 180;
  const points = [0, Math.PI / 2, Math.PI, Math.PI * 1.5].map((angle) => ({
    x: Math.cos(angle + phase) * BALLOON_DIAMETER_FT * 0.32,
    y: Math.sin(angle + phase) * BALLOON_DIAMETER_FT * 0.32,
    z: 0
  }));
  resolvePacking(points, BALLOON_CONTACT_DISTANCE_FT, 8).forEach((point, index) => {
    const balloon = balloonEntity(`${name}-balloon-${index}`, colors[index % colors.length]);
    balloon.setLocalPosition(point.x, point.y, point.z);
    root.addChild(balloon);
  });
  return root;
}

function resolvePacking(points, minDistance, iterations) {
  const result = points.map((point) => ({ ...point }));
  for (let pass = 0; pass < iterations; pass += 1) {
    for (let i = 0; i < result.length; i += 1) {
      for (let j = i + 1; j < result.length; j += 1) {
        const a = result[i];
        const b = result[j];
        let dx = b.x - a.x;
        let dy = b.y - a.y;
        let dz = b.z - a.z;
        let distance = Math.hypot(dx, dy, dz);
        if (distance < 0.0001) {
          dx = 1;
          distance = 1;
        }
        if (distance >= minDistance) {
          continue;
        }
        const push = (minDistance - distance) * 0.5;
        const nx = dx / distance;
        const ny = dy / distance;
        const nz = dz / distance;
        a.x -= nx * push;
        a.y -= ny * push;
        a.z -= nz * push;
        b.x += nx * push;
        b.y += ny * push;
        b.z += nz * push;
      }
    }
  }
  return result;
}

function balloonEntity(name, color) {
  const root = new pc.Entity(name);
  root.addChild(sphere(`${name}-body`, [0, 0, 0], [BALLOON_DIAMETER_FT * 0.98, BALLOON_DIAMETER_FT * 1.06, BALLOON_DIAMETER_FT * 0.98], color));
  root.addChild(sphere(`${name}-neck`, [0, -BALLOON_DIAMETER_FT * 0.54, 0], [BALLOON_DIAMETER_FT * 0.16, BALLOON_DIAMETER_FT * 0.23, BALLOON_DIAMETER_FT * 0.16], color));
  root.addChild(sphere(`${name}-knot`, [0, -BALLOON_DIAMETER_FT * 0.68, 0], [BALLOON_DIAMETER_FT * 0.18, BALLOON_DIAMETER_FT * 0.1, BALLOON_DIAMETER_FT * 0.18], color));
  return root;
}

function createSelectionMarker() {
  const root = new pc.Entity("selection-marker");
  root.enabled = false;
  root.addChild(box("select-front", [0, 0.055, -5.2], [11.5, 0.04, 0.08], COLORS.brass));
  root.addChild(box("select-back", [0, 0.055, 5.2], [11.5, 0.04, 0.08], COLORS.brass));
  root.addChild(box("select-left", [-5.75, 0.055, 0], [0.08, 0.04, 10.4], COLORS.brass));
  root.addChild(box("select-right", [5.75, 0.055, 0], [0.08, 0.04, 10.4], COLORS.brass));
  return root;
}

function sphere(name, position, scale, color) {
  const entity = new pc.Entity(name);
  entity.setLocalPosition(position[0], position[1], position[2]);
  entity.setLocalScale(scale[0], scale[1], scale[2]);
  entity.addComponent("render", { type: "sphere", material: material(color, true) });
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
  const key = `${hex}:${balloon}`;
  if (materialCache.has(key)) {
    return materialCache.get(key);
  }
  const mat = new pc.StandardMaterial();
  const color = toColor(hex);
  mat.diffuse.copy(color);
  mat.emissive = new pc.Color(color.r * 0.025, color.g * 0.025, color.b * 0.025);
  mat.specular = balloon ? new pc.Color(0.78, 0.7, 0.56) : new pc.Color(0.18, 0.17, 0.15);
  mat.shininess = balloon ? 68 : 18;
  mat.update();
  materialCache.set(key, mat);
  return mat;
}

function collectMeshes(entity, target) {
  entity.findComponents("render").forEach((render) => {
    render.meshInstances.forEach((mesh) => target.add(mesh));
  });
}

function toColor(hex) {
  const value = Number.parseInt(hex.slice(1), 16);
  return new pc.Color(((value >> 16) & 0xff) / 255, ((value >> 8) & 0xff) / 255, (value & 0xff) / 255);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function normalizeDeg(value) {
  return ((value % 360) + 360) % 360;
}

function titleCase(value) {
  return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
}
