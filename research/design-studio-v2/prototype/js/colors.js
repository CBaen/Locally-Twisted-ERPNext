(function () {
  const LT_COLORS = [
    { name: "White", hex: "#f8f7f2", family: "neutral" },
    { name: "Black", hex: "#101010", family: "neutral" },
    { name: "Reflex Gold", hex: "#b89158", family: "metallic" },
    { name: "Reflex Silver", hex: "#c4c8cc", family: "metallic" },
    { name: "Deep Teal", hex: "#0f3d3e", family: "deep" },
    { name: "Blue Slate", hex: "#2f3f53", family: "muted" },
    { name: "Royal Blue", hex: "#234ea4", family: "bright" },
    { name: "Forest", hex: "#1f4f36", family: "deep" },
    { name: "Raspberry", hex: "#b21f59", family: "bright" },
    { name: "Blush", hex: "#e8b8b0", family: "soft" },
    { name: "Dusk Cream", hex: "#efe2ce", family: "muted" },
    { name: "Empowermint", hex: "#9ed7c2", family: "soft" }
  ];

  function getColorByName(name) {
    return LT_COLORS.find((color) => color.name === name) || LT_COLORS[0];
  }

  window.LTDesignStudio = {
    ...(window.LTDesignStudio || {}),
    LT_COLORS,
    getColorByName
  };
})();
