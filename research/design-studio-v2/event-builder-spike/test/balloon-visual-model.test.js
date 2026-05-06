import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  createFinishMaterial,
  createInflationSamples,
  createRoundLatexBalloonVisual,
} from "../src/balloon-visual-model.js";
import {
  createDupletVisual,
  createNestedQuadClusters,
  createQuadClusterVisual,
} from "../src/classic-cluster-geometry.js";

const nearlyEqual = (actual, expected, tolerance = 0.0001) => {
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    `expected ${actual} to be within ${tolerance} of ${expected}`,
  );
};

describe("balloon visual model", () => {
  it("models an 11 inch round latex balloon as a sized, tension-aware object", () => {
    const balloon = createRoundLatexBalloonVisual({
      balloonId: "sample-red-11",
      colorName: "Red",
      finish: "standard",
      nominalSizeIn: 11,
      sizedDiameterIn: 10,
      inflationProfile: "proper_teardrop",
      contacts: [
        {
          withBalloonId: "neighbor-white-11",
          pressure: 0.26,
          normal: [1, 0, 0],
        },
      ],
    });

    assert.equal(balloon.primitive_family, "round_latex");
    assert.equal(balloon.nominal_size_in, 11);
    assert.equal(balloon.sized_diameter_in, 10);
    assert.equal(balloon.sizing_basis, "explicit");
    nearlyEqual(balloon.dimensions.diameter_ft, 10 / 12);
    assert.equal(balloon.inflation.profile, "proper_teardrop");
    assert.ok(balloon.shape.body_scale[1] > balloon.shape.body_scale[0]);
    assert.ok(balloon.shape.neck_scale[1] > balloon.shape.neck_scale[0]);
    assert.ok(balloon.shape.knot_scale[0] > 0);
    assert.deepEqual(balloon.orientation.nozzle_axis, [0, -1, 0]);
    assert.equal(balloon.material.finish, "standard");
    assert.equal(balloon.material.metalness, 0);
    assert.equal(balloon.tension.contacts.length, 1);
    assert.ok(balloon.tension.radial_pressure > 0);
  });

  it("keeps under, properly inflated, and overinflated balloons visually distinct", () => {
    const samples = createInflationSamples({
      colorName: "Blue",
      finish: "standard",
      nominalSizeIn: 11,
      sizedDiameterIn: 10,
    });

    assert.deepEqual(
      samples.map((sample) => sample.inflation.profile),
      ["underinflated", "proper_teardrop", "overinflated"],
    );

    const [under, proper, over] = samples;
    assert.ok(under.shape.body_scale[0] < proper.shape.body_scale[0]);
    assert.ok(proper.shape.body_scale[1] > proper.shape.body_scale[0]);
    assert.ok(over.inflation.neck_inflation > proper.inflation.neck_inflation);
    assert.ok(over.tension.radial_pressure > proper.tension.radial_pressure);
  });

  it("distinguishes latex finishes without treating reflex latex as metal", () => {
    const standard = createFinishMaterial("standard", "#d92f2f");
    const reflex = createFinishMaterial("reflex", "#cda349");

    assert.equal(standard.metalness, 0);
    assert.equal(reflex.metalness, 0);
    assert.ok(reflex.clearcoat > standard.clearcoat);
    assert.ok(reflex.specular_intensity > standard.specular_intensity);
    assert.ok(reflex.roughness < standard.roughness);
  });
});

describe("classic balloon cluster geometry", () => {
  it("creates a tied duplet with mirrored balloons and reciprocal contact", () => {
    const duplet = createDupletVisual({
      clusterId: "duplet-lab",
      colors: ["Red", "White"],
      sizedDiameterIn: 10,
    });

    assert.equal(duplet.construction_unit, "duplet");
    assert.equal(duplet.balloons.length, 2);
    assert.equal(duplet.balloons[0].contacts[0].withBalloonId, duplet.balloons[1].balloon_id);
    assert.equal(duplet.balloons[1].contacts[0].withBalloonId, duplet.balloons[0].balloon_id);
    assert.ok(duplet.balloons[0].local_position[0] < 0);
    assert.ok(duplet.balloons[1].local_position[0] > 0);
    assert.ok(duplet.tie_pressure > 0);
  });

  it("creates a quad cluster with four contact-aware slots around the tie center", () => {
    const quad = createQuadClusterVisual({
      clusterId: "quad-lab",
      colors: ["Red", "White", "Red", "White"],
      sizedDiameterIn: 10,
      clusterRotationDeg: 45,
    });

    assert.equal(quad.construction_unit, "quad");
    assert.equal(quad.balloons.length, 4);
    assert.equal(new Set(quad.balloons.map((balloon) => balloon.slot)).size, 4);
    assert.ok(quad.center_pressure > 0);
    assert.ok(quad.balloons.every((balloon) => balloon.contacts.length >= 3));
    assert.ok(quad.balloons.every((balloon) => balloon.tension.center_pressure === quad.center_pressure));
    assert.ok(quad.balloons.every((balloon) => balloon.knot_axis[1] < 0));
  });

  it("nests classic quads with alternating phase and adjacency hints", () => {
    const nested = createNestedQuadClusters({
      pieceId: "nested-lab",
      count: 2,
      colors: ["Red", "White"],
      sizedDiameterIn: 10,
      rotationStepDeg: 45,
    });

    assert.equal(nested.construction_unit, "nested_quad_chain");
    assert.equal(nested.clusters.length, 2);
    assert.deepEqual(
      nested.clusters.map((cluster) => cluster.cluster_rotation_deg),
      [0, 45],
    );
    assert.equal(nested.balloons.length, 8);
    assert.ok(nested.clusters[0].adjacent_cluster_ids.includes(nested.clusters[1].cluster_id));
    assert.ok(nested.clusters[1].adjacent_cluster_ids.includes(nested.clusters[0].cluster_id));
  });
});
