(function () {
  const {
    BALLOON_SIZES,
    DENSITY_TIERS,
    EVENT_CONTEXTS,
    LT_COLORS,
    PRODUCT_FAMILIES,
    SCENARIOS,
    buildDesignPayload,
    calculateRenderFacts,
    createStore,
    designForId,
    designsForFamily,
    dimensionForId,
    dimensionsForFamily,
    familyForId,
    initialState,
    maxColorsForState,
    renderPreview,
    renderSummaryHtml,
    sourceVariantCount
  } = window.LTDesignStudio;

  const root = document.querySelector("[data-lt-design-studio]");
  if (!root) {
    throw new Error("Plan Custom Decor prototype root not found.");
  }

  const store = createStore(initialState);
  const controls = {
    reviewScenario: root.querySelector('[data-control="reviewScenario"]'),
    eventContext: root.querySelector('[data-control="eventContext"]'),
    productFamily: root.querySelector('[data-control="productFamily"]'),
    design: root.querySelector('[data-control="design"]'),
    dimension: root.querySelector('[data-control="dimension"]'),
    balloonSize: root.querySelector('[data-control="balloonSize"]'),
    densityTier: root.querySelector('[data-control="densityTier"]'),
    colors: root.querySelector('[data-control="colors"]')
  };
  const controlSections = {
    balloonSize: root.querySelector('[data-control-section="balloonSize"]'),
    densityTier: root.querySelector('[data-control-section="densityTier"]')
  };
  const preview = root.querySelector("[data-preview]");
  const summary = root.querySelector("[data-summary]");
  const summaryLine = root.querySelector("[data-summary-line]");
  const reviewStatus = root.querySelector("[data-review-status]");
  const payloadOutput = root.querySelector("[data-payload-output]");
  const ruleOutput = root.querySelector("[data-rule-output]");

  function makeButton(className, label) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.setAttribute("aria-pressed", "false");
    if (label) button.textContent = label;
    return button;
  }

  function populateSegmented(control, items, selectedValue, onSelect) {
    control.replaceChildren();
    items.forEach((item) => {
      const value = typeof item === "string" ? item : item.id;
      const label = typeof item === "string" ? item : item.label;
      const button = makeButton("segment-button", "");
      const text = document.createElement("span");
      text.textContent = label;
      button.append(text);
      button.dataset.value = value;
      button.setAttribute("aria-pressed", String(value === selectedValue));
      button.addEventListener("click", () => onSelect(value));
      control.append(button);
    });
  }

  function populateScenarioControls(state) {
    controls.reviewScenario.replaceChildren();
    SCENARIOS.forEach((scenario) => {
      const button = makeButton("scenario-button", "");
      const label = document.createElement("strong");
      const description = document.createElement("small");
      label.textContent = scenario.label;
      description.textContent = scenario.description;
      button.append(label, description);
      button.dataset.value = scenario.id;
      button.setAttribute("aria-pressed", String(scenario.id === state.review_scenario));
      button.addEventListener("click", () => {
        store.setState({
          review_scenario: scenario.id,
          ...scenario.patch,
          selected_color_names: [...scenario.patch.selected_color_names],
          pieces_considered: [...scenario.patch.pieces_considered]
        });
      });
      controls.reviewScenario.append(button);
    });
  }

  function populateProductControls(state) {
    controls.productFamily.replaceChildren();
    PRODUCT_FAMILIES.forEach((family) => {
      const button = makeButton("choice-button product-choice", "");
      const label = document.createElement("strong");
      const hint = document.createElement("small");
      const count = document.createElement("span");
      label.textContent = family.label;
      hint.textContent = family.hint;
      count.className = "choice-meta";
      count.textContent = sourceVariantCount(family) > 0 ? `${sourceVariantCount(family)} variants` : "rule-based";
      button.append(label, hint, count);
      button.dataset.value = family.id;
      button.setAttribute("aria-pressed", String(family.id === state.product_family));
      button.addEventListener("click", () => {
        store.setState({
          review_scenario: "custom_review_state",
          product_family: family.id,
          design_id: family.default_design,
          dimension_id: family.default_dimension,
          balloon_size_id: family.default_balloon_size || state.balloon_size_id,
          density_tier_id: family.default_density_tier || state.density_tier_id,
          pieces_considered: family.suggestion ? [family.suggestion] : []
        });
      });
      controls.productFamily.append(button);
    });
  }

  function populateDesignControls(state) {
    const designs = designsForFamily(state.product_family);
    controls.design.replaceChildren();
    designs.forEach((design) => {
      const button = makeButton("choice-button design-choice", "");
      const label = document.createElement("strong");
      const hint = document.createElement("small");
      label.textContent = design.label;
      hint.textContent = design.construction_basis;
      button.append(label, hint);
      button.dataset.value = design.id;
      button.setAttribute("aria-pressed", String(design.id === state.design_id));
      button.addEventListener("click", () => {
        store.setState({ review_scenario: "custom_review_state", design_id: design.id });
      });
      controls.design.append(button);
    });
  }

  function populateDimensionControls(state) {
    populateSegmented(controls.dimension, dimensionsForFamily(state.product_family), state.dimension_id, (value) => {
      store.setState({ review_scenario: "custom_review_state", dimension_id: value });
    });
  }

  function populateConditionalControls(state) {
    const family = familyForId(state.product_family);
    const design = designForId(family.id, state.design_id);
    const showBalloonSize = design.engine === "structured_cluster" && (family.id === "arch" || family.id === "column");
    const showDensity = design.engine === "organic_recipe" && (family.id === "garland" || family.id === "arch" || family.id === "column");

    controlSections.balloonSize.hidden = !showBalloonSize;
    controlSections.densityTier.hidden = !showDensity;

    populateSegmented(controls.balloonSize, BALLOON_SIZES, state.balloon_size_id, (value) => {
      store.setState({ review_scenario: "custom_review_state", balloon_size_id: value });
    });
    populateSegmented(controls.densityTier, DENSITY_TIERS, state.density_tier_id, (value) => {
      store.setState({ review_scenario: "custom_review_state", density_tier_id: value });
    });
  }

  function toggleColor(colorName) {
    const state = store.getState();
    const current = state.selected_color_names;
    const maxColors = maxColorsForState(state);
    if (current.includes(colorName)) {
      if (current.length === 1) return;
      store.setState({
        review_scenario: "custom_review_state",
        selected_color_names: current.filter((name) => name !== colorName)
      });
      return;
    }
    if (current.length >= maxColors) return;
    store.setState({ review_scenario: "custom_review_state", selected_color_names: [...current, colorName] });
  }

  function populateColorControls(state) {
    const maxColors = maxColorsForState(state);
    controls.colors.replaceChildren();
    LT_COLORS.forEach((color) => {
      const selected = state.selected_color_names.includes(color.name);
      const locked = !selected && state.selected_color_names.length >= maxColors;
      const button = makeButton("swatch-button", "");
      const chip = document.createElement("span");
      const label = document.createElement("span");
      chip.className = "swatch-chip";
      chip.style.backgroundColor = color.hex;
      label.className = "swatch-label";
      label.textContent = color.name;
      button.append(chip, label);
      button.dataset.value = color.name;
      button.disabled = locked;
      button.setAttribute("aria-pressed", String(selected));
      button.addEventListener("click", () => toggleColor(color.name));
      controls.colors.append(button);
    });
  }

  function renderRuleOutput(state) {
    const family = familyForId(state.product_family);
    const design = designForId(family.id, state.design_id);
    const dimension = dimensionForId(family.id, state.dimension_id);
    const facts = calculateRenderFacts(state);
    const clusterText = facts.estimated_clusters === null ? "not fixed" : facts.estimated_clusters;
    const dimensionLabel = dimension.label || `${dimension.width_ft || dimension.length_ft || dimension.height_ft} ft`;
    ruleOutput.innerHTML = `
      <strong>${design.engine}</strong>
      <span>${family.label}; ${design.label}; ${dimensionLabel}</span>
      <span>${facts.estimated_balloons} balloons; clusters: ${clusterText}; cap: ${maxColorsForState(state)} colors</span>
    `;
  }

  function renderControls(state) {
    populateScenarioControls(state);
    populateSegmented(controls.eventContext, EVENT_CONTEXTS, state.event_context, (value) => {
      store.setState({ review_scenario: "custom_review_state", event_context: value });
    });
    populateProductControls(state);
    populateDesignControls(state);
    populateDimensionControls(state);
    populateConditionalControls(state);
    populateColorControls(state);
  }

  function renderOutput(state) {
    const payload = buildDesignPayload(state);
    const selected = payload.selected_pieces[0];
    const facts = selected.render_facts;
    summaryLine.textContent = `${payload.event_context}: ${selected.display_label}; ${selected.design}; ${selected.selected_color_names.join(", ")}`;
    reviewStatus.textContent = `${payload.review_scenario_label}. ${selected.display_label}; ${facts.render_engine}; ${facts.estimated_balloons} estimated balloons.`;
    preview.innerHTML = renderPreview(state);
    summary.innerHTML = renderSummaryHtml(state);
    payloadOutput.textContent = JSON.stringify(payload, null, 2);
    payloadOutput.setAttribute(
      "aria-label",
      `Design payload for ${selected.display_label} with ${selected.selected_color_names.join(", ")}`
    );
    renderRuleOutput(state);
  }

  function render(state) {
    renderControls(state);
    renderOutput(state);
    window.LTDesignStudio.ready = true;
  }

  store.subscribe(render);
  render(store.getState());
})();
