const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

const browserCandidates = [
  process.env.PLAYWRIGHT_CHROME_PATH,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].filter(Boolean);

const executablePath = browserCandidates.find((candidate) => fs.existsSync(candidate));
const indexPath = path.resolve(__dirname, "index.html");
const outDir = path.resolve("output/playwright/design-studio-v2-prototype/review-grade");

const scenarios = [
  {
    label: "Classic arch",
    productFamily: "arch",
    engine: "structured_cluster",
    minVariants: 40,
    scenarioId: "classic_arch",
    screenshot: "classic-arch"
  },
  {
    label: "Classic column",
    productFamily: "column",
    engine: "structured_cluster",
    minVariants: 40,
    scenarioId: "classic_column",
    screenshot: "classic-column"
  },
  {
    label: "Organic garland",
    productFamily: "garland",
    engine: "organic_recipe",
    minVariants: 40,
    scenarioId: "organic_garland",
    screenshot: "organic-garland"
  },
  {
    label: "Backdrop wall",
    productFamily: "wall",
    engine: "structured_grid",
    minVariants: 0,
    scenarioId: "backdrop_wall",
    screenshot: "backdrop-wall"
  },
  {
    label: "Balloon drop",
    productFamily: "drop",
    engine: "drop_mix",
    minVariants: 40,
    scenarioId: "balloon_drop",
    screenshot: "balloon-drop"
  }
];

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function payloadFrom(page) {
  const payloadText = await page.locator("[data-payload-output]").textContent();
  return JSON.parse(payloadText);
}

async function assertNoHorizontalOverflow(page, label) {
  const metrics = await page.evaluate(() => ({
    width: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth
  }));
  assert(metrics.scrollWidth <= metrics.width + 1, `${label}: horizontal overflow ${metrics.scrollWidth} > ${metrics.width}`);
}

async function assertDesktopFraming(page, label, viewport) {
  if (viewport.width < 1000) {
    return;
  }
  const positions = await page.evaluate(() => ({
    stageTop: document.querySelector(".studio-stage").getBoundingClientRect().top,
    summaryTop: document.querySelector(".studio-summary").getBoundingClientRect().top,
    introTop: document.querySelector(".studio-intro").getBoundingClientRect().top
  }));
  assert(positions.stageTop <= positions.introTop + 12, `${label}: desktop preview starts too low`);
  assert(positions.summaryTop <= positions.introTop + 12, `${label}: desktop summary starts too low`);
}

async function assertCoreState(page, label) {
  const payload = await payloadFrom(page);
  assert(payload.schema_version === "design-studio-prototype-v2", `${label}: schema version missing`);
  assert(payload.review_scenario_label, `${label}: review scenario label missing`);
  assert(payload.selected_pieces.length === 1, `${label}: selected piece missing`);
  assert(payload.selected_pieces[0].selected_color_names.length >= 2, `${label}: named colors missing`);
  assert(Array.isArray(payload.pieces_considered), `${label}: pieces considered missing`);
  assert(Array.isArray(payload.declined_suggestions), `${label}: declined suggestions missing`);
  assert(payload.render_summary.disclaimer.includes("Planning visualization"), `${label}: disclaimer missing`);
  const selected = payload.selected_pieces[0];
  assert(selected.source_products && selected.source_products.length > 0, `${label}: source product evidence missing`);
  assert(Number.isFinite(selected.variant_count), `${label}: variant count missing`);
  assert(selected.render_facts.render_engine, `${label}: render engine missing`);
  assert(Number.isFinite(selected.render_facts.estimated_balloons), `${label}: balloon estimate missing`);
  assert(Number.isFinite(selected.render_facts.visible_render_count), `${label}: visible render count missing`);
  assert(selected.render_facts.construction_basis, `${label}: construction basis missing`);
  assert(selected.selected_variant_axes, `${label}: selected variant axes missing`);
}

async function assertPhysicsState(page, scenario) {
  const payload = await payloadFrom(page);
  const selected = payload.selected_pieces[0];
  const facts = selected.render_facts;
  assert(selected.product_family === scenario.productFamily, `${scenario.label}: wrong product family`);
  assert(facts.render_engine === scenario.engine, `${scenario.label}: wrong render engine ${facts.render_engine}`);
  assert(selected.variant_count >= scenario.minVariants, `${scenario.label}: variant count too low`);
  assert(facts.estimated_balloons >= facts.visible_render_count, `${scenario.label}: visible count exceeds estimate`);

  if (scenario.productFamily === "arch") {
    assert(selected.selected_variant_axes.length_ft === 25, "Classic arch: expected 25 ft preset");
    assert(selected.selected_variant_axes.balloon_size === "11 inch", "Classic arch: expected balloon size axis");
    assert(selected.selected_color_names.length === 2, "Classic arch: expected two-color candy-cane spiral");
    assert(facts.estimated_balloons === 200, `Classic arch: expected 200 balloons, saw ${facts.estimated_balloons}`);
    assert(facts.estimated_clusters === 50, `Classic arch: expected 50 clusters, saw ${facts.estimated_clusters}`);
    assert(facts.balloons_per_foot === 8, "Classic arch: expected 40 balloons per 5 ft density");
    assert(facts.swirl_color_model === "two_color_two_balloon_bands", "Classic arch: expected two-balloon spiral bands");
    assert(facts.swirl_phase_model === "one_slot_phase_advance", "Classic arch: expected one-slot phase advance");
  }

  if (scenario.productFamily === "column") {
    assert(selected.selected_variant_axes.height_ft === 8, "Classic column: expected 8 ft height");
    assert(facts.estimated_balloons === 64, `Classic column: expected 64 balloons, saw ${facts.estimated_balloons}`);
    assert(facts.estimated_clusters === 16, `Classic column: expected 16 clusters, saw ${facts.estimated_clusters}`);
  }

  if (scenario.productFamily === "garland") {
    assert(selected.selected_variant_axes.length_ft === 9, "Organic garland: expected 9 ft length");
    assert(selected.selected_variant_axes.density_tier === "Standard", "Organic garland: expected density tier");
    assert(facts.base_balloons === 86, `Organic garland: expected 86 base balloons, saw ${facts.base_balloons}`);
    assert(facts.estimated_balloons === 97, `Organic garland: expected 97 balloons with overage, saw ${facts.estimated_balloons}`);
    assert(facts.overage_balloon_range[0] === 95 && facts.overage_balloon_range[1] === 99, "Organic garland: expected 10-15% overage range");
    assert(facts.size_mix.filler_5 > 0 && facts.size_mix.body_11 > 0 && facts.size_mix.accent_16 > 0 && facts.size_mix.hero_24 > 0, "Organic garland: construction size mix missing");
    assert(facts.size_mix.body_11 > facts.size_mix.filler_5, "Organic garland: 11-inch body balloons should dominate");
    assert(facts.visual_layers.includes("primary_structure"), "Organic garland: primary structure layer missing");
    assert(facts.visual_layers.includes("massing_clusters"), "Organic garland: massing cluster layer missing");
    assert(facts.visual_layers.includes("filler_detail"), "Organic garland: filler detail layer missing");
    assert(facts.constraints.includes("no_touching_twins"), "Organic garland: no-touching-twins constraint missing");
  }

  if (scenario.productFamily === "wall") {
    assert(selected.selected_variant_axes.width_ft === 10, "Backdrop wall: expected 10 ft width");
    assert(selected.selected_variant_axes.height_ft === 10, "Backdrop wall: expected 10 ft height");
    assert(facts.estimated_clusters === 100, `Backdrop wall: expected 100 clusters, saw ${facts.estimated_clusters}`);
    assert(facts.estimated_balloons === 400, `Backdrop wall: expected 400 balloons, saw ${facts.estimated_balloons}`);
  }

  if (scenario.productFamily === "drop") {
    assert(selected.selected_variant_axes.drop_count === 500, "Balloon drop: expected 500 count tier");
    assert(facts.estimated_balloons === 500, `Balloon drop: expected 500 balloons, saw ${facts.estimated_balloons}`);
    assert(facts.spatial_pattern_survives_release === false, "Balloon drop: stable spatial pattern must be false");
  }
}

async function runScenario(page, scenario, viewport) {
  await page.setViewportSize(viewport);
  await page.goto(pathToFileURL(indexPath).href);
  await page.waitForSelector("[data-preview] svg");
  await page.locator(`[data-control="reviewScenario"] button[data-value="${scenario.scenarioId}"]`).click();
  await page.waitForFunction(
    ({ productFamily }) => JSON.parse(document.querySelector("[data-payload-output]").textContent).selected_pieces[0].product_family === productFamily,
    { productFamily: scenario.productFamily }
  );
  await page.evaluate(() => window.scrollTo(0, 0));
  await assertNoHorizontalOverflow(page, `${scenario.label} ${viewport.width}px`);
  await assertDesktopFraming(page, scenario.label, viewport);
  await assertCoreState(page, scenario.label);
  await assertPhysicsState(page, scenario);
  const status = await page.locator("[data-review-status]").textContent();
  assert(status.includes(scenario.label), `${scenario.label}: review status did not update`);
  const prefix = viewport.width < 760 ? "mobile" : "desktop";
  await page.screenshot({
    path: path.join(outDir, `${prefix}-${scenario.screenshot}.png`),
    fullPage: true
  });
}

async function assertKeyboardAndMobileText(page) {
  await page.setViewportSize({ width: 375, height: 780 });
  await page.goto(pathToFileURL(indexPath).href);
  await page.waitForSelector("[data-preview] svg");
  await page.keyboard.press("Tab");
  const focused = await page.evaluate(() => {
    const active = document.activeElement;
    const styles = window.getComputedStyle(active);
    return {
      tag: active.tagName,
      outlineWidth: styles.outlineWidth,
      outlineStyle: styles.outlineStyle
    };
  });
  assert(focused.tag === "BUTTON", "Tab did not reach a button control");
  assert(focused.outlineStyle !== "none" && focused.outlineWidth !== "0px", "Focused control lacks visible outline");

  const swatchOverflowCount = await page.evaluate(() =>
    Array.from(document.querySelectorAll(".swatch-button")).filter((button) => button.scrollWidth > button.clientWidth + 1).length
  );
  assert(swatchOverflowCount === 0, `Mobile swatch label overflow count ${swatchOverflowCount}`);

  await page.locator('[data-control="reviewScenario"] button[data-value="backdrop_wall"]').click();
  await page.waitForFunction(() =>
    JSON.parse(document.querySelector("[data-payload-output]").textContent).selected_pieces[0].product_family === "wall"
  );
  const disabledOverflowColors = await page.evaluate(() =>
    Array.from(document.querySelectorAll(".swatch-button[disabled]")).length
  );
  assert(disabledOverflowColors > 0, "Color cap should disable overflow color choices");
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ headless: true, executablePath });
  const page = await browser.newPage();
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });
  page.on("pageerror", (error) => consoleErrors.push(error.message));

  for (const scenario of scenarios) {
    await runScenario(page, scenario, { width: 1440, height: 900 });
    await runScenario(page, scenario, { width: 375, height: 780 });
  }
  await assertKeyboardAndMobileText(page);

  assert(consoleErrors.length === 0, `Console or page errors: ${consoleErrors.join(" | ")}`);
  await browser.close();
  console.log("Design Studio prototype review-grade browser verification passed.");
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
