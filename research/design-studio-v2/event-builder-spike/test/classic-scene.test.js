import test from "node:test";
import assert from "node:assert/strict";

import {
  createClassicSceneState,
  CLASSIC_CAMERA,
  createClassicPayload,
  deletePiece,
  duplicatePiece,
  createClassicRenderObjects,
  movePiece,
  panStageByScreenDelta,
  setPieceRotation,
  setStageRotation,
  spinPieceByScreenDelta,
  turnStageByScreenDelta,
  selectPiece
} from "../src/classic-scene.js";

test("scene starts with a corporate stage, classic arch, and classic column pair", () => {
  const state = createClassicSceneState();

  assert.equal(state.scene_version, "playcanvas-classic-stage-builder-v1");
  assert.equal(state.venue, "corporate_stage");
  assert.equal(state.stage.width_ft, 24);
  assert.equal(state.stage.depth_ft, 12);
  assert.equal(state.grid.tile_size_ft, 1);
  assert.deepEqual(
    state.pieces.map((piece) => piece.product_family),
    ["classic_arch", "classic_column_pair"]
  );
  assert.equal(state.view.stage_rotation_deg, 0);
  assert.equal(state.view.pan_x_ft, 0);
  assert.equal(state.view.pan_y_ft, 0);
});

test("movePiece preserves free placement while clamping to recoverable stage bounds", () => {
  const state = createClassicSceneState();

  movePiece(state, "arch_1", { deltaXFt: 200, deltaYFt: -200 });
  const arch = state.pieces.find((piece) => piece.id === "arch_1");

  assert.equal(arch.placement.x_ft, 11.5);
  assert.equal(arch.placement.y_ft, -5.5);
});

test("setPieceRotation supports arbitrary customer spin degrees", () => {
  const state = createClassicSceneState();

  setPieceRotation(state, "arch_1", 37);
  const arch = state.pieces.find((piece) => piece.id === "arch_1");
  assert.equal(arch.placement.rotation_deg, 37);

  setPieceRotation(state, "arch_1", 725);
  assert.equal(arch.placement.rotation_deg, 5);
});

test("classic camera views the stage from the audience side", () => {
  assert.equal(CLASSIC_CAMERA.position.z < 0, true);
  assert.equal(CLASSIC_CAMERA.target.z > CLASSIC_CAMERA.position.z, true);
});

test("setStageRotation supports arbitrary customer view spin without changing placement", () => {
  const state = createClassicSceneState();
  const beforePlacement = { ...state.pieces.find((piece) => piece.id === "arch_1").placement };

  setStageRotation(state, 123);
  assert.equal(state.view.stage_rotation_deg, 123);

  setStageRotation(state, 740);
  assert.equal(state.view.stage_rotation_deg, 20);
  assert.deepEqual(state.pieces.find((piece) => piece.id === "arch_1").placement, beforePlacement);
});

test("turnStageByScreenDelta spins the stage view from a pointer drag", () => {
  const state = createClassicSceneState();

  turnStageByScreenDelta(state, 80);

  assert.equal(state.view.stage_rotation_deg, 40);
});

test("panStageByScreenDelta moves the stage view without moving pieces", () => {
  const state = createClassicSceneState();
  const beforePlacement = { ...state.pieces.find((piece) => piece.id === "arch_1").placement };

  panStageByScreenDelta(state, 90, -45, { width: 900, height: 600 });

  assert.notEqual(state.view.pan_x_ft, 0);
  assert.notEqual(state.view.pan_y_ft, 0);
  assert.deepEqual(state.pieces.find((piece) => piece.id === "arch_1").placement, beforePlacement);
});

test("spinPieceByScreenDelta spins the selected piece from a pointer drag", () => {
  const state = createClassicSceneState();

  spinPieceByScreenDelta(state, "arch_1", 74);

  const arch = state.pieces.find((piece) => piece.id === "arch_1");
  assert.equal(arch.placement.rotation_deg, 37);
});

test("stage view transform changes render positions while preserving payload placement", () => {
  const state = createClassicSceneState();
  const before = createClassicRenderObjects(state).find((object) => object.id === "arch_1_c0_b0");

  setStageRotation(state, 90);
  panStageByScreenDelta(state, 60, 30, { width: 900, height: 600 });
  const after = createClassicRenderObjects(state).find((object) => object.id === "arch_1_c0_b0");
  const payload = createClassicPayload(state);
  const arch = payload.pieces.find((piece) => piece.id === "arch_1");

  assert.notEqual(after.position.x, before.position.x);
  assert.notEqual(after.position.z, before.position.z);
  assert.equal(payload.view.stage_rotation_deg, 90);
  assert.notEqual(payload.view.pan_x_ft, 0);
  assert.notEqual(payload.view.pan_y_ft, 0);
  assert.deepEqual(arch.placement, { x_ft: 0, y_ft: -3.2, rotation_deg: 0 });
});

test("duplicatePiece preserves construction facts and creates a unique selected instance", () => {
  const state = createClassicSceneState();

  const duplicate = duplicatePiece(state, "column_pair_1");

  assert.equal(duplicate.product_family, "classic_column_pair");
  assert.notEqual(duplicate.id, "column_pair_1");
  assert.equal(duplicate.render_facts.estimated_balloons, 128);
  assert.equal(state.selected_piece_id, duplicate.id);
  assert.equal(state.pieces.length, 3);
});

test("deletePiece removes only the selected piece and keeps another piece selected", () => {
  const state = createClassicSceneState();
  const duplicate = duplicatePiece(state, "arch_1");

  deletePiece(state, duplicate.id);

  assert.equal(state.pieces.some((piece) => piece.id === duplicate.id), false);
  assert.equal(state.pieces.length, 2);
  assert.equal(state.selected_piece_id, "arch_1");
});

test("payload records placement, rotation, construction facts, and warnings", () => {
  const state = createClassicSceneState();
  selectPiece(state, "arch_1");
  setPieceRotation(state, "arch_1", 37);
  movePiece(state, "arch_1", { deltaXFt: 0, deltaYFt: -20 });

  const payload = createClassicPayload(state);
  const arch = payload.pieces.find((piece) => piece.id === "arch_1");

  assert.equal(payload.scene_version, "playcanvas-classic-stage-builder-v1");
  assert.equal(payload.engine, "playcanvas");
  assert.equal(payload.view.stage_rotation_deg, 0);
  assert.equal(payload.view.pan_x_ft, 0);
  assert.equal(payload.view.pan_y_ft, 0);
  assert.equal(arch.placement.rotation_deg, 37);
  assert.equal(arch.render_facts.estimated_clusters, 50);
  assert.equal(arch.render_facts.estimated_balloons, 200);
  assert.ok(arch.warnings.some((warning) => warning.code === "near_stage_edge"));
});
