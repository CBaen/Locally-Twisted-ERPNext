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
import {
  EVENT_PLAYGROUND_CONSTRUCTION_VERSION,
  createClassicQuadRenderSlots
} from "../src/event-playground-construction.js";

const dot = (a, b) => a.x * b.x + a.y * b.y + a.z * b.z;

const normalizedToward = (from, to = { x: 0, y: 0, z: 0 }) => {
  const vector = {
    x: to.x - from.x,
    y: to.y - from.y,
    z: to.z - from.z
  };
  const length = Math.hypot(vector.x, vector.y, vector.z);
  return {
    x: vector.x / length,
    y: vector.y / length,
    z: vector.z / length
  };
};

test("event playground starts with V2 venues, honest decor families, context props, and suggestions", () => {
  const state = createEventPlaygroundState();

  assert.equal(EVENT_PLAYGROUND_SCHEMA_VERSION, "event-playground-v2");
  assert.deepEqual(
    state.levels.map((level) => level.id),
    ["school_gym", "corporate_lobby", "backyard_patio", "community_room", "car_dealership_lite"]
  );
  assert.ok(state.palette.pieces.some((piece) => piece.id === "classic_arch"));
  assert.equal(
    state.palette.pieces.find((piece) => piece.id === "classic_arch").render_facts.orientation_basis,
    "neck_and_knot_point_to_shared_quad_tie_center"
  );
  assert.ok(state.palette.pieces.some((piece) => piece.id === "column_pair"));
  assert.ok(state.palette.pieces.some((piece) => piece.id === "balloon_wall"));
  assert.ok(state.palette.pieces.some((piece) => piece.id === "table_centerpiece"));
  assert.ok(state.palette.pieces.some((piece) => piece.id === "welcome_sign_cluster"));
  assert.equal(state.palette.pieces.some((piece) => piece.id.includes("organic")), false);
  assert.ok(state.palette.props.some((prop) => prop.id === "linen_table"));
  assert.ok(state.palette.props.some((prop) => prop.id === "display_car"));
  assert.ok(state.suggestions.some((suggestion) => suggestion.id === "complete_entrance"));
});

test("event playground classic quad render slots point knots to the tie center", () => {
  const slots = createClassicQuadRenderSlots({ phaseDeg: 42, radius: 0.31, zOffset: 0.08 });

  assert.equal(EVENT_PLAYGROUND_CONSTRUCTION_VERSION, "event-playground-construction-0.1.0");
  assert.equal(slots.length, 4);
  assert.equal(new Set(slots.map((slot) => slot.slot)).size, 4);
  assert.equal(
    slots.every((slot) => slot.orientation_basis === "neck_and_knot_point_to_shared_quad_tie_center"),
    true
  );
  assert.equal(slots.every((slot) => slot.neck_direction.y < 0), false);
  assert.ok(slots.some((slot) => slot.neck_direction.y > 0));
  assert.ok(slots.every((slot) => {
    const expectedDirection = normalizedToward(slot.local_position, slot.tie_center);
    return dot(slot.neck_direction, expectedDirection) > 0.999;
  }));
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
      phone: "801-555-0100",
      event_date: "2026-06-14",
      event_city: "Ogden"
    },
    handoffState: "draft"
  });

  assert.equal(payload.schema_version, "event-playground-v2");
  assert.equal(payload.level_id, "community_room");
  assert.equal(payload.screenshot_reference, "data:image/png;base64,preview");
  assert.equal(payload.customer_contact.customer_name, "Avery Planner");
  assert.equal(payload.customer_contact.email, "avery@example.com");
  assert.equal(payload.customer_contact.event_date, "2026-06-14");
  assert.equal(payload.customer_contact.event_city, "Ogden");
  assert.equal(payload.customer_contact_handoff_state, "draft");
  assert.ok(payload.placed_balloon_pieces.length >= 2);
  assert.ok(payload.placed_props.some((prop) => prop.product_family === "linen_table"));
  assert.equal(
    payload.placed_balloon_pieces.every((piece) => piece.physical_status === "production-plausible"),
    true
  );
  assert.deepEqual(payload.upsell_suggestions.accepted, ["add_matching_columns"]);
  assert.deepEqual(payload.upsell_suggestions.ignored, ["add_photo_moment"]);
  assert.equal(payload.integration_adapter.target_contract, "design-studio-v1");
  assert.equal(payload.design_studio_contract.schema_version, "design-studio-v1");
  assert.equal(payload.design_studio_contract.event.event_date, "2026-06-14");
  assert.equal(payload.design_studio_contract.event.event_city, "Ogden");
  assert.equal(payload.design_studio_contract.disclaimers.quote_requires_lt_review, true);
  assert.equal(
    payload.placed_balloon_pieces.every((piece) => piece.production_estimate?.quote_ready === false),
    true
  );
  assert.ok(payload.warnings.some((warning) => warning.code === "quote_math_pending_lt_approval"));
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
