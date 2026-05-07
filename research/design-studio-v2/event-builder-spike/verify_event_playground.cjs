const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { chromium } = require("playwright");

const rootDir = __dirname;
const outputDir = path.resolve(rootDir, "../../../output/playwright/event-playground");
const serverPort = Number(process.env.EVENT_PLAYGROUND_VERIFY_PORT || 4306);

const browserCandidates = [
  process.env.PLAYWRIGHT_CHROME_PATH,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].filter(Boolean);

function assert(condition, message) {
  if (!condition) throw new Error(message);
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
    if (processRef.exitCode !== null) throw new Error(`Vite exited early with ${processRef.exitCode}`);
    try {
      const response = await fetch(url);
      if (response.ok) return;
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

async function assertCanvasNonblank(page, label) {
  const metrics = await page.evaluate(() => {
    const canvas = document.querySelector("#event-playground-canvas");
    if (!canvas) return { missing: true };
    const sample = document.createElement("canvas");
    sample.width = 180;
    sample.height = 120;
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
      if (a > 0 && (r < 242 || g < 242 || b < 242)) coloredPixels += 1;
      buckets.add(`${r >> 4}-${g >> 4}-${b >> 4}-${a >> 6}`);
    }
    return { coloredPixels, colorBuckets: buckets.size };
  });
  assert(!metrics.missing, `${label}: canvas missing`);
  assert(metrics.coloredPixels > 700, `${label}: canvas appears blank`);
  assert(metrics.colorBuckets > 30, `${label}: canvas lacks visual variation`);
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
    if (response.status() >= 400 && !url.endsWith("/favicon.ico") && !url.includes("fonts.googleapis.com")) {
      errors.push(`response: ${response.status()} ${url}`);
    }
  });

  await page.goto(`${baseUrl}/event-playground.html`);
  await page.waitForSelector("[data-event-playground-ready='true']", { timeout: 20000 });
  await assertNoOverflow(page, viewport.name);
  await assertCanvasNonblank(page, viewport.name);

  const payload = await page.evaluate(() => window.eventPlayground.getPayload());
  assert(payload.schema_version === "event-playground-v2", `${viewport.name}: wrong payload schema`);
  assert(payload.integration_adapter?.target_contract === "design-studio-v1", `${viewport.name}: missing Frappe adapter contract`);
  assert(payload.design_studio_contract?.schema_version === "design-studio-v1", `${viewport.name}: missing design-studio contract`);
  assert(payload.warnings?.some((warning) => warning.code === "quote_math_pending_lt_approval"), `${viewport.name}: missing quote honesty warning`);
  assert(payload.level_id === "school_gym", `${viewport.name}: wrong default level`);
  assert(payload.placed_balloon_pieces.length >= 2, `${viewport.name}: expected balloon pieces`);
  assert(payload.placed_props.some((prop) => prop.product_family === "linen_table"), `${viewport.name}: expected linen table prop`);
  assert(!payload.placed_balloon_pieces.some((piece) => piece.product_family.includes("organic")), `${viewport.name}: organic decor leaked into V1`);

  if (viewport.name === "desktop") {
    await page.locator("[data-tool='rotate']").click();
    await page.locator("[data-action='rotate-right']").click();
    await page.locator("[data-action='duplicate']").click();
    await page.waitForFunction(() => document.querySelector("[data-status='piece-count']").textContent === "4");
    await page.locator("[data-action='delete']").click();
    await page.waitForFunction(() => document.querySelector("[data-status='piece-count']").textContent === "3");
    await page.locator("[data-color='Pearl White']").click();
    const changed = await page.evaluate(() => window.eventPlayground.getPayload());
    assert(changed.placed_balloon_pieces.some((piece) => piece.selected_colors.includes("Pearl White")), "desktop: color update missing from payload");
  }

  assert(errors.length === 0, `${viewport.name}: ${errors.join("; ")}`);
  await page.screenshot({ path: path.join(outputDir, `${viewport.name}.png`), fullPage: true });
  await page.close();
}

async function main() {
  fs.mkdirSync(outputDir, { recursive: true });
  const server = startServer(serverPort);
  let stdout = "";
  let stderr = "";
  server.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
  server.stderr.on("data", (chunk) => { stderr += chunk.toString(); });

  try {
    const baseUrl = `http://127.0.0.1:${serverPort}`;
    await waitForServer(`${baseUrl}/event-playground.html`, server);
    const executablePath = browserCandidates.find((candidate) => fs.existsSync(candidate));
    const browser = await chromium.launch({ headless: true, executablePath, args: ["--disable-gpu"] });
    await verifyViewport(browser, baseUrl, { name: "desktop", width: 1366, height: 900 });
    await verifyViewport(browser, baseUrl, { name: "mobile", width: 390, height: 820 });
    await browser.close();
    console.log("Event Playground verification passed.");
  } catch (error) {
    if (stdout.trim()) console.error(stdout.trim());
    if (stderr.trim()) console.error(stderr.trim());
    throw error;
  } finally {
    if (server.exitCode === null) server.kill();
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
