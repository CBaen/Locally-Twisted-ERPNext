(function () {
  const {
    getColorByName,
    colorForCluster,
    estimateArchClusters,
    estimateBackdropClusters,
    estimateColumnClusters,
    scaleForId
  } = window.LTDesignStudio;

  const DISCLAIMER = "Planning visualization. Final design and installation details are confirmed by Locally Twisted.";

  function svgFrame(inner) {
    return `
      <svg viewBox="0 0 760 420" role="img" aria-label="Planning visualization preview" xmlns="http://www.w3.org/2000/svg">
        <rect width="760" height="420" fill="#f7f4ef"/>
        <line x1="70" y1="350" x2="690" y2="350" stroke="#c8beb0" stroke-width="3"/>
        ${inner}
        <text x="380" y="392" text-anchor="middle" fill="#4f5b66" font-size="15">${DISCLAIMER}</text>
      </svg>
    `;
  }

  function balloonCircle(cx, cy, radius, colorName, extra = "") {
    const color = getColorByName(colorName);
    return `
      <g ${extra}>
        <circle cx="${cx}" cy="${cy}" r="${radius}" fill="rgba(16,24,32,0.14)" transform="translate(3 5)"/>
        <circle cx="${cx}" cy="${cy}" r="${radius}" fill="${color.hex}" stroke="rgba(16,24,32,0.22)" stroke-width="1.5"/>
        <circle cx="${cx - radius * 0.32}" cy="${cy - radius * 0.36}" r="${Math.max(radius * 0.18, 2)}" fill="rgba(255,255,255,0.46)"/>
      </g>
    `;
  }

  function referenceFrame(label, width = 190, height = 210) {
    const x = 380 - width / 2;
    const y = 350 - height;
    return `
      <rect x="${x}" y="${y}" width="${width}" height="${height}" fill="none" stroke="#9d9488" stroke-width="4" rx="4"/>
      <text x="380" y="${y - 14}" text-anchor="middle" fill="#65717f" font-size="16">${label}</text>
    `;
  }

  function renderCluster(cx, cy, radius, clusterIndex, colorNames, style, rotation = 0) {
    const offsets = [
      [Math.cos(rotation) * radius * 0.72, Math.sin(rotation) * radius * 0.72],
      [Math.cos(rotation + Math.PI / 2) * radius * 0.72, Math.sin(rotation + Math.PI / 2) * radius * 0.72],
      [Math.cos(rotation + Math.PI) * radius * 0.72, Math.sin(rotation + Math.PI) * radius * 0.72],
      [Math.cos(rotation + Math.PI * 1.5) * radius * 0.72, Math.sin(rotation + Math.PI * 1.5) * radius * 0.72]
    ];

    return offsets
      .map(([dx, dy], slotIndex) => {
        const colorName = colorForCluster(clusterIndex, slotIndex, colorNames, style);
        return balloonCircle((cx + dx).toFixed(1), (cy + dy).toFixed(1), radius, colorName);
      })
      .join("");
  }

  function scaleLabel(scaleId) {
    const scale = scaleForId(scaleId);
    if (scale.id === "door") return "Door scale";
    if (scale.id === "stage") return "Stage scale";
    return "Venue scale";
  }

  function renderPreview(state) {
    if (state.piece_type === "classic_columns") return renderColumns(state);
    if (state.piece_type === "backdrop_wall") return renderBackdrop(state);
    return renderArch(state);
  }

  function renderArch(state) {
    const scale = scaleForId(state.scale);
    const trueClusters = estimateArchClusters(scale.feet);
    const visibleClusters = Math.min(trueClusters, 32);
    const rx = scale.id === "gym" ? 270 : scale.id === "stage" ? 245 : 220;
    const ry = scale.id === "gym" ? 210 : scale.id === "stage" ? 190 : 170;
    const radius = scale.id === "gym" ? 10 : 11;
    const clusters = [];

    for (let index = 0; index < visibleClusters; index += 1) {
      const t = visibleClusters === 1 ? 0 : index / (visibleClusters - 1);
      const angle = Math.PI - t * Math.PI;
      const cx = 380 + Math.cos(angle) * rx;
      const cy = 350 - Math.sin(angle) * ry;
      clusters.push(renderCluster(cx, cy, radius, index, state.selected_color_names, state.style, index * Math.PI / 4));
    }

    return svgFrame(`
      ${referenceFrame(scaleLabel(scale.id))}
      <text x="108" y="326" fill="#65717f" font-size="14">Estimated clusters: ${trueClusters}</text>
      <g aria-label="Classic arch made from repeated four-balloon clusters">${clusters.join("")}</g>
    `);
  }

  function renderColumns(state) {
    const scale = scaleForId(state.scale);
    const heightFt = scale.id === "gym" ? 10 : scale.id === "stage" ? 8 : 7;
    const trueClusters = estimateColumnClusters(heightFt);
    const visibleRows = Math.min(trueClusters, 18);
    const rowGap = scale.id === "gym" ? 16 : 18;
    const radius = scale.id === "gym" ? 9 : 10;
    const startY = 334;
    const leftX = 200;
    const rightX = 560;
    const rows = [];

    for (let row = 0; row < visibleRows; row += 1) {
      const y = startY - row * rowGap;
      const rotation = state.style === "stripe" ? 0 : row * Math.PI / 2;
      rows.push(renderCluster(leftX, y, radius, row, state.selected_color_names, state.style, rotation));
      rows.push(renderCluster(rightX, y, radius, row, state.selected_color_names, state.style, rotation));
    }

    return svgFrame(`
      ${referenceFrame(scaleLabel(scale.id), scale.id === "gym" ? 230 : 190, scale.id === "gym" ? 240 : 205)}
      <rect x="186" y="${startY - visibleRows * rowGap - 12}" width="28" height="${visibleRows * rowGap + 22}" fill="rgba(16,24,32,0.06)" rx="12"/>
      <rect x="546" y="${startY - visibleRows * rowGap - 12}" width="28" height="${visibleRows * rowGap + 22}" fill="rgba(16,24,32,0.06)" rx="12"/>
      <text x="108" y="326" fill="#65717f" font-size="14">Estimated clusters per pair: ${trueClusters * 2}</text>
      <g aria-label="Pair of classic columns made from stacked four-balloon clusters">${rows.join("")}</g>
    `);
  }

  function backdropDimensions(scaleId) {
    if (scaleId === "gym") return { columns: 12, rows: 8, label: "Wide venue wall" };
    if (scaleId === "stage") return { columns: 10, rows: 8, label: "Stage photo wall" };
    return { columns: 8, rows: 8, label: "Entry photo wall" };
  }

  function colorForBackdropCell(row, column, columns, rows, colorNames, style) {
    const colors = colorNames.length ? colorNames : ["White"];
    if (style === "solid") return colors[0];
    if (style === "stripe") return colors[column % colors.length];
    if (style === "banded") {
      const bandHeight = Math.max(1, Math.ceil(rows / colors.length));
      return colors[Math.floor(row / bandHeight) % colors.length];
    }
    return colors[(row + column) % colors.length];
  }

  function renderBackdrop(state) {
    const scale = scaleForId(state.scale);
    const { columns, rows, label } = backdropDimensions(scale.id);
    const trueClusters = estimateBackdropClusters(columns, rows);
    const cellSize = 24;
    const gap = 3;
    const gridWidth = columns * cellSize + (columns - 1) * gap;
    const gridHeight = rows * cellSize + (rows - 1) * gap;
    const startX = 380 - gridWidth / 2;
    const startY = 332 - gridHeight;
    const cells = [];

    for (let row = 0; row < rows; row += 1) {
      for (let column = 0; column < columns; column += 1) {
        const colorName = colorForBackdropCell(row, column, columns, rows, state.selected_color_names, state.style);
        const color = getColorByName(colorName);
        const x = startX + column * (cellSize + gap);
        const y = startY + row * (cellSize + gap);
        cells.push(`
          <rect x="${x}" y="${y}" width="${cellSize}" height="${cellSize}" rx="7" fill="${color.hex}" stroke="rgba(16,24,32,0.2)" stroke-width="1.2"/>
          <circle cx="${x + 8}" cy="${y + 7}" r="3" fill="rgba(255,255,255,0.38)"/>
        `);
      }
    }

    return svgFrame(`
      <rect x="${startX - 18}" y="${startY - 18}" width="${gridWidth + 36}" height="${gridHeight + 36}" fill="#ffffff" stroke="#c8beb0" stroke-width="3" rx="8"/>
      <text x="380" y="${startY - 34}" text-anchor="middle" fill="#65717f" font-size="16">${label}</text>
      <text x="108" y="326" fill="#65717f" font-size="14">Estimated clusters: ${trueClusters}</text>
      <g aria-label="Backdrop wall made from a whole-cell balloon cluster grid">${cells.join("")}</g>
    `);
  }

  window.LTDesignStudio = {
    ...(window.LTDesignStudio || {}),
    renderPreview,
    renderArch,
    renderColumns,
    renderBackdrop
  };
})();
