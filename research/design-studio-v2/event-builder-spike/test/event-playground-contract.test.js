import test from "node:test";
import assert from "node:assert/strict";

import {
  EVENT_PLAYGROUND_SCHEMA_VERSION,
  createEventPlaygroundState,
  createEventPlaygroundPayload,
  setSelectedPieceColors,
  setLevel,
  addPiece,
  duplicateSelectedPiece,
  deleteSelectedPiece,
  setSelectedPieceRotation,
  acceptSuggestion,
  ignoreSuggestion
} from "../src/event-playground-state.js";

test("event playground starts with V1 venues, honest decor families, context props, and suggestions", () => {
  const state = createEventPlaygroundState();

  assert.equal(EVENT_PLAYGROUND_SCHEMA_VERSION, "event-playground-v1");
  assert.deepEqual(
    state.levels.map((level) => level.id),
    ["school_gym", "corporate_lobby", "backyard_patio", "community_room", "car_dealership_lite"]
  );
  assert.ok(state.palette.pieces.some((piece) => piece.id === "classic_arch"));
  assert.ok(state.palette.pieces.some((piece) => piece.id === "column_pair"));
  assert.ok(state.palette.pieces.some((piece) => piece.id === "balloon_wall"));
  assert.ok(state.palette.pieces.some((piece) => piece.id === "table_centerpiece"));
  assert.ok(state.palette.pieces.some((piece) => piece.id === "welcome_sign_cluster"));
  assert.equal(state.palette.pieces.some((piece) => piece.id.includes("organic")), false);
  assert.ok(state.palette.props.some((prop) => prop.id === "linen_table"));
  assert.ok(state.palette.props.some((prop) => prop.id === "display_car"));
  assert.ok(state.suggestions.some((suggestion) => suggestion.id === "complete_entrance"));
});

test("event playground payload keeps Frappe handoff schema stable", () => {
  const state = createEventPlaygroundState();

  setLevel(state, "community_room");
  addPiece(state, "welcome_sign_cluster");
  setSelectedPieceRotation(state, 37);
  setSelectedPieceColors(state, ["Berry", "Pearl White"]);
  acceptSuggestion(state, "add_matching_columns");
  ignoreSuggestion(state, "add_photo_moment");

  const payload = createEventPlaygroundPayload(state, {
    screenshotReference: "data:image/png;base64,preview",
    contact: {
      customer_name: "Avery Planner",
      email: "avery@example.com",
      phone: "801-555-0100"
    },
    handoffState: "draft"
  });

  assert.equal(payload.schema_version, "event-playground-v1");
  assert.equal(payload.level_id, "community_room");
  assert.equal(payload.screenshot_reference, "data:image/png;base64,preview");
  assert.equal(payload.customer_contact.customer_name, "Avery Planner");
  assert.equal(payload.customer_contact.email, "avery@example.com");
  assert.equal(payload.customer_contact_handoff_state, "draft");
  assert.ok(payload.placed_balloon_pieces.length >= 2);
  assert.ok(payload.placed_props.some((prop) => prop.product_family === "linen_table"));
  assert.equal(
    payload.placed_balloon_pieces.every((piece) => piece.physical_status === "production-plausible"),
    true
  );
  assert.deepEqual(payload.upsell_suggestions.accepted, ["add_matching_columns"]);
  assert.deepEqual(payload.upsell_suggestions.ignored, ["add_photo_moment"]);
});

test("duplicate and delete operate on the selected whole piece", () => {
  const state = createEventPlaygroundState();
  const startingCount = state.placedItems.length;

  const duplicate = duplicateSelectedPiece(state);
  assert.ok(duplicate.id !== "classic_arch_1");
  assert.equal(state.placedItems.length, startingCount + 1);
  assert.equal(state.selectedItemId, duplicate.id);

  deleteSelectedPiece(state);
  assert.equal(state.placedItems.length, startingCount);
  assert.equal(state.selectedItemId, "classic_arch_1");
});
