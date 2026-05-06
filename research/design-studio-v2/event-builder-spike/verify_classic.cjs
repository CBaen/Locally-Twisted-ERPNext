const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { chromium } = require("playwright");

const rootDir = __dirname;
const outputDir = path.resolve(rootDir, "../../../output/playwright/design-studio-v2-classic-stage-builder");
const requiredFiles = ["package.json", "classic-playcanvas.html"];
const serverPort = Number(process.env.CLASSIC_VERIFY_PORT || 4281);
const viewports = [
  { name: "desktop", width: 1280, height: 860 },
  { name: "mobile", width: 390, height: 780 }
];

const browserCandidates = [
  process.env.PLAYWRIGHT_CHROME_PATH,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].filter(Boolean);

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertRequiredFiles() {
  const missing = requiredFiles.filter((fileName) => !fs.existsSync(path.join(rootDir, fileName)));
  assert(missing.length === 0, `Missing classic builder files: ${missing.join(", ")}`);
}

function startServer(port) {
  const viteEntry = path.join(rootDir, "node_modules", "vite", "bin", "vite.js");
  assert(fs.existsSync(viteEntry), "Vite is not installed. Run npm install in the spike folder.");
  return spawn(process.execPath, [viteEntry, "--host", "127.0.0.1", "--port", String(port), "--strictPort"], {
    cwd: rootDir,
    stdio: ["ignore", "pipe", "pipe"],
    shell: false
  });
}

async function waitForServer(url, processRef) {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    if (processRef.exitCode !== null) {
      throw new Error(`Vite exited early with ${processRef.exitCode}`);
    }
    try {
      const response = await fetch(url);
      if (response.ok) {
        return;
      }
    } catch (_) {
      // Server is not ready yet.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("Timed out waiting for Vite server");
}

async function assertNoOverflow(page, label) {
  const metrics = await page.evaluate(() => ({
    width: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth
  }));
  assert(metrics.scrollWidth <= metrics.width + 1, `${label}: horizontal overflow ${metrics.scrollWidth} > ${metrics.width}`);
}

async function assertCanvasNonblank(page, label, selector = "canvas[data-classic-canvas]") {
  const metrics = await page.evaluate((canvasSelector) => {
    const canvas = document.querySelector(canvasSelector);
    if (!canvas) {
      return { missing: true };
    }
    const sample = document.createElement("canvas");
    sample.width = 160;
    sample.height = 110;
    const context = sample.getContext("2d", { willReadFrequently: true });
    context.drawImage(canvas, 0, 0, sample.width, sample.height);
    const data = context.getImageData(0, 0, sample.width, sample.height).data;
    let coloredPixels = 0;
    const buckets = new Set();
    for (let index = 0; index < data.length; index += 16) {
      const r = data[index];
      const g = data[index + 1];
      const b = data[index + 2];
      const a = data[index + 3];
      if (a > 0 && (r < 245 || g < 245 || b < 245)) {
        coloredPixels += 1;
      }
      buckets.add(`${r >> 4}-${g >> 4}-${b >> 4}-${a >> 6}`);
    }
    return {
      width: canvas.width,
      height: canvas.height,
      coloredPixels,
      colorBuckets: buckets.size
    };
  }, selector);
  assert(!metrics.missing, `${label}: canvas missing`);
  assert(metrics.width > 0 && metrics.height > 0, `${label}: canvas has zero size`);
  assert(metrics.coloredPixels > 600, `${label}: canvas appears blank`);
  assert(metrics.colorBuckets > 12, `${label}: canvas lacks visual variation`);
}

async function readPayload(page) {
  return page.evaluate(() => window.classicStageBuilder.getPayload());
}

function assertPayload(payload, label) {
  assert(payload.scene_version === "playcanvas-classic-stage-builder-v1", `${label}: wrong scene version`);
  assert(payload.venue === "corporate_stage", `${label}: wrong venue`);
  assert(payload.engine === "playcanvas", `${label}: wrong engine`);
  assert(payload.view.stage_rotation_deg === 0, `${label}: default stage view rotation should be 0`);
  assert(payload.view.pan_x_ft === 0 && payload.view.pan_y_ft === 0, `${label}: default stage pan should be 0`);
  assert(payload.stage.width_ft === 24 && payload.stage.depth_ft === 12, `${label}: wrong stage size`);
  assert(Array.isArray(payload.pieces), `${label}: pieces missing`);
  assert(payload.pieces.length >= 2, `${label}: expected classic pieces`);
  assert(payload.pieces.every((piece) => piece.construction_engine === "structured_quad"), `${label}: non-classic construction leaked in`);
  assert(!payload.pieces.some((piece) => piece.product_family.includes("organic") || piece.product_family.includes("drop")), `${label}: deferred piece leaked in`);

  const arch = payload.pieces.find((piece) => piece.product_family === "classic_arch");
  assert(arch, `${label}: classic arch missing`);
  assert(arch.render_facts.estimated_clusters === 50, `${label}: arch expected 50 clusters`);
  assert(arch.render_facts.estimated_balloons === 200, `${label}: arch expected 200 balloons`);

  const columns = payload.pieces.find((piece) => piece.product_family === "classic_column_pair");
  assert(columns, `${label}: classic column pair missing`);
  assert(columns.render_facts.estimated_clusters === 32, `${label}: column pair expected 32 clusters`);
  assert(columns.render_facts.estimated_balloons === 128, `${label}: column pair expected 128 balloons`);
}

async function verifyDesktopInteractions(page) {
  const before = await readPayload(page);
  const arch = before.pieces.find((piece) => piece.id === "arch_1");
  const canvasBox = await page.locator("canvas[data-classic-canvas]").boundingBox();
  assert(canvasBox, "desktop: canvas box missing");
  const emptyPoint = {
    x: canvasBox.x + canvasBox.width * 0.86,
    y: canvasBox.y + canvasBox.height * 0.18
  };

  await page.locator('[data-stage-drag-mode="turn"]').click();
  await page.mouse.move(emptyPoint.x, emptyPoint.y);
  await page.mouse.down();
  await page.mouse.move(emptyPoint.x + 96, emptyPoint.y + 4, { steps: 8 });
  await page.mouse.up();
  await page.waitForFunction(() => window.classicStageBuilder.getPayload().view.stage_rotation_deg !== 0);

  await page.locator('[data-stage-drag-mode="move"]').click();
  const panBefore = await readPayload(page);
  await page.mouse.move(emptyPoint.x, emptyPoint.y);
  await page.mouse.down();
  await page.mouse.move(emptyPoint.x + 62, emptyPoint.y - 38, { steps: 8 });
  await page.mouse.up();
  await page.waitForFunction(
    (previousPan) => {
      const view = window.classicStageBuilder.getPayload().view;
      return view.pan_x_ft !== previousPan.pan_x_ft || view.pan_y_ft !== previousPan.pan_y_ft;
    },
    panBefore.view
  );

  await page.locator('[data-piece-drag-mode="spin"]').click();
  const spinPoint = await page.evaluate(() => window.classicStageBuilder.getPieceScreenPosition("arch_1"));
  assert(spinPoint && Number.isFinite(spinPoint.x) && Number.isFinite(spinPoint.y), "desktop: arch spin position missing");
  const rotationBeforeDrag = (await readPayload(page)).pieces.find((piece) => piece.id === "arch_1").placement.rotation_deg;
  await page.mouse.move(spinPoint.x, spinPoint.y);
  await page.mouse.down();
  await page.mouse.move(spinPoint.x + 74, spinPoint.y, { steps: 8 });
  await page.mouse.up();
  await page.waitForFunction(
    (previousRotation) => window.classicStageBuilder.getPayload().pieces.find((piece) => piece.id === "arch_1").placement.rotation_deg !== previousRotation,
    rotationBeforeDrag
  );

  await page.locator('[data-piece-drag-mode="move"]').click();
  const movePoint = await page.evaluate(() => window.classicStageBuilder.getPieceScreenPosition("arch_1"));
  assert(movePoint && Number.isFinite(movePoint.x) && Number.isFinite(movePoint.y), "desktop: arch move position missing");
  await page.mouse.move(movePoint.x, movePoint.y);
  await page.mouse.down();
  await page.mouse.move(movePoint.x + 82, movePoint.y + 44, { steps: 8 });
  await page.mouse.up();
  await page.waitForFunction((previousX) => window.classicStageBuilder.getPayload().pieces.find((piece) => piece.id === "arch_1").placement.x_ft !== previousX, arch.placement.x_ft);

  const spinInput = page.locator('[data-floating-actions] [data-rotation-input]');
  await spinInput.fill("37");
  await page.waitForFunction(() => window.classicStageBuilder.getPayload().pieces.find((piece) => piece.id === "arch_1").placement.rotation_deg === 37);

  const stageSpinInput = page.locator("[data-stage-rotation-input]");
  await stageSpinInput.fill("123");
  await page.waitForFunction(() => window.classicStageBuilder.getPayload().view.stage_rotation_deg === 123);
  const afterStageSpin = await readPayload(page);
  assert(afterStageSpin.pieces.find((piece) => piece.id === "arch_1").placement.rotation_deg === 37, "desktop: stage spin changed piece rotation");

  const countBeforeDuplicate = (await readPayload(page)).pieces.length;
  await page.locator('[data-floating-actions] [data-action="duplicate"]').click();
  await page.waitForFunction((previousCount) => window.classicStageBuilder.getPayload().pieces.length === previousCount + 1, countBeforeDuplicate);
  const duplicatedPayload = await readPayload(page);
  assert(new Set(duplicatedPayload.pieces.map((piece) => piece.id)).size === duplicatedPayload.pieces.length, "desktop: duplicated piece ID is not unique");

  await page.locator('[data-floating-actions] [data-action="delete"]').click();
  await page.waitForFunction((expectedCount) => window.classicStageBuilder.getPayload().pieces.length === expectedCount, countBeforeDuplicate);
}

async function verifyMobileControls(page) {
  const metrics = await page.evaluate(() => {
    const sheet = document.querySelector("[data-mobile-sheet]");
    const actions = document.querySelector("[data-floating-actions]");
    const spin = document.querySelector("[data-floating-actions] [data-rotation-input]");
    const stageSpin = document.querySelector("[data-stage-rotation-input]");
    const stageDragModes = document.querySelectorAll("[data-stage-drag-mode]").length;
    const pieceDragModes = document.querySelectorAll("[data-piece-drag-mode]").length;
    return {
      sheetVisible: !!sheet && getComputedStyle(sheet).display !== "none",
      actionButtons: actions ? actions.querySelectorAll("button").length : 0,
      spinVisible: !!spin && getComputedStyle(spin).display !== "none",
      stageSpinVisible: !!stageSpin && getComputedStyle(stageSpin).display !== "none",
      stageDragModes,
      pieceDragModes
    };
  });
  assert(metrics.sheetVisible, "mobile: selected-piece bottom sheet is not visible");
  assert(metrics.actionButtons >= 2, "mobile: compact action buttons missing");
  assert(metrics.spinVisible, "mobile: free-spin control missing");
  assert(metrics.stageSpinVisible, "mobile: stage-turn control missing");
  assert(metrics.stageDragModes >= 2, "mobile: stage drag mode controls missing");
  assert(metrics.pieceDragModes >= 2, "mobile: piece drag mode controls missing");
}

async function verifyViewport(browser, baseUrl, viewport) {
  const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height } });
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      const text = message.text();
      if (!text.includes("Failed to load resource: the server responded with a status of 404")) {
        errors.push(`console: ${text}`);
      }
    }
  });
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("response", (response) => {
    const url = response.url();
    if (response.status() >= 400 && !url.endsWith("/favicon.ico")) {
      errors.push(`response: ${response.status()} ${url}`);
    }
  });

  await page.goto(`${baseUrl}/classic-playcanvas.html`);
  await page.waitForSelector("[data-classic-render-ready='true']", { timeout: 20000 });
  await assertNoOverflow(page, viewport.name);
  await assertCanvasNonblank(page, viewport.name);
  assertPayload(await readPayload(page), viewport.name);

  if (viewport.name === "desktop") {
    await verifyDesktopInteractions(page);
  }
  if (viewport.name === "mobile") {
    await verifyMobileControls(page);
  }

  assert(errors.length === 0, `${viewport.name}: ${errors.join("; ")}`);
  await page.screenshot({
    path: path.join(outputDir, `${viewport.name}-classic-playcanvas.png`),
    fullPage: true
  });
  await page.close();
}

async function main() {
  assertRequiredFiles();
  fs.mkdirSync(outputDir, { recursive: true });

  const server = startServer(serverPort);
  let stdout = "";
  let stderr = "";
  server.stdout.on("data", (chunk) => {
    stdout += chunk.toString();
  });
  server.stderr.on("data", (chunk) => {
    stderr += chunk.toString();
  });

  try {
    const baseUrl = `http://127.0.0.1:${serverPort}`;
    await waitForServer(`${baseUrl}/classic-playcanvas.html`, server);
    const executablePath = browserCandidates.find((candidate) => fs.existsSync(candidate));
    const browser = await chromium.launch({
      headless: true,
      executablePath,
      args: ["--disable-gpu"]
    });
    for (const viewport of viewports) {
      await verifyViewport(browser, baseUrl, viewport);
    }
    await browser.close();
    console.log("Classic PlayCanvas stage builder verification passed.");
  } catch (error) {
    if (stdout.trim()) {
      console.error(stdout.trim());
    }
    if (stderr.trim()) {
      console.error(stderr.trim());
    }
    throw error;
  } finally {
    if (server.exitCode === null) {
      server.kill();
    }
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
