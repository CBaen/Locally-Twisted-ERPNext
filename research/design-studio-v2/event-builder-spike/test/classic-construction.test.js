import test from "node:test";
import assert from "node:assert/strict";

import { createClassicArch, createClassicColumnPair } from "../src/classic-construction.js";

test("classic arch uses whole quad clusters and the approved 25 ft reference count", () => {
  const arch = createClassicArch({
    id: "arch_1",
    lengthFt: 25,
    balloonSizeIn: 11,
    pattern: "two_color_spiral",
    selectedColorNames: ["Reflex Gold", "Deep Teal"]
  });

  assert.equal(arch.product_family, "classic_arch");
  assert.equal(arch.construction_engine, "structured_quad");
  assert.equal(arch.render_facts.construction_basis, "classic_4_balloon_quad_cluster");
  assert.equal(arch.render_facts.estimated_clusters, 50);
  assert.equal(arch.render_facts.estimated_balloons, 200);
  assert.equal(arch.render_facts.cluster_size, 4);
  assert.equal(arch.render_facts.balloons_per_foot, 8);
  assert.equal(arch.pattern, "two_color_spiral");
  assert.deepEqual(arch.selected_color_names, ["Reflex Gold", "Deep Teal"]);
});

test("classic column pair uses stacked quads around two poles", () => {
  const columns = createClassicColumnPair({
    id: "column_pair_1",
    heightFt: 8,
    balloonSizeIn: 11,
    pattern: "two_color_spiral",
    selectedColorNames: ["Pearl White", "Reflex Gold"]
  });

  assert.equal(columns.product_family, "classic_column_pair");
  assert.equal(columns.construction_engine, "structured_quad");
  assert.equal(columns.render_facts.construction_basis, "classic_4_balloon_quad_cluster");
  assert.equal(columns.render_facts.columns, 2);
  assert.equal(columns.render_facts.estimated_clusters_per_column, 16);
  assert.equal(columns.render_facts.estimated_balloons_per_column, 64);
  assert.equal(columns.render_facts.estimated_clusters, 32);
  assert.equal(columns.render_facts.estimated_balloons, 128);
  assert.equal(columns.pattern, "two_color_spiral");
});
