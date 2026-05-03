(function () {
  const SOURCE_CATALOG_COLOR_VALUE_COUNT = 53;

  const LT_COLORS = [
    { name: "Reflex Champagne", hex: "#d5b986", family: "reflex" },
    { name: "Reflex Truffle", hex: "#5b4038", family: "reflex" },
    { name: "Reflex Silver", hex: "#c8ccd0", family: "reflex" },
    { name: "Reflex Gold", hex: "#b89158", family: "reflex" },
    { name: "Reflex Blue", hex: "#2f59a8", family: "reflex" },
    { name: "Reflex Green", hex: "#238259", family: "reflex" },
    { name: "Reflex Violet", hex: "#6750a4", family: "reflex" },
    { name: "Reflex Red", hex: "#b72b35", family: "reflex" },
    { name: "Dusk Cream", hex: "#efe2ce", family: "dusk" },
    { name: "Dusk Green Tea", hex: "#b7c7a4", family: "dusk" },
    { name: "Dusk Blue", hex: "#93a8be", family: "dusk" },
    { name: "Dusk Lilac", hex: "#b8a6c9", family: "dusk" },
    { name: "Dusk Rose", hex: "#c99ca5", family: "dusk" },
    { name: "Teal", hex: "#0e7f83", family: "deep" },
    { name: "Blue Slate", hex: "#2f3f53", family: "muted" },
    { name: "Smoke Grey", hex: "#737a7f", family: "neutral" },
    { name: "White", hex: "#f8f7f2", family: "neutral" },
    { name: "Black", hex: "#101010", family: "neutral" },
    { name: "Red", hex: "#c8262d", family: "bright" },
    { name: "Orange", hex: "#ef7b2d", family: "bright" },
    { name: "Yellow", hex: "#f7d84a", family: "bright" },
    { name: "Raspberry", hex: "#b21f59", family: "bright" },
    { name: "Fuchsia", hex: "#d5278d", family: "bright" },
    { name: "Bubble Gum", hex: "#f2a8cf", family: "bright" },
    { name: "Eucalyptus", hex: "#7ea38f", family: "green" },
    { name: "Forest", hex: "#1f4f36", family: "green" },
    { name: "Shamrock", hex: "#248b4d", family: "green" },
    { name: "Wintergreen", hex: "#5aa988", family: "green" },
    { name: "Lime", hex: "#9ccf39", family: "green" },
    { name: "LT Blue", hex: "#3b82c4", family: "blue" },
    { name: "Periwinkle", hex: "#8ea3da", family: "blue" },
    { name: "Royal Blue", hex: "#234ea4", family: "blue" },
    { name: "Robin's Egg", hex: "#8bcbd4", family: "blue" },
    { name: "Deep Teal", hex: "#0f3d3e", family: "deep" },
    { name: "Honey", hex: "#d9a441", family: "warm" },
    { name: "Violet", hex: "#7043a1", family: "purple" },
    { name: "Orchid", hex: "#b56bc2", family: "purple" },
    { name: "Lilac", hex: "#c4a6d8", family: "purple" },
    { name: "Chocolate", hex: "#4b2d24", family: "neutral" },
    { name: "Brown", hex: "#76503b", family: "neutral" },
    { name: "Latte", hex: "#b79572", family: "neutral" },
    { name: "Pastel Pink", hex: "#f4c1d2", family: "pastel" },
    { name: "Pastel Blue", hex: "#b8d8ee", family: "pastel" },
    { name: "Pastel Green", hex: "#bee1c3", family: "pastel" },
    { name: "Pastel Purple", hex: "#d2c2e9", family: "pastel" },
    { name: "Pastel Yellow", hex: "#f5eaa0", family: "pastel" },
    { name: "Pastel Melon", hex: "#f5b79d", family: "pastel" },
    { name: "Grey", hex: "#9a9a9a", family: "neutral" },
    { name: "Clear", hex: "#e6eef2", family: "special" },
    { name: "Blush", hex: "#e8b8b0", family: "soft" },
    { name: "Empowermint", hex: "#9ed7c2", family: "soft" }
  ];

  function normalizeColorName(name) {
    return String(name || "").trim().toLowerCase();
  }

  function getColorByName(name) {
    const normalized = normalizeColorName(name);
    return LT_COLORS.find((color) => normalizeColorName(color.name) === normalized) || LT_COLORS[0];
  }

  window.LTDesignStudio = {
    ...(window.LTDesignStudio || {}),
    LT_COLORS,
    SOURCE_CATALOG_COLOR_VALUE_COUNT,
    getColorByName
  };
})();
