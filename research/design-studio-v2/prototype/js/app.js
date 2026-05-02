(function () {
  const {
    LT_COLORS,
    buildDesignPayload,
    renderSummaryHtml,
    renderPreview,
    EVENT_CONTEXTS,
    PIECES,
    SCALES,
    STYLES,
    labelFor,
    pieceForId,
    createStore,
    initialState
  } = window.LTDesignStudio;

  const root = document.querySelector("[data-lt-design-studio]");
  if (!root) {
    throw new Error("Plan Custom Decor prototype root not found.");
  }

  const store = createStore(initialState);
  const controls = {
    eventContext: root.querySelector('[data-control="eventContext"]'),
    pieceType: root.querySelector('[data-control="pieceType"]'),
    style: root.querySelector('[data-control="style"]'),
    scale: root.querySelector('[data-control="scale"]'),
    colors: root.querySelector('[data-control="colors"]')
  };
  const preview = root.querySelector("[data-preview]");
  const summary = root.querySelector("[data-summary]");
  const summaryLine = root.querySelector("[data-summary-line]");
  const payloadOutput = root.querySelector("[data-payload-output]");

  function makeButton(className, label) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.setAttribute("aria-pressed", "false");
    button.textContent = label;
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

  function populatePieceControls(state) {
    controls.pieceType.replaceChildren();
    PIECES.forEach((piece) => {
      const button = makeButton("choice-button", "");
      const label = document.createElement("strong");
      const hint = document.createElement("small");
      label.textContent = piece.label;
      hint.textContent = piece.hint;
      button.append(label, hint);
      button.dataset.value = piece.id;
      button.setAttribute("aria-pressed", String(piece.id === state.piece_type));
      button.addEventListener("click", () => {
        const selected = pieceForId(piece.id);
        store.setState({
          piece_type: piece.id,
          pieces_considered: selected.suggestion ? [selected.suggestion] : []
        });
      });
      controls.pieceType.append(button);
    });
  }

  function populateColorControls(state) {
    controls.colors.replaceChildren();
    LT_COLORS.forEach((color) => {
      const selected = state.selected_color_names.includes(color.name);
      const button = makeButton("swatch-button", "");
      const chip = document.createElement("span");
      const label = document.createElement("span");
      chip.className = "swatch-chip";
      chip.style.backgroundColor = color.hex;
      label.className = "swatch-label";
      label.textContent = color.name;
      button.append(chip, label);
      button.dataset.value = color.name;
      button.setAttribute("aria-pressed", String(selected));
      button.addEventListener("click", () => toggleColor(color.name));
      controls.colors.append(button);
    });
  }

  function toggleColor(colorName) {
    const state = store.getState();
    const current = state.selected_color_names;
    if (current.includes(colorName)) {
      if (current.length === 1) return;
      store.setState({ selected_color_names: current.filter((name) => name !== colorName) });
      return;
    }
    if (current.length >= 4) {
      store.setState({ selected_color_names: [...current.slice(1), colorName] });
      return;
    }
    store.setState({ selected_color_names: [...current, colorName] });
  }

  function renderControls(state) {
    populateSegmented(controls.eventContext, EVENT_CONTEXTS, state.event_context, (value) => {
      store.setState({ event_context: value });
    });
    populatePieceControls(state);
    populateSegmented(controls.style, STYLES, state.style, (value) => {
      store.setState({ style: value });
    });
    populateSegmented(controls.scale, SCALES, state.scale, (value) => {
      store.setState({ scale: value });
    });
    populateColorControls(state);
  }

  function renderOutput(state) {
    const payload = buildDesignPayload(state);
    const selected = payload.selected_pieces[0];
    summaryLine.textContent = `${payload.event_context}: ${selected.display_label} in ${selected.selected_color_names.join(", ")}`;
    preview.innerHTML = renderPreview(state);
    summary.innerHTML = renderSummaryHtml(state);
    payloadOutput.textContent = JSON.stringify(payload, null, 2);
    payloadOutput.setAttribute(
      "aria-label",
      `Design payload for ${labelFor(PIECES, state.piece_type)} with ${state.selected_color_names.join(", ")}`
    );
  }

  function render(state) {
    renderControls(state);
    renderOutput(state);
    window.LTDesignStudio.ready = true;
  }

  store.subscribe(render);
  render(store.getState());
})();
