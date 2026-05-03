(function () {
  const {
    calculateRenderFacts,
    colorForStructuredSlot,
    colorForWallCell,
    densityTierForId,
    designForId,
    dimensionForId,
    familyForId,
    getColorByName,
    balloonSizeForId
  } = window.LTDesignStudio;

  const DISCLAIMER = "Planning visualization. Final design and installation details are confirmed by Locally Twisted.";

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function seededRandom(seed) {
    let value = seed % 2147483647;
    if (value <= 0) value += 2147483646;
    return function next() {
      value = (value * 16807) % 2147483647;
      return (value - 1) / 2147483646;
    };
  }

  function svgFrame(inner, title = "Planning visualization preview") {
    return `
      <svg viewBox="0 0 900 520" role="img" aria-label="${escapeHtml(title)}" xmlns="http://www.w3.org/2000/svg">
        <rect width="900" height="520" fill="#f7f4ef"/>
        <line x1="70" y1="440" x2="830" y2="440" stroke="#c8beb0" stroke-width="3"/>
        ${inner}
        <text x="450" y="492" text-anchor="middle" fill="#4f5b66" font-size="15">${escapeHtml(DISCLAIMER)}</text>
      </svg>
    `;
  }

  function colorHex(colorName) {
    return getColorByName(colorName).hex;
  }

  function balloonCircle(cx, cy, radius, colorName, opacity = 1, stroke = "rgba(16,24,32,0.22)") {
    const fill = colorHex(colorName);
    const highlight = Math.max(radius * 0.18, 1.8);
    return `
      <g opacity="${opacity.toFixed(2)}">
        <circle cx="${(cx + radius * 0.18).toFixed(1)}" cy="${(cy + radius * 0.28).toFixed(1)}" r="${radius.toFixed(1)}" fill="rgba(16,24,32,0.12)"/>
        <circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${radius.toFixed(1)}" fill="${fill}" stroke="${stroke}" stroke-width="1.2"/>
        <circle cx="${(cx - radius * 0.34).toFixed(1)}" cy="${(cy - radius * 0.36).toFixed(1)}" r="${highlight.toFixed(1)}" fill="rgba(255,255,255,0.45)"/>
      </g>
    `;
  }

  function renderRuleBadge(state, x, y) {
    const facts = calculateRenderFacts(state);
    const clusters = facts.estimated_clusters === null ? "no fixed clusters" : `${facts.estimated_clusters} clusters`;
    return `
      <g aria-label="Construction math summary">
        <rect x="${x}" y="${y}" width="306" height="72" rx="8" fill="rgba(255,255,255,0.84)" stroke="rgba(16,24,32,0.14)"/>
        <text x="${x + 16}" y="${y + 25}" fill="#263446" font-size="15" font-weight="700">${escapeHtml(facts.render_engine)}</text>
        <text x="${x + 16}" y="${y + 47}" fill="#65717f" font-size="13">${facts.estimated_balloons} est. balloons; ${escapeHtml(clusters)}</text>
        <text x="${x + 16}" y="${y + 64}" fill="#65717f" font-size="12">visible_render_count: ${facts.visible_render_count}</text>
      </g>
    `;
  }

  function renderReferencePerson(x, floorY, scale = 1) {
    const headR = 10 * scale;
    const bodyH = 52 * scale;
    return `
      <g opacity="0.58" aria-label="Scale reference">
        <circle cx="${x}" cy="${floorY - bodyH - headR}" r="${headR}" fill="#65717f"/>
        <line x1="${x}" y1="${floorY - bodyH}" x2="${x}" y2="${floorY - 14 * scale}" stroke="#65717f" stroke-width="${8 * scale}" stroke-linecap="round"/>
        <line x1="${x - 17 * scale}" y1="${floorY - 12 * scale}" x2="${x + 17 * scale}" y2="${floorY - 12 * scale}" stroke="#65717f" stroke-width="${7 * scale}" stroke-linecap="round"/>
      </g>
    `;
  }

  function generateStructuredArchBalloons(state) {
    const facts = calculateRenderFacts(state);
    const dimension = dimensionForId("arch", state.dimension_id);
    const balloonSize = balloonSizeForId(state.balloon_size_id);
    const balloonRadiusFt = balloonSize.diameter_in / 24;
    const totalClusters = Math.max(1, facts.estimated_clusters);
    const visibleClusters = Math.max(1, Math.min(totalClusters, Math.floor(facts.visible_render_count / 4)));
    const archWidth = dimension.length_ft * 0.5;
    const archHeight = dimension.length_ft * 0.4;
    const scale = Math.min(650 / archWidth, 305 / archHeight);
    const offsetFromCenter = balloonRadiusFt * 0.85;
    const spiralAngle = Math.PI / 4;
    const random = seededRandom(900 + dimension.length_ft);
    const balloons = [];

    for (let visibleCluster = 0; visibleCluster < visibleClusters; visibleCluster += 1) {
      const clusterIndex = visibleClusters > 1
        ? Math.round((visibleCluster / (visibleClusters - 1)) * (totalClusters - 1))
        : 0;
      const t = totalClusters > 1 ? clusterIndex / (totalClusters - 1) : 0.5;
      const angle = t * Math.PI;
      const curveX = Math.cos(angle) * (archWidth / 2);
      const curveY = Math.sin(angle) * archHeight;
      const normalX = Math.cos(angle);
      const normalY = Math.sin(angle);
      const clusterRotation = clusterIndex * spiralAngle;

      for (let slotIndex = 0; slotIndex < 4; slotIndex += 1) {
        const slotAngle = slotIndex * Math.PI / 2 + clusterRotation;
        const offsetRadial = Math.cos(slotAngle) * offsetFromCenter;
        const offsetZ = Math.sin(slotAngle) * offsetFromCenter;
        const radiusJitter = 0.97 + random() * 0.06;
        const posJitterX = (random() - 0.5) * 0.08;
        const posJitterY = (random() - 0.5) * 0.08;
        const x = curveX + normalX * offsetRadial * radiusJitter + posJitterX;
        const y = curveY + normalY * offsetRadial * radiusJitter + posJitterY;
        const z = offsetZ * radiusJitter;
        balloons.push({
          x: 450 + x * scale + z * scale * 0.26,
          y: 434 - y * scale - z * scale * 0.08,
          z,
          radius: Math.max(4.5, balloonRadiusFt * scale * 0.78),
          colorName: colorForStructuredSlot(clusterIndex, slotIndex, state.selected_color_names, state.design_id)
        });
      }
    }

    return balloons.sort((a, b) => a.z - b.z);
  }

  function generateStructuredColumnBalloons(state) {
    const facts = calculateRenderFacts(state);
    const dimension = dimensionForId("column", state.dimension_id);
    const balloonSize = balloonSizeForId(state.balloon_size_id);
    const balloonRadiusFt = balloonSize.diameter_in / 24;
    const totalClusters = Math.max(1, facts.estimated_clusters);
    const visibleClusters = Math.max(1, Math.min(totalClusters, Math.floor(facts.visible_render_count / 4)));
    const scale = Math.min(44, 320 / dimension.height_ft);
    const offsetFromCenter = balloonRadiusFt * 0.85;
    const spiralAngle = Math.PI / 4;
    const random = seededRandom(1200 + dimension.height_ft);
    const balloons = [];

    for (let visibleCluster = 0; visibleCluster < visibleClusters; visibleCluster += 1) {
      const clusterIndex = visibleClusters > 1
        ? Math.round((visibleCluster / (visibleClusters - 1)) * (totalClusters - 1))
        : 0;
      const t = totalClusters > 1 ? clusterIndex / (totalClusters - 1) : 0.5;
      const curveY = t * dimension.height_ft;
      const clusterRotation = clusterIndex * spiralAngle;

      for (let slotIndex = 0; slotIndex < 4; slotIndex += 1) {
        const slotAngle = slotIndex * Math.PI / 2 + clusterRotation;
        const offsetX = Math.cos(slotAngle) * offsetFromCenter;
        const offsetZ = Math.sin(slotAngle) * offsetFromCenter;
        const radiusJitter = 0.97 + random() * 0.06;
        balloons.push({
          x: 450 + offsetX * scale * radiusJitter + offsetZ * scale * 0.44,
          y: 432 - curveY * scale - offsetZ * scale * 0.08 + (random() - 0.5) * 2,
          z: offsetZ,
          radius: Math.max(5.5, balloonRadiusFt * scale * 0.9),
          colorName: colorForStructuredSlot(clusterIndex, slotIndex, state.selected_color_names, state.design_id)
        });
      }
    }

    return balloons.sort((a, b) => a.z - b.z);
  }

  function renderArch(state) {
    const design = designForId("arch", state.design_id);
    if (design.engine === "organic_recipe") {
      return renderOrganicArch(state);
    }

    const balloons = generateStructuredArchBalloons(state);
    const dimension = dimensionForId("arch", state.dimension_id);
    return svgFrame(`
      <rect x="250" y="198" width="400" height="242" fill="none" stroke="#a99c8d" stroke-width="4" rx="4"/>
      <text x="450" y="176" text-anchor="middle" fill="#65717f" font-size="16">${dimension.label} arch frame</text>
      ${renderReferencePerson(705, 440, 1)}
      ${renderRuleBadge(state, 76, 58)}
      <g aria-label="Classic arch made from projected four-balloon quad clusters">
        ${balloons.map((balloon) => balloonCircle(balloon.x, balloon.y, balloon.radius, balloon.colorName)).join("")}
      </g>
    `, "Classic arch quad-cluster planning preview");
  }

  function renderColumns(state) {
    const design = designForId("column", state.design_id);
    if (design.engine === "organic_recipe") {
      return renderOrganicColumn(state);
    }

    const balloons = generateStructuredColumnBalloons(state);
    const dimension = dimensionForId("column", state.dimension_id);
    return svgFrame(`
      <rect x="378" y="104" width="144" height="336" fill="none" stroke="#a99c8d" stroke-width="4" rx="4"/>
      <line x1="450" y1="98" x2="450" y2="438" stroke="rgba(16,24,32,0.2)" stroke-width="3" stroke-dasharray="6 8"/>
      <text x="450" y="78" text-anchor="middle" fill="#65717f" font-size="16">${dimension.label} column around a center pole</text>
      ${renderReferencePerson(680, 440, 1)}
      ${renderRuleBadge(state, 76, 58)}
      <g aria-label="Classic column made from stacked four-balloon quad clusters">
        ${balloons.map((balloon) => balloonCircle(balloon.x, balloon.y, balloon.radius, balloon.colorName)).join("")}
      </g>
    `, "Classic column quad-cluster planning preview");
  }

  function organicColor(index, total, colors, designId) {
    if (!colors.length) return "White";
    if (designId === "garland_ombre") {
      const zone = Math.min(colors.length - 1, Math.floor((index / Math.max(total - 1, 1)) * colors.length));
      return colors[zone];
    }
    if (designId === "garland_accent_cluster") {
      const edge = index < total * 0.18 || index > total * 0.82;
      if (edge && colors.length > 1) return colors[(index % (colors.length - 1)) + 1];
      return colors[0];
    }
    return colors[index % colors.length];
  }

  function organicPathPoint(t, pathType) {
    if (pathType === "arch") {
      const angle = t * Math.PI;
      const x = 450 + Math.cos(angle) * 280;
      const y = 432 - Math.sin(angle) * 248;
      const tangentX = -Math.sin(angle) * 280;
      const tangentY = -Math.cos(angle) * 248;
      const length = Math.hypot(tangentX, tangentY) || 1;
      return { x, y, normalX: -tangentY / length, normalY: tangentX / length };
    }

    if (pathType === "column") {
      const wave = Math.sin(t * Math.PI * 5);
      const x = 450 + wave * 24;
      const y = 430 - t * 318;
      const tangentX = Math.cos(t * Math.PI * 5) * Math.PI * 5 * 24;
      const tangentY = -318;
      const length = Math.hypot(tangentX, tangentY) || 1;
      return { x, y, normalX: -tangentY / length, normalY: tangentX / length };
    }

    const x = 130 + t * 640;
    const y = 278 + Math.sin(t * Math.PI * 2.2) * 52 + Math.sin(t * Math.PI * 7) * 10;
    const tangentX = 640;
    const tangentY = Math.cos(t * Math.PI * 2.2) * Math.PI * 2.2 * 52
      + Math.cos(t * Math.PI * 7) * Math.PI * 7 * 10;
    const length = Math.hypot(tangentX, tangentY) || 1;
    return { x, y, normalX: -tangentY / length, normalY: tangentX / length };
  }

  function scaledOrganicMix(facts) {
    const keys = ["body_11", "accent_16", "hero_24", "filler_5"];
    const baseTotal = Math.max(1, facts.estimated_balloons);
    const counts = {};
    keys.forEach((key) => {
      counts[key] = Math.max(0, Math.round((facts.size_mix[key] || 0) * facts.visible_render_count / baseTotal));
    });
    let delta = facts.visible_render_count - keys.reduce((sum, key) => sum + counts[key], 0);
    while (delta !== 0) {
      const key = delta > 0 ? "body_11" : keys.find((candidate) => counts[candidate] > 0);
      counts[key] += delta > 0 ? 1 : -1;
      delta += delta > 0 ? -1 : 1;
    }
    return counts;
  }

  function organicAnchorT(index, count, pathType, layer, random) {
    if (layer === "primary_structure" || count <= 1) {
      return count <= 1 ? 0.5 : (index + 0.5) / count;
    }

    const heroAnchors = pathType === "column"
      ? [0.18, 0.52, 0.84]
      : [0.16, 0.5, 0.84];
    const accentAnchors = [0.08, 0.2, 0.34, 0.46, 0.58, 0.72, 0.88];
    const anchors = layer === "massing_clusters" ? accentAnchors : heroAnchors;
    const anchor = anchors[index % anchors.length];
    return Math.max(0.02, Math.min(0.98, anchor + (random() - 0.5) * 0.07));
  }

  function organicRadius(sizeKey, random) {
    if (sizeKey === "filler_5") return 6.4 + random() * 2.8;
    if (sizeKey === "hero_24") return 29 + random() * 7;
    if (sizeKey === "accent_16") return 20 + random() * 5;
    return 12.8 + random() * 4.2;
  }

  function addOrganicLayer(balloons, state, pathType, layer, sizeKey, count, random, startIndex) {
    const layerRank = layer === "primary_structure" ? 0 : layer === "massing_clusters" ? 1 : 2;
    for (let index = 0; index < count; index += 1) {
      const t = organicAnchorT(index, count, pathType, layer, random);
      const point = organicPathPoint(t, pathType);
      const radius = organicRadius(sizeKey, random);
      const side = index % 2 === 0 ? 1 : -1;
      const spread = layer === "primary_structure" ? 18 + random() * 16 : layer === "massing_clusters" ? 26 + random() * 26 : 10 + random() * 48;
      const alongJitter = layer === "filler_detail" ? (random() - 0.5) * 22 : (random() - 0.5) * 12;
      const colorName = organicColor(startIndex + index, startIndex + count, state.selected_color_names, state.design_id);
      balloons.push({
        x: point.x + point.normalX * spread * side + alongJitter,
        y: point.y + point.normalY * spread * side + (random() - 0.5) * 12,
        radius,
        colorName,
        layer,
        layerRank,
        z: layerRank * 100 + radius + random() * 10
      });
    }
  }

  function generateOrganicBalloons(state, pathType) {
    const facts = calculateRenderFacts(state);
    const random = seededRandom(1700 + facts.visible_render_count + state.selected_color_names.length);
    const mix = scaledOrganicMix(facts);
    const balloons = [];
    let startIndex = 0;

    addOrganicLayer(balloons, state, pathType, "primary_structure", "body_11", mix.body_11, random, startIndex);
    startIndex += mix.body_11;
    addOrganicLayer(balloons, state, pathType, "massing_clusters", "accent_16", mix.accent_16, random, startIndex);
    startIndex += mix.accent_16;
    addOrganicLayer(balloons, state, pathType, "massing_clusters", "hero_24", mix.hero_24, random, startIndex);
    startIndex += mix.hero_24;
    addOrganicLayer(balloons, state, pathType, "filler_detail", "filler_5", mix.filler_5, random, startIndex);

    return balloons.sort((a, b) => a.layerRank - b.layerRank || a.z - b.z);
  }

  function renderOrganicArch(state) {
    const balloons = generateOrganicBalloons(state, "arch");
    return svgFrame(`
      <path d="M170 434 C210 155 690 155 730 434" fill="none" stroke="rgba(16,24,32,0.18)" stroke-width="5" stroke-dasharray="10 10"/>
      <text x="658" y="92" text-anchor="middle" fill="#65717f" font-size="16">Organic arch path with mixed-size doublets and filler</text>
      ${renderReferencePerson(705, 440, 1)}
      ${renderRuleBadge(state, 76, 58)}
      <g aria-label="Organic arch generated from mixed-size doublets and filler">
        ${balloons.map((balloon) => balloonCircle(balloon.x, balloon.y, balloon.radius, balloon.colorName)).join("")}
      </g>
    `, "Organic arch planning preview");
  }

  function renderOrganicColumn(state) {
    const balloons = generateOrganicBalloons(state, "column");
    return svgFrame(`
      <line x1="450" y1="104" x2="450" y2="438" stroke="rgba(16,24,32,0.18)" stroke-width="5" stroke-dasharray="10 10"/>
      <text x="650" y="84" text-anchor="middle" fill="#65717f" font-size="16">Organic column path with mixed sizes</text>
      ${renderReferencePerson(680, 440, 1)}
      ${renderRuleBadge(state, 76, 58)}
      <g aria-label="Organic column generated from mixed-size doublets and filler">
        ${balloons.map((balloon) => balloonCircle(balloon.x, balloon.y, balloon.radius, balloon.colorName)).join("")}
      </g>
    `, "Organic column planning preview");
  }

  function renderOrganicGarland(state) {
    const balloons = generateOrganicBalloons(state, "garland");
    const dimension = dimensionForId("garland", state.dimension_id);
    const density = densityTierForId(state.density_tier_id);
    return svgFrame(`
      <path d="M118 282 C260 206 326 372 450 282 S642 206 782 282" fill="none" stroke="rgba(16,24,32,0.18)" stroke-width="5" stroke-dasharray="10 10"/>
      <text x="660" y="104" text-anchor="middle" fill="#65717f" font-size="16">${dimension.label}; ${density.label} density</text>
      ${renderReferencePerson(706, 440, 1)}
      ${renderRuleBadge(state, 76, 58)}
      <g aria-label="Organic garland made from doublets and filler, not fixed quad clusters">
        ${balloons.map((balloon) => balloonCircle(balloon.x, balloon.y, balloon.radius, balloon.colorName)).join("")}
      </g>
    `, "Organic garland planning preview");
  }

  function renderBackdropWall(state) {
    const dimension = dimensionForId("wall", state.dimension_id);
    const columns = Math.ceil(dimension.width_ft);
    const rows = Math.ceil(dimension.height_ft);
    const cell = Math.min(26, 650 / columns, 320 / rows);
    const gap = Math.max(1.5, cell * 0.12);
    const gridWidth = columns * cell + (columns - 1) * gap;
    const gridHeight = rows * cell + (rows - 1) * gap;
    const startX = 450 - gridWidth / 2;
    const startY = 430 - gridHeight;
    const cells = [];

    for (let row = 0; row < rows; row += 1) {
      for (let column = 0; column < columns; column += 1) {
        const x = startX + column * (cell + gap);
        const y = startY + row * (cell + gap);
        const colorName = colorForWallCell(row, column, columns, rows, state.selected_color_names, state.design_id);
        const r = Math.max(2.2, cell * 0.21);
        const offset = cell * 0.25;
        cells.push(`
          <rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${cell.toFixed(1)}" height="${cell.toFixed(1)}" rx="3" fill="rgba(255,255,255,0.54)" stroke="rgba(16,24,32,0.12)"/>
          ${balloonCircle(x + offset, y + offset, r, colorName, 0.96)}
          ${balloonCircle(x + cell - offset, y + offset, r, colorName, 0.96)}
          ${balloonCircle(x + offset, y + cell - offset, r, colorName, 0.96)}
          ${balloonCircle(x + cell - offset, y + cell - offset, r, colorName, 0.96)}
        `);
      }
    }

    return svgFrame(`
      <rect x="${(startX - 18).toFixed(1)}" y="${(startY - 18).toFixed(1)}" width="${(gridWidth + 36).toFixed(1)}" height="${(gridHeight + 36).toFixed(1)}" fill="#ffffff" stroke="#c8beb0" stroke-width="3" rx="8"/>
      <text x="662" y="${Math.max(startY - 34, 146).toFixed(1)}" text-anchor="middle" fill="#65717f" font-size="16">${dimension.label} cluster grid</text>
      ${renderReferencePerson(774, 440, 0.9)}
      ${renderRuleBadge(state, 76, 58)}
      <g aria-label="Backdrop wall made from a 4-balloon cluster grid">${cells.join("")}</g>
    `, "Backdrop wall whole-cell grid planning preview");
  }

  function renderBalloonDrop(state) {
    const dimension = dimensionForId("drop", state.dimension_id);
    const facts = calculateRenderFacts(state);
    const random = seededRandom(2500 + dimension.drop_count);
    const balloons = [];
    for (let index = 0; index < facts.visible_render_count; index += 1) {
      const colorName = state.selected_color_names[index % state.selected_color_names.length];
      const band = Math.floor(index / 20);
      balloons.push({
        x: 168 + random() * 564,
        y: 120 + random() * 234 + band * 0.7,
        radius: 6 + random() * 8,
        colorName,
        z: random()
      });
    }
    balloons.sort((a, b) => a.z - b.z);

    return svgFrame(`
      <rect x="130" y="82" width="640" height="46" rx="10" fill="rgba(16,24,32,0.08)" stroke="#a99c8d" stroke-width="3"/>
      <line x1="130" y1="128" x2="770" y2="128" stroke="#a99c8d" stroke-width="2" stroke-dasharray="7 8"/>
      <path d="M158 128 C248 202 350 184 450 232 S650 202 742 128" fill="none" stroke="rgba(16,24,32,0.15)" stroke-width="4"/>
      <text x="660" y="72" text-anchor="middle" fill="#65717f" font-size="16">${dimension.label}; released mix is representational</text>
      ${renderReferencePerson(770, 440, 0.9)}
      ${renderRuleBadge(state, 76, 58)}
      <g aria-label="Balloon drop represented as a proportional random color cloud">
        ${balloons.map((balloon) => balloonCircle(balloon.x, balloon.y, balloon.radius, balloon.colorName, 0.9)).join("")}
      </g>
    `, "Balloon drop planning preview");
  }

  function renderPreview(state) {
    const family = familyForId(state.product_family);
    if (family.id === "column") return renderColumns(state);
    if (family.id === "garland") return renderOrganicGarland(state);
    if (family.id === "wall") return renderBackdropWall(state);
    if (family.id === "drop") return renderBalloonDrop(state);
    return renderArch(state);
  }

  window.LTDesignStudio = {
    ...(window.LTDesignStudio || {}),
    renderPreview,
    renderArch,
    renderColumns,
    renderOrganicGarland,
    renderBackdropWall,
    renderBalloonDrop,
    generateStructuredArchBalloons,
    generateStructuredColumnBalloons
  };
})();
