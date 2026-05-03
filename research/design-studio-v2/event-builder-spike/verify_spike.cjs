const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { chromium } = require("playwright");

const rootDir = __dirname;
const outputDir = path.resolve(rootDir, "../../../output/playwright/design-studio-v2-event-builder-spike");
const requiredFiles = ["package.json", "playcanvas.html", "babylon.html"];
const engines = [
  { id: "playcanvas", path: "/playcanvas.html", screenshot: "playcanvas" },
  { id: "babylon", path: "/babylon.html", screenshot: "babylon" }
];
const serverPort = Number(process.env.SPIKE_VERIFY_PORT || 4277);
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
  assert(missing.length === 0, `Missing spike files: ${missing.join(", ")}`);
}

function normalizePayload(payload) {
  return {
    ...payload,
    engine: "<engine>"
  };
}

function assertPayload(payload, expectedEngine) {
  assert(payload.scene_version === "event-builder-spike-v1", `${expectedEngine}: wrong scene version`);
  assert(payload.venue === "corporate_stage", `${expectedEngine}: wrong venue`);
  assert(payload.engine === expectedEngine, `${expectedEngine}: wrong engine in payload`);
  assert(payload.camera === "fixed_isometric", `${expectedEngine}: fixed camera missing`);
  assert(Array.isArray(payload.pieces), `${expectedEngine}: pieces missing`);
  assert(payload.pieces.length >= 4, `${expectedEngine}: expected at least four rendered pieces`);

  const arch = payload.pieces.find((piece) => piece.id === "arch_1");
  assert(arch, `${expectedEngine}: arch_1 missing`);
  assert(arch.product_family === "arch", `${expectedEngine}: arch product family missing`);
  assert(arch.render_facts.estimated_balloons === 200, `${expectedEngine}: arch expected 200 balloons`);
  assert(arch.render_facts.estimated_clusters === 50, `${expectedEngine}: arch expected 50 clusters`);
  assert(arch.render_facts.balloon_diameter_ft === 0.9167, `${expectedEngine}: arch 11 inch diameter fact missing`);

  const garland = payload.pieces.find((piece) => piece.id === "garland_1");
  assert(garland, `${expectedEngine}: garland_1 missing`);
  assert(garland.product_family === "garland", `${expectedEngine}: garland product family missing`);
  assert(garland.render_facts.estimated_balloons === 97, `${expectedEngine}: garland expected 97 balloons`);
  assert(garland.render_facts.size_mix.body_11 > garland.render_facts.size_mix.filler_5, `${expectedEngine}: garland 11 inch body should dominate`);
  assert(garland.render_facts.size_layers.includes("11_inch_body"), `${expectedEngine}: garland body layer missing`);
  assert(garland.render_facts.size_layers.includes("16_24_inch_anchors"), `${expectedEngine}: garland anchor layer missing`);
  assert(garland.render_facts.size_layers.includes("5_inch_filler"), `${expectedEngine}: garland filler layer missing`);
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
      // Server not ready yet.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("Timed out waiting for Vite server");
}

function startServer(port) {
  const viteEntry = path.join(rootDir, "node_modules", "vite", "bin", "vite.js");
  assert(fs.existsSync(viteEntry), "Vite is not installed. Run npm install in the spike folder.");
  const command = process.execPath;
  const args = [viteEntry, "--host", "127.0.0.1", "--port", String(port), "--strictPort"];
  return spawn(command, args, {
    cwd: rootDir,
    stdio: ["ignore", "pipe", "pipe"],
    shell: false
  });
}

async function readPayload(page) {
  const payloadText = await page.locator("[data-payload-output]").textContent();
  return JSON.parse(payloadText);
}

async function assertNoOverflow(page, label) {
  const metrics = await page.evaluate(() => ({
    width: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth
  }));
  assert(metrics.scrollWidth <= metrics.width + 1, `${label}: horizontal overflow ${metrics.scrollWidth} > ${metrics.width}`);
}

async function assertCanvasNonblank(page, label) {
  const metrics = await page.evaluate(() => {
    const canvas = document.querySelector("canvas[data-scene-canvas]");
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
  });
  assert(!metrics.missing, `${label}: canvas missing`);
  assert(metrics.width > 0 && metrics.height > 0, `${label}: canvas has zero size`);
  assert(metrics.coloredPixels > 600, `${label}: canvas appears blank`);
  assert(metrics.colorBuckets > 12, `${label}: canvas lacks visual variation`);
}

async function assertRuntimeState(page, expectedEngine) {
  const runtime = await page.evaluate(() => window.eventBuilderSpike.getRuntimeState());
  assert(runtime.engine === expectedEngine, `${expectedEngine}: runtime engine mismatch`);
  assert(runtime.camera === "fixed_isometric", `${expectedEngine}: runtime camera mismatch`);
  assert(runtime.camera_controls === "disabled", `${expectedEngine}: customer orbit controls should be disabled`);
  assert(runtime.grid.tile_size_ft === 1, `${expectedEngine}: 1 ft grid missing`);
  assert(runtime.stage.width_ft === 24 && runtime.stage.depth_ft === 12, `${expectedEngine}: stage dimensions missing`);
  assert(runtime.performance.last_render_ms < 2500, `${expectedEngine}: render pass exceeded spike budget`);
}

async function assertDragUpdatesPayload(page, expectedEngine) {
  const before = await readPayload(page);
  const beforeArch = before.pieces.find((piece) => piece.id === "arch_1");
  const point = await page.evaluate(() => window.eventBuilderSpike.getPieceScreenPosition("arch_1"));
  assert(point && Number.isFinite(point.x) && Number.isFinite(point.y), `${expectedEngine}: arch screen position missing`);
  await page.mouse.move(point.x, point.y);
  await page.mouse.down();
  await page.mouse.move(point.x + 74, point.y + 38, { steps: 8 });
  await page.mouse.up();
  await page.waitForFunction((previousX) => {
    const payload = JSON.parse(document.querySelector("[data-payload-output]").textContent);
    return payload.pieces.find((piece) => piece.id === "arch_1").placement.x_ft !== previousX;
  }, beforeArch.placement.x_ft);
  const after = await readPayload(page);
  const afterArch = after.pieces.find((piece) => piece.id === "arch_1");
  assert(afterArch.placement.x_ft !== beforeArch.placement.x_ft || afterArch.placement.y_ft !== beforeArch.placement.y_ft, `${expectedEngine}: dragging did not update placement`);
}

async function verifyEngine(browser, baseUrl, engineConfig) {
  let desktopPayload;
  for (const viewport of viewports) {
    const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height } });
    const errors = [];
    page.on("console", (message) => {
      if (message.type() === "error") {
        errors.push(`console: ${message.text()}`);
      }
    });
    page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
    await page.goto(`${baseUrl}${engineConfig.path}`);
    await page.waitForSelector("[data-render-ready='true']", { timeout: 20000 });
    await assertNoOverflow(page, `${engineConfig.id} ${viewport.name}`);
    await assertCanvasNonblank(page, `${engineConfig.id} ${viewport.name}`);
    await assertRuntimeState(page, engineConfig.id);
    const payload = await readPayload(page);
    assertPayload(payload, engineConfig.id);
    if (viewport.name === "desktop") {
      desktopPayload = payload;
      await assertDragUpdatesPayload(page, engineConfig.id);
    }
    assert(errors.length === 0, `${engineConfig.id} ${viewport.name}: ${errors.join("; ")}`);
    await page.screenshot({
      path: path.join(outputDir, `${viewport.name}-${engineConfig.screenshot}.png`),
      fullPage: true
    });
    await page.close();
  }
  return desktopPayload;
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
    await waitForServer(`${baseUrl}/playcanvas.html`, server);
    const executablePath = browserCandidates.find((candidate) => fs.existsSync(candidate));
    const browser = await chromium.launch({
      headless: true,
      executablePath,
      args: ["--disable-gpu"]
    });
    const payloads = {};
    for (const engineConfig of engines) {
      payloads[engineConfig.id] = await verifyEngine(browser, baseUrl, engineConfig);
    }
    await browser.close();
    assert(
      JSON.stringify(normalizePayload(payloads.playcanvas)) === JSON.stringify(normalizePayload(payloads.babylon)),
      "PlayCanvas and Babylon payloads differ beyond the engine field"
    );
    console.log("Event builder spike verification passed.");
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
