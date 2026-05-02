(function () {
  const EVENT_CONTEXTS = [
    "Corporate",
    "School",
    "City/community",
    "Venue/photo op",
    "Wedding/private",
    "Not sure"
  ];

  const PIECES = [
    {
      id: "classic_arch",
      label: "Classic arch",
      suggestion: "classic_columns",
      hint: "Frames an entrance, stage, or check-in moment."
    },
    {
      id: "classic_columns",
      label: "Pair of classic columns",
      suggestion: "backdrop_wall",
      hint: "Adds height beside doors, stages, or photo areas."
    },
    {
      id: "backdrop_wall",
      label: "Backdrop/photo-op wall",
      suggestion: "classic_arch",
      hint: "Creates a focused wall for photos or presentations."
    }
  ];

  const STYLES = [
    { id: "solid", label: "Solid" },
    { id: "spiral", label: "Spiral" },
    { id: "banded", label: "Color-blocked" },
    { id: "stripe", label: "Stripe" }
  ];

  const SCALES = [
    { id: "door", label: "Door / entry", feet: 20 },
    { id: "stage", label: "Stage moment", feet: 25 },
    { id: "gym", label: "Gym / venue", feet: 30 }
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

  function estimateArchClusters(lengthFt, balloonsPerFoot = 7) {
    return Math.ceil((lengthFt * balloonsPerFoot) / 4);
  }

  function estimateColumnClusters(heightFt, balloonsPerFoot = 8) {
    return Math.ceil((heightFt * balloonsPerFoot) / 4);
  }

  function estimateBackdropClusters(widthFt, heightFt) {
    return widthFt * heightFt;
  }

  function colorForCluster(clusterIndex, slotIndex, colorNames, style) {
    const colors = colorNames.length ? colorNames : ["White"];
    if (style === "solid") return colors[0];
    if (style === "banded") return colors[Math.floor(clusterIndex / 2) % colors.length];
    if (style === "stripe") return colors[slotIndex % colors.length];
    if (colors.length === 3) {
      const repeat = [
        [colors[0], colors[0], colors[1], colors[2]],
        [colors[0], colors[1], colors[1], colors[2]],
        [colors[0], colors[1], colors[2], colors[2]]
      ];
      return repeat[clusterIndex % 3][slotIndex];
    }
    return colors[(clusterIndex + slotIndex) % colors.length];
  }

  function labelFor(list, id) {
    const found = list.find((item) => item.id === id);
    return found ? found.label : id;
  }

  function scaleForId(scaleId) {
    return SCALES.find((scale) => scale.id === scaleId) || SCALES[0];
  }

  function pieceForId(pieceId) {
    return PIECES.find((piece) => piece.id === pieceId) || PIECES[0];
  }

  window.LTDesignStudio = {
    ...(window.LTDesignStudio || {}),
    EVENT_CONTEXTS,
    PIECES,
    STYLES,
    SCALES,
    gcd,
    minimumClusterRepeat,
    estimateArchClusters,
    estimateColumnClusters,
    estimateBackdropClusters,
    colorForCluster,
    labelFor,
    scaleForId,
    pieceForId
  };
})();
