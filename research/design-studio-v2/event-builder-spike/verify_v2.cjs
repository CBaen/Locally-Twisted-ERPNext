const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { chromium } = require("playwright");

const rootDir = __dirname;
const outputDir = path.resolve(rootDir, "../../../output/playwright/design-studio-v2-classic-stage-builder-v2");
const serverPort = Number(process.env.CLASSIC_V2_VERIFY_PORT || 4295);

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

async function assertCanvasNonblank(page, label) {
  const metrics = await page.evaluate(() => {
    const canvas = document.querySelector("#application-canvas");
    if (!canvas) {
      return { missing: true };
    }
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
      if (a > 0 && (r < 242 || g < 242 || b < 242)) {
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
  assert(metrics.coloredPixels > 700, `${label}: canvas appears blank`);
  assert(metrics.colorBuckets > 40, `${label}: canvas lacks visual variation`);
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

  await page.goto(`${baseUrl}/classic-playcanvas-v2.html`);
  await page.waitForSelector("[data-builder-ready='true']", { timeout: 20000 });
  await assertNoOverflow(page, viewport.name);
  await assertCanvasNonblank(page, viewport.name);

  const initialState = await page.evaluate(() => window.balloonBuilderV2.getState());
  assert(initialState.pieceCount === 2, `${viewport.name}: expected two starting pieces`);
  assert(initialState.selectedLabel === "Classic Arch", `${viewport.name}: arch should start selected`);

  await page.locator("[data-mode='stage']").click();
  const box = await page.locator("#application-canvas").boundingBox();
  assert(box, `${viewport.name}: canvas box missing`);
  await page.mouse.move(box.x + box.width * 0.54, box.y + box.height * 0.46);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.68, box.y + box.height * 0.46, { steps: 8 });
  await page.mouse.up();
  await page.waitForFunction(() => window.balloonBuilderV2.getState().stageYawDeg !== 0);

  const beforeDuplicate = await page.evaluate(() => window.balloonBuilderV2.getState().pieceCount);
  await page.locator("[data-action='duplicate']").click();
  await page.waitForFunction((count) => window.balloonBuilderV2.getState().pieceCount === count + 1, beforeDuplicate);
  await page.locator("[data-action='delete']").click();
  await page.waitForFunction((count) => window.balloonBuilderV2.getState().pieceCount === count, beforeDuplicate);

  assert(errors.length === 0, `${viewport.name}: ${errors.join("; ")}`);
  await page.screenshot({
    path: path.join(outputDir, `${viewport.name}-classic-playcanvas-v2.png`),
    fullPage: true
  });
  await page.close();
}

async function main() {
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
    await waitForServer(`${baseUrl}/classic-playcanvas-v2.html`, server);
    const executablePath = browserCandidates.find((candidate) => fs.existsSync(candidate));
    const browser = await chromium.launch({
      headless: true,
      executablePath,
      args: ["--disable-gpu"]
    });
    await verifyViewport(browser, baseUrl, { name: "desktop", width: 1280, height: 860 });
    await verifyViewport(browser, baseUrl, { name: "mobile", width: 390, height: 780 });
    await browser.close();
    console.log("Classic PlayCanvas v2 verification passed.");
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
