(function () {
  const { normalizeState } = window.LTDesignStudio;

  const initialState = normalizeState({
    schema_version: "design-studio-prototype-v2",
    review_scenario: "classic_arch",
    event_context: "Corporate",
    product_family: "arch",
    design_id: "arch_swirl",
    dimension_id: "arch_25",
    balloon_size_id: "eleven_inch",
    density_tier_id: "standard",
    selected_color_names: ["Reflex Gold", "Deep Teal", "White"],
    pieces_considered: ["column"],
    disclaimer: "Planning visualization. Final design and installation details are confirmed by Locally Twisted."
  });

  function cloneState(state) {
    return {
      ...state,
      selected_color_names: [...state.selected_color_names],
      pieces_considered: [...state.pieces_considered]
    };
  }

  function createStore(initial = initialState) {
    let state = normalizeState(initial);
    const listeners = new Set();
    return {
      getState: () => cloneState(state),
      setState: (patch) => {
        state = normalizeState({ ...state, ...patch });
        listeners.forEach((listener) => listener(cloneState(state)));
      },
      subscribe: (listener) => {
        listeners.add(listener);
        return () => listeners.delete(listener);
      }
    };
  }

  window.LTDesignStudio = {
    ...(window.LTDesignStudio || {}),
    initialState,
    createStore
  };
})();
