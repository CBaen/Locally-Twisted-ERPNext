import { CLASSIC_COLOR_HEX } from "./classic-construction.js";
import {
  createClassicPayload,
  createClassicSceneState,
  deletePiece,
  duplicatePiece,
  getPieceAnchor,
  getSelectedPiece,
  movePieceByScreenDelta,
  panStageByScreenDelta,
  projectStagePointToScreen,
  setPieceRotation,
  setStageRotation,
  spinPieceByScreenDelta,
  selectPiece,
  turnStageByScreenDelta,
  updatePieceColors,
  updatePiecePattern
} from "./classic-scene.js";

export function createClassicBuilderPage({ createRenderer }) {
  const shell = document.querySelector(".classic-shell");
  const canvas = document.querySelector("[data-classic-canvas]");
  const payloadOutput = document.querySelector("[data-classic-payload]");
  const selectedName = document.querySelector("[data-selected-name]");
  const selectedSummary = document.querySelector("[data-selected-summary]");
  const selectedFacts = document.querySelector("[data-selected-facts]");
  const warningList = document.querySelector("[data-warning-list]");
  const sceneSummary = document.querySelector("[data-scene-summary]");
  const patternSelect = document.querySelector("[data-pattern-select]");
  const colorSelects = [...document.querySelectorAll("[data-color-slot]")];
  const rotationInputs = [...document.querySelectorAll("[data-rotation-input]")];
  const rotationOutput = document.querySelector("[data-rotation-output]");
  const stageRotationInputs = [...document.querySelectorAll("[data-stage-rotation-input]")];
  const stageRotationOutput = document.querySelector("[data-stage-rotation-output]");
  const stageDragModeButtons = [...document.querySelectorAll("[data-stage-drag-mode]")];
  const pieceDragModeButtons = [...document.querySelectorAll("[data-piece-drag-mode]")];

  const state = createClassicSceneState();
  const renderer = createRenderer(canvas);
  let currentPayload = createClassicPayload(state);
  let stageDragMode = "turn";
  let pieceDragMode = "move";
  let dragging = null;

  populateColorSelects(colorSelects);

  function syncPayload() {
    currentPayload = createClassicPayload(state);
    payloadOutput.textContent = JSON.stringify(currentPayload, null, 2);
  }

  function syncInspector() {
    const piece = getSelectedPiece(state);
    if (!piece) {
      return;
    }
    const payloadPiece = currentPayload.pieces.find((candidate) => candidate.id === piece.id);
    stageRotationInputs.forEach((input) => {
      input.value = String(state.view.stage_rotation_deg);
    });
    if (stageRotationOutput) {
      stageRotationOutput.textContent = `${state.view.stage_rotation_deg} deg`;
    }
    selectedName.textContent = labelForPiece(piece);
    selectedSummary.textContent = `${piece.requested_dimensions.length_ft ?? piece.requested_dimensions.height_ft} ft, ${piece.pattern.replaceAll("_", " ")}`;
    patternSelect.value = piece.pattern;
    rotationInputs.forEach((input) => {
      input.value = String(piece.placement.rotation_deg);
    });
    if (rotationOutput) {
      rotationOutput.textContent = `${piece.placement.rotation_deg} deg`;
    }
    colorSelects.forEach((select, index) => {
      select.value = piece.selected_color_names[index] ?? piece.selected_color_names[0];
    });
    selectedFacts.innerHTML = "";
    appendFact(selectedFacts, "Construction", "4-balloon quads");
    appendFact(selectedFacts, "Clusters", String(piece.render_facts.estimated_clusters));
    appendFact(selectedFacts, "Balloons", String(piece.render_facts.estimated_balloons));
    appendFact(selectedFacts, "Placement", `${piece.placement.x_ft} ft, ${piece.placement.y_ft} ft`);
    appendFact(selectedFacts, "Rotation", `${piece.placement.rotation_deg} deg`);
    warningList.innerHTML = "";
    const warnings = payloadPiece?.warnings ?? [];
    if (!warnings.length) {
      const item = document.createElement("li");
      item.textContent = "No layout warnings for the selected piece.";
      warningList.append(item);
    } else {
      for (const warning of warnings) {
        const item = document.createElement("li");
        item.textContent = warning.message;
        warningList.append(item);
      }
    }
    sceneSummary.textContent = currentPayload.sales_summary;
  }

  function draw() {
    renderer.render(state);
    syncPayload();
    syncInspector();
    requestAnimationFrame(() => {
      shell.dataset.classicRenderReady = "true";
    });
  }

  function pieceAt(clientX, clientY) {
      const rect = canvas.getBoundingClientRect();
      let nearest = null;
      for (const piece of state.pieces) {
      const point = projectStagePointToScreen(getPieceAnchor(piece), rect, state.view);
      const distance = Math.hypot(clientX - point.x, clientY - point.y);
      if (distance < 95 && (!nearest || distance < nearest.distance)) {
        nearest = { piece, distance };
      }
    }
    return nearest?.piece ?? null;
  }

  canvas.addEventListener("pointerdown", (event) => {
    const piece = pieceAt(event.clientX, event.clientY);
    event.preventDefault();
    canvas.setPointerCapture(event.pointerId);
    if (piece) {
      selectPiece(state, piece.id);
      dragging = {
        type: pieceDragMode === "spin" ? "piece_spin" : "piece_move",
        pointerId: event.pointerId,
        pieceId: piece.id,
        lastX: event.clientX,
        lastY: event.clientY
      };
    } else {
      dragging = {
        type: stageDragMode === "move" ? "stage_pan" : "stage_turn",
        pointerId: event.pointerId,
        lastX: event.clientX,
        lastY: event.clientY
      };
    }
    draw();
  });

  canvas.addEventListener("pointermove", (event) => {
    if (!dragging || dragging.pointerId !== event.pointerId) {
      return;
    }
    const rect = canvas.getBoundingClientRect();
    const deltaX = event.clientX - dragging.lastX;
    const deltaY = event.clientY - dragging.lastY;
    if (dragging.type === "piece_move") {
      movePieceByScreenDelta(state, dragging.pieceId, deltaX, deltaY, rect);
    }
    if (dragging.type === "piece_spin") {
      spinPieceByScreenDelta(state, dragging.pieceId, deltaX);
    }
    if (dragging.type === "stage_turn") {
      turnStageByScreenDelta(state, deltaX);
    }
    if (dragging.type === "stage_pan") {
      panStageByScreenDelta(state, deltaX, deltaY, rect);
    }
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

  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) {
      return;
    }
    const selected = getSelectedPiece(state);
    if (!selected) {
      return;
    }
    if (button.dataset.action === "duplicate") {
      duplicatePiece(state, selected.id);
    }
    if (button.dataset.action === "delete") {
      deletePiece(state, selected.id);
    }
    draw();
  });

  patternSelect.addEventListener("change", () => {
    const selected = getSelectedPiece(state);
    if (selected) {
      updatePiecePattern(state, selected.id, patternSelect.value);
      draw();
    }
  });

  for (const select of colorSelects) {
    select.addEventListener("change", () => {
      const selected = getSelectedPiece(state);
      if (!selected) {
        return;
      }
      updatePieceColors(
        state,
        selected.id,
        colorSelects.map((candidate) => candidate.value)
      );
      draw();
    });
  }

  for (const input of rotationInputs) {
    input.addEventListener("input", () => {
      const selected = getSelectedPiece(state);
      if (!selected) {
        return;
      }
      setPieceRotation(state, selected.id, Number(input.value));
      draw();
    });
  }

  for (const input of stageRotationInputs) {
    input.addEventListener("input", () => {
      setStageRotation(state, Number(input.value));
      draw();
    });
  }

  for (const button of stageDragModeButtons) {
    button.addEventListener("click", () => {
      stageDragMode = button.dataset.stageDragMode;
      syncModeButtons(stageDragModeButtons, "stageDragMode", stageDragMode);
    });
  }

  for (const button of pieceDragModeButtons) {
    button.addEventListener("click", () => {
      pieceDragMode = button.dataset.pieceDragMode;
      syncModeButtons(pieceDragModeButtons, "pieceDragMode", pieceDragMode);
    });
  }

  window.addEventListener("resize", () => {
    draw();
  });

  window.classicStageBuilder = {
    getPayload: () => currentPayload,
    getState: () => state,
    getPieceScreenPosition: (pieceId) => {
      const piece = state.pieces.find((candidate) => candidate.id === pieceId);
      if (!piece) {
        return null;
      }
      return projectStagePointToScreen(getPieceAnchor(piece), canvas.getBoundingClientRect(), state.view);
    }
  };

  draw();
}

function populateColorSelects(selects) {
  for (const select of selects) {
    select.innerHTML = "";
    for (const [name, hex] of Object.entries(CLASSIC_COLOR_HEX)) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      option.dataset.hex = hex;
      select.append(option);
    }
  }
}

function appendFact(list, label, value) {
  const wrapper = document.createElement("div");
  const term = document.createElement("dt");
  const detail = document.createElement("dd");
  term.textContent = label;
  detail.textContent = value;
  wrapper.append(term, detail);
  list.append(wrapper);
}

function labelForPiece(piece) {
  if (piece.product_family === "classic_arch") {
    return "Classic arch";
  }
  if (piece.product_family === "classic_column_pair") {
    return "Classic column pair";
  }
  return "Classic piece";
}

function syncModeButtons(buttons, datasetKey, activeValue) {
  for (const button of buttons) {
    button.setAttribute("aria-pressed", String(button.dataset[datasetKey] === activeValue));
  }
}
