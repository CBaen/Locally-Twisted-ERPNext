const { test, expect } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { gotoAndSettle, auditPageLayout, expectNoLayoutFailures } = require("./layout_helpers");

const EVENT_PLAYGROUND_PORT = Number(process.env.EVENT_PLAYGROUND_VERIFY_PORT || 4306);
const EVENT_PLAYGROUND_BASE = `http://127.0.0.1:${EVENT_PLAYGROUND_PORT}`;
const EVENT_PLAYGROUND_URL = `${EVENT_PLAYGROUND_BASE}/event-playground.html`;
const SPIKE_DIR = path.resolve(__dirname, "../..", "research/design-studio-v2/event-builder-spike");
let viteServer = null;

async function isPreviewReady() {
	try {
		const response = await fetch(EVENT_PLAYGROUND_URL);
		return response.ok;
	} catch (_) {
		return false;
	}
}

async function waitForPreview() {
	const deadline = Date.now() + 30000;
	while (Date.now() < deadline) {
		if (await isPreviewReady()) return;
		if (viteServer && viteServer.exitCode !== null) {
			throw new Error(`Event Playground Vite server exited with ${viteServer.exitCode}`);
		}
		await new Promise((resolve) => setTimeout(resolve, 250));
	}
	throw new Error(`Timed out waiting for ${EVENT_PLAYGROUND_URL}`);
}

test.beforeAll(async () => {
	if (await isPreviewReady()) return;
	const viteEntry = path.join(SPIKE_DIR, "node_modules", "vite", "bin", "vite.js");
	if (!fs.existsSync(viteEntry)) {
		throw new Error("Vite is not installed in the Event Playground spike folder.");
	}
	viteServer = spawn(
		process.execPath,
		[viteEntry, "--host", "127.0.0.1", "--port", String(EVENT_PLAYGROUND_PORT), "--strictPort"],
		{ cwd: SPIKE_DIR, stdio: ["ignore", "pipe", "pipe"], shell: false },
	);
	await waitForPreview();
});

test.afterAll(async () => {
	if (viteServer && viteServer.exitCode === null) {
		viteServer.kill();
	}
});

async function expectCanvasNonblank(page) {
	const metrics = await page.frameLocator("[data-event-playground-frame]").locator("canvas").evaluate((canvas) => {
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
	expect(metrics.coloredPixels, "canvas should be nonblank").toBeGreaterThan(700);
	expect(metrics.colorBuckets, "canvas should have visual variety").toBeGreaterThan(30);
}

test.describe("Event Playground route", () => {
	for (const viewport of [
		{ name: "mobile", width: 375, height: 900 },
		{ name: "desktop", width: 1366, height: 900 },
	]) {
		test(`loads isolated PlayCanvas game at ${viewport.name}`, async ({ page }) => {
			await page.setViewportSize({ width: viewport.width, height: viewport.height });
			const response = await gotoAndSettle(page, "/event-playground");
			expect(response, "/event-playground should respond").not.toBeNull();
			expect(response.status(), "/event-playground HTTP status").toBeLessThan(400);

			const frame = page.frameLocator("[data-event-playground-frame]");
			await expect(frame.locator("[data-event-playground-ready='true']")).toBeVisible({ timeout: 20000 });
			await expect(frame.locator("text=Event Playground")).toBeVisible();
			await expect(frame.locator("[data-action='save-draft']")).toBeVisible();
			await expect(frame.locator("[data-action='submit-inquiry']")).toBeVisible();
			await expectCanvasNonblank(page);

			const result = await auditPageLayout(page, {
				containerSelectors: [".lt-event-playground", ".lt-event-playground__shell"],
				targetSelectors: [".lt-event-playground__link", ".lt-event-playground__frame"],
			});
			expectNoLayoutFailures(expect, result, `/event-playground at ${viewport.name}`);
		});
	}

	test("select, rotate, duplicate, delete, customize, and produce payload", async ({ page }) => {
		await page.setViewportSize({ width: 1280, height: 860 });
		const response = await gotoAndSettle(page, "/event-playground");
		expect(response.status()).toBeLessThan(400);
		const frame = page.frameLocator("[data-event-playground-frame]");
		await expect(frame.locator("[data-event-playground-ready='true']")).toBeVisible({ timeout: 20000 });

		await frame.locator("[data-tool='rotate']").click();
		await frame.locator("[data-action='rotate-right']").click();
		await frame.locator("[data-action='duplicate']").click();
		await expect(frame.locator("[data-status='piece-count']")).toHaveText("4");
		await frame.locator("[data-action='delete']").click();
		await expect(frame.locator("[data-status='piece-count']")).toHaveText("3");
		await frame.locator("[data-color='Pearl White']").click();

		const payload = await page.frameLocator("[data-event-playground-frame]").locator("body").evaluate(() => window.eventPlayground.getPayload());
		expect(payload.schema_version).toBe("event-playground-v1");
		expect(payload.placed_balloon_pieces.length).toBeGreaterThanOrEqual(2);
		expect(payload.placed_balloon_pieces.some((piece) => piece.selected_colors.includes("Pearl White"))).toBe(true);
	});

	test("submit inquiry hands the design to the contact form without backend writes", async ({ page }) => {
		await page.setViewportSize({ width: 1280, height: 860 });
		const response = await gotoAndSettle(page, "/event-playground");
		expect(response.status()).toBeLessThan(400);
		const frame = page.frameLocator("[data-event-playground-frame]");
		await expect(frame.locator("[data-event-playground-ready='true']")).toBeVisible({ timeout: 20000 });

		await frame.locator("input[name='customer_name']").fill("Avery Planner");
		await frame.locator("input[name='email']").fill("avery@example.invalid");
		await frame.locator("input[name='phone']").fill("801-555-0198");
		await frame.locator("[data-action='submit-inquiry']").click();

		await page.waitForURL(/\/contact\?intent=quote&source=event-playground/, { timeout: 15000 });
		await expect(page.locator("#book_name")).toHaveValue("Avery Planner");
		await expect(page.locator("#book_email")).toHaveValue("avery@example.invalid");
		await expect(page.locator("#book_phone")).toHaveValue("801-555-0198");
		await expect(page.locator("input[name='x_services'][value='Balloon Decor']")).toBeChecked();
		await expect(page.locator("#book_notes")).toHaveValue(/Event Playground design preview/);
	});
});
