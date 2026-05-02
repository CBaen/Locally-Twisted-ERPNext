(function () {
  const initialState = {
    schema_version: "design-studio-prototype-v1",
    event_context: "Corporate",
    piece_type: "classic_arch",
    style: "spiral",
    scale: "door",
    selected_color_names: ["Reflex Gold", "Deep Teal"],
    pieces_considered: ["classic_columns"],
    disclaimer: "Planning visualization. Final design and installation details are confirmed by Locally Twisted."
  };

  function createStore(initial = initialState) {
    let state = { ...initial };
    const listeners = new Set();
    return {
      getState: () => ({
        ...state,
        selected_color_names: [...state.selected_color_names],
        pieces_considered: [...state.pieces_considered]
      }),
      setState: (patch) => {
        state = { ...state, ...patch };
        listeners.forEach((listener) => listener(state));
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
