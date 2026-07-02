const { test, expect } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { gotoAndSettle, auditPageLayout, expectNoLayoutFailures } = require("./layout_helpers");

const EVENT_PLAYGROUND_PORT = Number(process.env.EVENT_PLAYGROUND_VERIFY_PORT || 4306);
const EVENT_PLAYGROUND_BASE = `http://127.0.0.1:${EVENT_PLAYGROUND_PORT}`;
const EVENT_PLAYGROUND_URL = `${EVENT_PLAYGROUND_BASE}/event-playground.html`;
const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const DESK_USER = process.env.LT_DESK_TEST_USER;
const DESK_PASSWORD = process.env.LT_DESK_TEST_PASSWORD;
const DEFAULT_SPIKE_DIR =
	"/home/guidingl/projects/design-studio/workstreams/locally-twisted-plan-custom-decor-v2/design-studio-v2/event-builder-spike";
const SPIKE_DIR = path.resolve(process.env.EVENT_PLAYGROUND_SPIKE_DIR || DEFAULT_SPIKE_DIR);
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
	if (!DESK_USER || !DESK_PASSWORD) return;
	if (await isPreviewReady()) return;
	const viteEntry = path.join(SPIKE_DIR, "node_modules", "vite", "bin", "vite.js");
	if (!fs.existsSync(viteEntry)) {
		throw new Error(
			`Vite is not installed in the Event Playground spike folder: ${SPIKE_DIR}. Set EVENT_PLAYGROUND_SPIKE_DIR if the design-studio repo moved.`,
		);
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

async function loginAsSystemManager(page) {
	const response = await page.goto(new URL("/login", BASE_URL).toString(), { waitUntil: "domcontentloaded" });
	expect(response, "/login should respond").not.toBeNull();

	const login = await page.evaluate(
		async ({ user, password }) => {
			const response = await fetch("/api/method/login", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Requested-With": "XMLHttpRequest",
				},
				body: JSON.stringify({ usr: user, pwd: password }),
			});
			return { status: response.status, body: await response.text() };
		},
		{ user: DESK_USER, password: DESK_PASSWORD },
	);
	expect(login.status, login.body).toBe(200);
}

test.describe("Event Playground route", () => {
	test("blocks guests from the internal preview bridge", async ({ request }) => {
		const response = await request.get(new URL("/event-playground?port=12345", BASE_URL).toString(), {
			maxRedirects: 0,
		});
		expect([301, 302, 403], "guest should be redirected or denied").toContain(response.status());
		if ([301, 302].includes(response.status())) {
			expect(response.headers().location || "", "guest redirect should point at login").toContain("/login");
		}
		expect(await response.text()).not.toContain("127.0.0.1:12345/event-playground.html");
	});

	for (const viewport of [
		{ name: "mobile", width: 375, height: 900 },
		{ name: "desktop", width: 1366, height: 900 },
	]) {
		test(`loads isolated PlayCanvas game at ${viewport.name}`, async ({ page }) => {
			test.skip(!DESK_USER || !DESK_PASSWORD, "Set LT_DESK_TEST_USER and LT_DESK_TEST_PASSWORD.");
			await loginAsSystemManager(page);
			await page.setViewportSize({ width: viewport.width, height: viewport.height });
			const response = await gotoAndSettle(page, "/event-playground");
			expect(response, "/event-playground should respond").not.toBeNull();
			expect(response.status(), "/event-playground HTTP status").toBeLessThan(400);

			const frame = page.frameLocator("[data-event-playground-frame]");
			await expect(frame.locator("[data-event-playground-ready='true']")).toBeVisible({ timeout: 20000 });
			await expect(frame.locator("text=Plan Custom Decor")).toBeVisible();
			await expect(frame.locator("text=planning visualization")).toBeVisible();
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
		test.skip(!DESK_USER || !DESK_PASSWORD, "Set LT_DESK_TEST_USER and LT_DESK_TEST_PASSWORD.");
		await loginAsSystemManager(page);
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
		expect(payload.schema_version).toBe("event-playground-v2");
		expect(payload.integration_adapter.target_contract).toBe("design-studio-v1");
		expect(payload.design_studio_contract.schema_version).toBe("design-studio-v1");
		expect(payload.warnings.some((warning) => warning.code === "quote_math_pending_lt_approval")).toBe(true);
		expect(payload.placed_balloon_pieces.length).toBeGreaterThanOrEqual(2);
		expect(payload.placed_balloon_pieces.some((piece) => piece.selected_colors.includes("Pearl White"))).toBe(true);
		expect(payload.placed_balloon_pieces.every((piece) => piece.production_estimate.quote_ready === false)).toBe(true);
	});

	test("submit inquiry hands the design to the contact form without backend writes", async ({ page }) => {
		test.skip(!DESK_USER || !DESK_PASSWORD, "Set LT_DESK_TEST_USER and LT_DESK_TEST_PASSWORD.");
		await loginAsSystemManager(page);
		await page.setViewportSize({ width: 1280, height: 860 });
		const response = await gotoAndSettle(page, "/event-playground");
		expect(response.status()).toBeLessThan(400);
		const frame = page.frameLocator("[data-event-playground-frame]");
		await expect(frame.locator("[data-event-playground-ready='true']")).toBeVisible({ timeout: 20000 });

		await frame.locator("input[name='customer_name']").fill("Avery Planner");
		await frame.locator("input[name='email']").fill("avery@example.invalid");
		await frame.locator("input[name='phone']").fill("801-555-0198");
		await frame.locator("input[name='event_date']").fill("2026-06-14");
		await frame.locator("input[name='event_city']").fill("Ogden Union Station");
			await frame.locator("[data-action='submit-inquiry']").click();

			await page.waitForURL(/\/contact\?intent=quote&source=event-playground/, { timeout: 15000 });
		await expect(page.locator("#book_name")).toHaveValue("Avery Planner");
		await expect(page.locator("#book_email")).toHaveValue("avery@example.invalid");
		await expect(page.locator("#book_phone")).toHaveValue("801-555-0198");
		await expect(page.locator("#book_date")).toHaveValue("2026-06-14");
		await expect(page.locator("#book_location")).toHaveValue("Ogden Union Station");
		await expect(page.locator("input[name='x_services'][value='Balloon Decor']")).toBeChecked();
		await expect(page.locator("#book_notes")).toHaveValue(/Event Playground design preview/);
			await expect(page.locator("#book_notes")).toHaveValue(/Event date: 2026-06-14/);
			await expect(page.locator("#book_notes")).toHaveValue(/Event city \/ venue: Ogden Union Station/);
	});
});
