(function () {
  const EVENT_CONTEXTS = [
    "Corporate",
    "School",
    "City/community",
    "Venue/photo op",
    "Wedding/private",
    "Not sure"
  ];

  const ENGINE_LABELS = {
    structured_cluster: "Structured cluster",
    structured_grid: "Structured grid",
    organic_recipe: "Organic recipe",
    drop_mix: "Drop mix"
  };

  const PRODUCT_FAMILIES = [
    {
      id: "arch",
      label: "Classic arch",
      product_label: "Arch product family",
      hint: "Classic and organic arches share the same customer product family.",
      suggestion: "column",
      default_design: "arch_swirl",
      default_dimension: "arch_25",
      default_balloon_size: "eleven_inch",
      source_products: [
        { name: "Classic Arch", slug: "classic-arch", variant_count: 848 },
        { name: "Classic Organic Arch", slug: "classic-organic-arch", variant_count: 636 },
        { name: "Premium Organic Arch", slug: "premium-organic-arch", variant_count: 424 }
      ]
    },
    {
      id: "column",
      label: "Classic column",
      product_label: "Column product family",
      hint: "Classic and organic columns are design options inside one planning family.",
      suggestion: "arch",
      default_design: "column_classic_spiral",
      default_dimension: "column_8",
      default_balloon_size: "eleven_inch",
      source_products: [
        { name: "Classic Column", slug: "classic-column", variant_count: 1908 },
        { name: "Classic Organic columns", slug: "classic-organic-columns", variant_count: 318 },
        { name: "Pemium Organic Column", slug: "pemium-organic-column", variant_count: 636 }
      ]
    },
    {
      id: "garland",
      label: "Organic garland",
      product_label: "Garland product family",
      hint: "Always organic: doublets on a strip with mixed sizes and filler.",
      suggestion: "wall",
      default_design: "garland_organic_blend",
      default_dimension: "garland_9",
      default_density_tier: "standard",
      source_products: [
        { name: "Classic Organic Balloon Garland", slug: "classic-organic-balloon-garland", variant_count: 159 },
        { name: "Premium Organic Garland", slug: "premium-organic-garland", variant_count: 159 },
        { name: "Organic Grab n' Go", slug: "organic-grab-n-go", variant_count: 156 }
      ]
    },
    {
      id: "wall",
      label: "Backdrop wall",
      product_label: "Backdrop / wall product family",
      hint: "Any-size wall represented as a whole-cluster grid.",
      suggestion: "garland",
      default_design: "wall_lattice",
      default_dimension: "wall_10x10",
      source_products: [
        { name: "Backdrop / Wall spec", slug: "product-details-backdrop-wall", variant_count: 0 }
      ]
    },
    {
      id: "drop",
      label: "Balloon drop",
      product_label: "Balloon drop",
      hint: "Literal count tier; released colors become a proportional mix.",
      suggestion: "column",
      default_design: "drop_classic_mix",
      default_dimension: "drop_500",
      source_products: [
        { name: "Balloon Drop", slug: "balloon-drop", variant_count: 159 }
      ]
    }
  ];

  const DESIGNS_BY_FAMILY = {
    arch: [
      {
        id: "arch_swirl",
        label: "Swirl",
        engine: "structured_cluster",
        max_colors: 4,
        construction_basis: "4-balloon quads along an arch frame; each quad rotates 45 degrees."
      },
      {
        id: "arch_layered",
        label: "Layered",
        engine: "structured_cluster",
        max_colors: 8,
        construction_basis: "4-balloon quads in two-cluster color bands along the arch frame."
      },
      {
        id: "arch_organic",
        label: "Organic",
        engine: "organic_recipe",
        max_colors: 6,
        construction_basis: "Mixed-size doublets and filler follow an arch path, not fixed quads."
      }
    ],
    column: [
      {
        id: "column_classic_spiral",
        label: "Classic spiral",
        engine: "structured_cluster",
        max_colors: 4,
        construction_basis: "4-balloon quads stacked around a pole; each quad rotates 45 degrees."
      },
      {
        id: "column_classic_banded",
        label: "Classic color block",
        engine: "structured_cluster",
        max_colors: 4,
        construction_basis: "Whole quad bands stack around a central pole."
      },
      {
        id: "column_organic",
        label: "Organic",
        engine: "organic_recipe",
        max_colors: 6,
        construction_basis: "Mixed-size doublets and filler form a vertical organic column."
      }
    ],
    garland: [
      {
        id: "garland_organic_blend",
        label: "Organic blend",
        engine: "organic_recipe",
        max_colors: 6,
        construction_basis: "Doublets on a strip with 5 inch filler and controlled randomness."
      },
      {
        id: "garland_ombre",
        label: "Ombre",
        engine: "organic_recipe",
        max_colors: 4,
        construction_basis: "Feathered color zones on an organic doublet-and-filler backbone."
      },
      {
        id: "garland_accent_cluster",
        label: "Accent cluster",
        engine: "organic_recipe",
        max_colors: 6,
        construction_basis: "Organic placement with deliberate color accents near ends or focal points."
      }
    ],
    wall: [
      {
        id: "wall_solid",
        label: "Solid",
        engine: "structured_grid",
        max_colors: 1,
        construction_basis: "One 4-balloon quad per square-foot grid cell."
      },
      {
        id: "wall_vertical_stripes",
        label: "Vertical stripes",
        engine: "structured_grid",
        max_colors: 6,
        construction_basis: "Whole columns of grid cells become stripes; no sub-cell stripes."
      },
      {
        id: "wall_color_blocks",
        label: "Color blocks",
        engine: "structured_grid",
        max_colors: 3,
        construction_basis: "Large rectangular blocks of whole cluster cells."
      },
      {
        id: "wall_lattice",
        label: "Lattice",
        engine: "structured_grid",
        max_colors: 3,
        construction_basis: "Background cells plus full-cell diagonal accent bands."
      }
    ],
    drop: [
      {
        id: "drop_classic_mix",
        label: "Classic mix",
        engine: "drop_mix",
        max_colors: 4,
        construction_basis: "Air-filled balloons in a pre-strung drop net; no spatial pattern survives release."
      },
      {
        id: "drop_confetti_mix",
        label: "Confetti mix",
        engine: "drop_mix",
        max_colors: 6,
        construction_basis: "Representational color cloud for a literal balloon-count tier."
      }
    ]
  };

  const BALLOON_SIZES = [
    { id: "five_inch", label: "5 inch", diameter_in: 5, balloons_per_foot: 12.5 },
    { id: "nine_inch", label: "9 inch", diameter_in: 9, balloons_per_foot: 7.5 },
    { id: "eleven_inch", label: "11 inch", diameter_in: 11, balloons_per_foot: 8 },
    { id: "sixteen_inch", label: "14-16 inch", diameter_in: 16, balloons_per_foot: 4.5 }
  ];

  const DENSITY_TIERS = [
    { id: "light", label: "Light", balloons_per_foot: 5.5 },
    { id: "standard", label: "Standard", balloons_per_foot: 9.5 },
    { id: "lush", label: "Lush", balloons_per_foot: 12 },
    { id: "mixed_premium", label: "Mixed-size premium", balloons_per_foot: 14 }
  ];

  const DIMENSIONS_BY_FAMILY = {
    arch: [
      { id: "arch_20", label: "20 ft", length_ft: 20 },
      { id: "arch_25", label: "25 ft", length_ft: 25 },
      { id: "arch_30", label: "30 ft", length_ft: 30 },
      { id: "arch_35", label: "35 ft", length_ft: 35 }
    ],
    column: [
      { id: "column_5", label: "5 ft", height_ft: 5 },
      { id: "column_6", label: "6 ft", height_ft: 6 },
      { id: "column_7", label: "7 ft", height_ft: 7 },
      { id: "column_8", label: "8 ft", height_ft: 8 },
      { id: "column_9", label: "9 ft", height_ft: 9 },
      { id: "column_10", label: "10 ft", height_ft: 10 }
    ],
    garland: [
      { id: "garland_6", label: "6 ft", length_ft: 6 },
      { id: "garland_9", label: "9 ft", length_ft: 9 },
      { id: "garland_12", label: "12 ft", length_ft: 12 }
    ],
    wall: [
      { id: "wall_8x8", label: "8 x 8 ft", width_ft: 8, height_ft: 8 },
      { id: "wall_10x10", label: "10 x 10 ft", width_ft: 10, height_ft: 10 },
      { id: "wall_10x30", label: "10 x 30 ft", width_ft: 30, height_ft: 10 }
    ],
    drop: [
      { id: "drop_250", label: "250 balloons", drop_count: 250 },
      { id: "drop_500", label: "500 balloons", drop_count: 500 },
      { id: "drop_1000", label: "1000 balloons", drop_count: 1000 }
    ]
  };

  const SCENARIOS = [
    {
      id: "classic_arch",
      label: "Classic arch",
      description: "25 ft structured arch with a two-color candy-cane spiral.",
      patch: {
        event_context: "Corporate",
        product_family: "arch",
        design_id: "arch_swirl",
        dimension_id: "arch_25",
        balloon_size_id: "eleven_inch",
        density_tier_id: "standard",
        selected_color_names: ["Reflex Gold", "Deep Teal"],
        pieces_considered: ["column"]
      }
    },
    {
      id: "classic_column",
      label: "Classic column",
      description: "8 ft column using stacked quad-cluster spiral math.",
      patch: {
        event_context: "School",
        product_family: "column",
        design_id: "column_classic_spiral",
        dimension_id: "column_8",
        balloon_size_id: "eleven_inch",
        density_tier_id: "standard",
        selected_color_names: ["Royal Blue", "Reflex Silver", "White"],
        pieces_considered: ["arch"]
      }
    },
    {
      id: "organic_garland",
      label: "Organic garland",
      description: "9 ft standard-density organic recipe with mixed sizes.",
      patch: {
        event_context: "Wedding/private",
        product_family: "garland",
        design_id: "garland_organic_blend",
        dimension_id: "garland_9",
        density_tier_id: "standard",
        selected_color_names: ["Dusk Cream", "Blush", "Empowermint"],
        pieces_considered: ["wall"]
      }
    },
    {
      id: "backdrop_wall",
      label: "Backdrop wall",
      description: "10 x 10 ft whole-cell lattice grid.",
      patch: {
        event_context: "Venue/photo op",
        product_family: "wall",
        design_id: "wall_lattice",
        dimension_id: "wall_10x10",
        density_tier_id: "standard",
        selected_color_names: ["Black", "Reflex Gold", "White"],
        pieces_considered: ["garland"]
      }
    },
    {
      id: "balloon_drop",
      label: "Balloon drop",
      description: "500-balloon air-filled drop mix.",
      patch: {
        event_context: "City/community",
        product_family: "drop",
        design_id: "drop_classic_mix",
        dimension_id: "drop_500",
        density_tier_id: "standard",
        selected_color_names: ["Royal Blue", "White", "Reflex Silver"],
        pieces_considered: ["column"]
      }
    }
  ];

  function gcd(a, b) {
    let x = Math.abs(a);
    let y = Math.abs(b);
    while (y) {
      const temp = y;
      y = x % y;
      x = temp;
    }
    return x || 1;
  }

  function minimumClusterRepeat(colorCount) {
    return colorCount / gcd(colorCount, 4);
  }

  function labelFor(list, id) {
    const found = list.find((item) => item.id === id);
    return found ? found.label : id;
  }

  function familyForId(familyId) {
    return PRODUCT_FAMILIES.find((family) => family.id === familyId) || PRODUCT_FAMILIES[0];
  }

  function designsForFamily(familyId) {
    return DESIGNS_BY_FAMILY[familyForId(familyId).id] || DESIGNS_BY_FAMILY.arch;
  }

  function designForId(familyId, designId) {
    const designs = designsForFamily(familyId);
    return designs.find((design) => design.id === designId) || designs[0];
  }

  function dimensionsForFamily(familyId) {
    return DIMENSIONS_BY_FAMILY[familyForId(familyId).id] || DIMENSIONS_BY_FAMILY.arch;
  }

  function dimensionForId(familyId, dimensionId) {
    const dimensions = dimensionsForFamily(familyId);
    return dimensions.find((dimension) => dimension.id === dimensionId) || dimensions[0];
  }

  function balloonSizeForId(balloonSizeId) {
    return BALLOON_SIZES.find((size) => size.id === balloonSizeId) || BALLOON_SIZES[2];
  }

  function densityTierForId(densityTierId) {
    return DENSITY_TIERS.find((tier) => tier.id === densityTierId) || DENSITY_TIERS[1];
  }

  function sourceVariantCount(family) {
    return family.source_products.reduce((sum, product) => sum + product.variant_count, 0);
  }

  function dropColorCap(dimension) {
    if (dimension.drop_count >= 1000) return 6;
    if (dimension.drop_count >= 500) return 4;
    return 3;
  }

  function maxColorsForState(state) {
    const family = familyForId(state.product_family);
    const design = designForId(family.id, state.design_id);
    const dimension = dimensionForId(family.id, state.dimension_id);
    if (family.id === "drop") return Math.min(design.max_colors, dropColorCap(dimension));
    return design.max_colors;
  }

  function normalizeState(inputState) {
    const family = familyForId(inputState.product_family);
    const design = designForId(family.id, inputState.design_id || family.default_design);
    const dimension = dimensionForId(family.id, inputState.dimension_id || family.default_dimension);
    const maxColors = maxColorsForState({
      ...inputState,
      product_family: family.id,
      design_id: design.id,
      dimension_id: dimension.id
    });
    const selectedColors = (inputState.selected_color_names && inputState.selected_color_names.length
      ? inputState.selected_color_names
      : ["White"]).slice(0, maxColors);

    return {
      ...inputState,
      product_family: family.id,
      design_id: design.id,
      dimension_id: dimension.id,
      balloon_size_id: inputState.balloon_size_id || family.default_balloon_size || "eleven_inch",
      density_tier_id: inputState.density_tier_id || family.default_density_tier || "standard",
      selected_color_names: selectedColors,
      pieces_considered: inputState.pieces_considered || (family.suggestion ? [family.suggestion] : [])
    };
  }

  function estimateStructuredByLength(lengthFt, balloonSize) {
    const estimatedBalloons = Math.ceil(lengthFt * balloonSize.balloons_per_foot);
    return {
      estimated_balloons: estimatedBalloons,
      estimated_clusters: Math.ceil(estimatedBalloons / 4)
    };
  }

  function estimateColumnByHeight(heightFt) {
    const estimatedBalloons = Math.ceil(heightFt * 8);
    return {
      estimated_balloons: estimatedBalloons,
      estimated_clusters: Math.ceil(estimatedBalloons / 4)
    };
  }

  function estimateOrganicRecipe(lengthFt, densityTier) {
    const baseBalloons = Math.ceil(lengthFt * densityTier.balloons_per_foot);
    const overageBalloonRange = [
      Math.ceil(baseBalloons * 1.1),
      Math.ceil(baseBalloons * 1.15)
    ];
    const estimatedBalloons = Math.ceil(baseBalloons * 1.12);
    const hero24 = Math.min(5, Math.max(2, Math.round(lengthFt / 3)));
    const body11 = Math.round(estimatedBalloons * 0.55);
    const accent16 = Math.round(estimatedBalloons * 0.15);
    const filler5 = Math.max(0, estimatedBalloons - body11 - accent16 - hero24);
    return {
      base_balloons: baseBalloons,
      estimated_balloons: estimatedBalloons,
      overage_balloon_range: overageBalloonRange,
      planning_overage_rate: 0.12,
      size_mix: {
        small: filler5,
        mid: body11,
        large: accent16 + hero24,
        filler_5: filler5,
        body_11: body11,
        accent_16: accent16,
        hero_24: hero24
      },
      visual_layers: ["primary_structure", "massing_clusters", "filler_detail"]
    };
  }

  function estimateWallGrid(widthFt, heightFt) {
    const estimatedClusters = Math.ceil(widthFt) * Math.ceil(heightFt);
    return {
      estimated_clusters: estimatedClusters,
      estimated_balloons: estimatedClusters * 4,
      overage_balloon_range: [
        Math.ceil(estimatedClusters * 4 * 1.1),
        Math.ceil(estimatedClusters * 4 * 1.15)
      ]
    };
  }

  function selectedVariantAxes(state) {
    const normalized = normalizeState(state);
    const family = familyForId(normalized.product_family);
    const design = designForId(family.id, normalized.design_id);
    const dimension = dimensionForId(family.id, normalized.dimension_id);
    const balloonSize = balloonSizeForId(normalized.balloon_size_id);
    const densityTier = densityTierForId(normalized.density_tier_id);
    const axes = { design: design.label };

    if (family.id === "arch") {
      axes.length_ft = dimension.length_ft;
      axes.balloon_size = balloonSize.label;
    } else if (family.id === "column") {
      axes.height_ft = dimension.height_ft;
      axes.balloon_size = balloonSize.label;
    } else if (family.id === "garland") {
      axes.length_ft = dimension.length_ft;
      axes.density_tier = densityTier.label;
    } else if (family.id === "wall") {
      axes.width_ft = dimension.width_ft;
      axes.height_ft = dimension.height_ft;
    } else if (family.id === "drop") {
      axes.drop_count = dimension.drop_count;
    }

    return axes;
  }

  function calculateRenderFacts(state) {
    const normalized = normalizeState(state);
    const family = familyForId(normalized.product_family);
    const design = designForId(family.id, normalized.design_id);
    const dimension = dimensionForId(family.id, normalized.dimension_id);
    const balloonSize = balloonSizeForId(normalized.balloon_size_id);
    const densityTier = densityTierForId(normalized.density_tier_id);
    const colorCount = normalized.selected_color_names.length;
    const common = {
      render_engine: design.engine,
      construction_basis: design.construction_basis,
      customer_visible_precision: "planning_visual",
      constraints: []
    };

    if (design.engine === "structured_cluster" && family.id === "arch") {
      const estimate = estimateStructuredByLength(dimension.length_ft, balloonSize);
      const isSpiral = normalized.design_id.includes("swirl") || normalized.design_id.includes("spiral");
      return {
        ...common,
        ...estimate,
        count_basis: "length_ft_x_balloon_size",
        balloons_per_foot: balloonSize.balloons_per_foot,
        minimum_cluster_repeat: minimumClusterRepeat(colorCount),
        geometry_cluster_rotation_degrees: 45,
        ...(isSpiral ? {
          swirl_phase_model: "one_slot_phase_advance",
          swirl_phase_degrees: 90,
          swirl_color_model: colorCount === 2 ? "two_color_two_balloon_bands" : "one_balloon_per_color_lane"
        } : {}),
        visible_render_count: Math.min(estimate.estimated_balloons, 160),
        constraints: [
          "four_balloon_quad",
          "45_degree_cluster_rotation",
          "whole_clusters",
          ...(isSpiral && colorCount === 2 ? ["two_balloon_color_bands"] : [])
        ]
      };
    }

    if (design.engine === "structured_cluster" && family.id === "column") {
      const estimate = estimateColumnByHeight(dimension.height_ft);
      const isSpiral = normalized.design_id.includes("swirl") || normalized.design_id.includes("spiral");
      return {
        ...common,
        ...estimate,
        count_basis: "height_ft_x_column_density",
        balloons_per_foot: 8,
        minimum_cluster_repeat: minimumClusterRepeat(colorCount),
        geometry_cluster_rotation_degrees: 45,
        ...(isSpiral ? {
          swirl_phase_model: "one_slot_phase_advance",
          swirl_phase_degrees: 90,
          swirl_color_model: colorCount === 2 ? "two_color_two_balloon_bands" : "one_balloon_per_color_lane"
        } : {}),
        visible_render_count: Math.min(estimate.estimated_balloons, 160),
        constraints: [
          "four_balloon_quad",
          "central_pole",
          "45_degree_cluster_rotation",
          ...(isSpiral && colorCount === 2 ? ["two_balloon_color_bands"] : [])
        ]
      };
    }

    if (design.engine === "structured_grid") {
      const estimate = estimateWallGrid(dimension.width_ft, dimension.height_ft);
      return {
        ...common,
        ...estimate,
        count_basis: "width_ft_x_height_ft_grid",
        visible_render_count: Math.min(estimate.estimated_balloons, 720),
        constraints: ["four_balloon_quad", "whole_cell_grid", "no_sub_cluster_stripes"]
      };
    }

    if (design.engine === "organic_recipe") {
      const lengthFt = dimension.length_ft || dimension.height_ft || 9;
      const estimate = estimateOrganicRecipe(lengthFt, densityTier);
      return {
        ...common,
        ...estimate,
        estimated_clusters: null,
        count_basis: "length_ft_x_density_tier",
        density_per_foot: densityTier.balloons_per_foot,
        visible_render_count: Math.min(estimate.estimated_balloons, 160),
        constraints: ["doublet_and_filler", "mixed_sizes", "controlled_randomness", "no_touching_twins"]
      };
    }

    if (design.engine === "drop_mix") {
      return {
        ...common,
        estimated_balloons: dimension.drop_count,
        estimated_clusters: null,
        count_basis: "literal_drop_count_tier",
        visible_render_count: Math.min(dimension.drop_count, 140),
        spatial_pattern_survives_release: false,
        constraints: ["air_filled_drop_net", "proportional_random_mix", "no_stable_release_pattern"]
      };
    }

    return {
      ...common,
      estimated_balloons: 0,
      estimated_clusters: null,
      visible_render_count: 0,
      count_basis: "unknown"
    };
  }

  function colorForStructuredSlot(clusterIndex, slotIndex, colorNames, designId) {
    const colors = colorNames.length ? colorNames : ["White"];
    if (designId.includes("layered") || designId.includes("banded")) {
      return colors[Math.floor(clusterIndex / 2) % colors.length];
    }
    const isSpiral = designId.includes("swirl") || designId.includes("spiral");
    if (colors.length === 1) return colors[0];
    if (isSpiral && colors.length === 2) {
      const phaseSlot = (slotIndex + clusterIndex) % 4;
      return phaseSlot < 2 ? colors[0] : colors[1];
    }
    if (isSpiral && colors.length === 4) {
      return colors[(slotIndex + clusterIndex) % colors.length];
    }
    if (isSpiral) {
      return colors[(slotIndex + clusterIndex) % colors.length];
    }
    if (colors.length === 2) return colors[slotIndex % 2];
    if (colors.length === 3) {
      const repeat = [
        [colors[0], colors[0], colors[1], colors[2]],
        [colors[0], colors[1], colors[1], colors[2]],
        [colors[0], colors[1], colors[2], colors[2]]
      ];
      return repeat[clusterIndex % 3][slotIndex];
    }
    return colors[slotIndex % colors.length];
  }

  function colorForWallCell(row, column, columns, rows, colorNames, designId) {
    const colors = colorNames.length ? colorNames : ["White"];
    if (designId === "wall_solid") return colors[0];
    if (designId === "wall_vertical_stripes") return colors[column % colors.length];
    if (designId === "wall_color_blocks") {
      const bandHeight = Math.max(1, Math.ceil(rows / colors.length));
      return colors[Math.floor(row / bandHeight) % colors.length];
    }
    if (designId === "wall_lattice") {
      const background = colors[0];
      const diagonalA = colors[1] || colors[0];
      const diagonalB = colors[2] || diagonalA;
      const down = (row + column) % 5 === 0;
      const up = (row - column + columns) % 6 === 0;
      if (down && up) return diagonalB;
      if (down) return diagonalA;
      if (up) return diagonalB;
      return background;
    }
    return colors[(row + column) % colors.length];
  }

  function scenarioForId(scenarioId) {
    return SCENARIOS.find((scenario) => scenario.id === scenarioId) || null;
  }

  window.LTDesignStudio = {
    ...(window.LTDesignStudio || {}),
    EVENT_CONTEXTS,
    ENGINE_LABELS,
    PRODUCT_FAMILIES,
    DESIGNS_BY_FAMILY,
    BALLOON_SIZES,
    DENSITY_TIERS,
    DIMENSIONS_BY_FAMILY,
    SCENARIOS,
    gcd,
    minimumClusterRepeat,
    labelFor,
    familyForId,
    designsForFamily,
    designForId,
    dimensionsForFamily,
    dimensionForId,
    balloonSizeForId,
    densityTierForId,
    sourceVariantCount,
    maxColorsForState,
    normalizeState,
    selectedVariantAxes,
    calculateRenderFacts,
    colorForStructuredSlot,
    colorForWallCell,
    scenarioForId
  };
})();
