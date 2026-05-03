import {
  createPayload,
  createRuntimeState,
  createSceneState,
  getPieceAnchor,
  movePieceByScreenDelta,
  projectWorldToScreen
} from "./scene-spec.js";

export function createEventBuilderPage({ engine, engineLabel, createRenderer }) {
  const shell = document.querySelector(".builder-shell");
  const canvas = document.querySelector("[data-scene-canvas]");
  const payloadOutput = document.querySelector("[data-payload-output]");
  const engineName = document.querySelector("[data-engine-name]");
  const state = createSceneState();
  const renderer = createRenderer(canvas);
  let lastRenderMs = 0;
  let currentPayload = createPayload(state, engine);
  let dragging = null;

  engineName.textContent = engineLabel;

  function syncPayload() {
    currentPayload = createPayload(state, engine);
    payloadOutput.textContent = JSON.stringify(currentPayload, null, 2);
  }

  function draw() {
    const started = performance.now();
    renderer.render(state);
    lastRenderMs = performance.now() - started;
    syncPayload();
    requestAnimationFrame(() => {
      shell.dataset.renderReady = "true";
    });
  }

  function pieceAt(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    let nearest = null;
    for (const piece of state.pieces) {
      const point = projectWorldToScreen(getPieceAnchor(piece), rect);
      const distance = Math.hypot(clientX - point.x, clientY - point.y);
      if (distance < 90 && (!nearest || distance < nearest.distance)) {
        nearest = { piece, distance };
      }
    }
    return nearest?.piece ?? null;
  }

  canvas.addEventListener("pointerdown", (event) => {
    const piece = pieceAt(event.clientX, event.clientY);
    if (!piece) {
      return;
    }
    event.preventDefault();
    canvas.setPointerCapture(event.pointerId);
    dragging = {
      pointerId: event.pointerId,
      piece,
      lastX: event.clientX,
      lastY: event.clientY
    };
  });

  canvas.addEventListener("pointermove", (event) => {
    if (!dragging || dragging.pointerId !== event.pointerId) {
      return;
    }
    const rect = canvas.getBoundingClientRect();
    movePieceByScreenDelta(dragging.piece, event.clientX - dragging.lastX, event.clientY - dragging.lastY, rect);
    dragging.lastX = event.clientX;
    dragging.lastY = event.clientY;
    draw();
  });

  canvas.addEventListener("pointerup", (event) => {
    if (dragging?.pointerId === event.pointerId) {
      dragging = null;
    }
  });

  canvas.addEventListener("pointercancel", () => {
    dragging = null;
  });

  window.addEventListener("resize", () => {
    draw();
  });

  window.eventBuilderSpike = {
    getPayload: () => currentPayload,
    getRuntimeState: () => createRuntimeState(engine, lastRenderMs),
    getPieceScreenPosition: (pieceId) => {
      const piece = state.pieces.find((candidate) => candidate.id === pieceId);
      if (!piece) {
        return null;
      }
      return projectWorldToScreen(getPieceAnchor(piece), canvas.getBoundingClientRect());
    }
  };

  draw();
}
