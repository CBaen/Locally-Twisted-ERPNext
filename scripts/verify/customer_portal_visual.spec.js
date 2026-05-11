const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const CONTAINER = "locally-twisted-erpnext-v15-backend-1";
const SITE = "frontend";
const PASSWORD = `PortalPreview-${Date.now()}!`;
const OUTPUT_DIR = path.join("output", "playwright", "customer-portal");

let fixture;

function sleep(ms) {
	Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function isTransientDatabaseLock(error) {
	const stderr = error.stderr ? error.stderr.toString() : "";
	const stdout = error.stdout ? error.stdout.toString() : "";
	const message = `${error.message || ""}\n${stdout}\n${stderr}`;
	return /Deadlock found|QueryDeadlockError|Lock wait timeout/i.test(message);
}

function benchExecute(method, kwargs = {}, options = {}) {
	const args = ["exec", CONTAINER, "bench", "--site", SITE, "execute", method];
	if (Object.keys(kwargs).length) {
		args.push("--kwargs", JSON.stringify(kwargs));
	}
	const retries = options.retries || 0;
	for (let attempt = 0; attempt <= retries; attempt += 1) {
		try {
			const output = execFileSync("docker", args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
			return JSON.parse(output.trim() || "{}");
		} catch (error) {
			if (attempt < retries && isTransientDatabaseLock(error)) {
				sleep(650 * (attempt + 1));
				continue;
			}
			throw error;
		}
	}
	throw new Error(`bench execute retry loop exhausted for ${method}`);
}

async function login(page) {
	await page.goto(new URL("/login", BASE_URL).toString(), { waitUntil: "domcontentloaded" });
	const result = await page.evaluate(
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
		{ user: fixture.email, password: PASSWORD },
	);
	expect(result.status, result.body).toBe(200);
}

async function dismissCookieBanner(page) {
	const accept = page.getByRole("button", { name: "Accept" });
	if (await accept.isVisible({ timeout: 1500 }).catch(() => false)) {
		await accept.click();
	}
}

test.describe("Customer portal branded visual contract", () => {
	test.beforeAll(() => {
		fs.mkdirSync(OUTPUT_DIR, { recursive: true });
		fixture = benchExecute("locally_twisted.verify.customer_portal_review_fixture.create", {
			password: PASSWORD,
		}, { retries: 3 });
		if (!fixture.ok) {
			throw new Error(`fixture creation failed: ${JSON.stringify(fixture)}`);
		}
	});

	test.afterAll(() => {
		if (!fixture) {
			return;
		}
		benchExecute("locally_twisted.verify.customer_portal_review_fixture.cleanup", {
			email: fixture.email,
			token: fixture.token,
		});
	});

	for (const viewport of [
		{ name: "mobile", width: 375, height: 812 },
		{ name: "desktop", width: 1366, height: 768 },
	]) {
		test(`account home is branded and contained on ${viewport.name}`, async ({ page }) => {
			await page.setViewportSize(viewport);
			await login(page);
			await page.goto(new URL("/me", BASE_URL).toString(), { waitUntil: "networkidle" });
			await dismissCookieBanner(page);

			await expect(page.locator("[data-lt-customer-portal][data-lt-account-dashboard]")).toBeVisible();
			await expect(page.locator('link[href*="lt-customer-portal.css"]')).toHaveCount(1);
			const logoLoaded = await page.locator(".lt-portal__brand > img").first().evaluate((img) => img.complete && img.naturalWidth > 0);
			expect(logoLoaded).toBe(true);
			const logoSrc = await page.locator(".lt-portal__brand > img").first().getAttribute("src");
			expect(logoSrc).toContain("portal-balloon-dog-red.png");
			await expect(page.locator(".lt-portal__identity")).toContainText("Private account view");
			await expect(page.locator(".lt-portal__metric")).toHaveCount(4);
			await expect(page.locator(".lt-portal__nav a")).toHaveCount(8);
			await expect(page.locator("body")).not.toContainText("SHORT NOTICE");
			await expect(page.locator("body")).not.toContainText("Stay in the loop");
			await expect(page.locator("body")).not.toContainText("Opportunity");
			await expect(page.locator("body")).not.toContainText("Material Request");
			await expect(page.locator("body")).not.toContainText("Supplier Quotation");

			const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
			expect(overflow).toBeLessThanOrEqual(2);

			await page.screenshot({
				path: path.join(OUTPUT_DIR, `account-home-${viewport.name}.png`),
				fullPage: true,
			});
		});
	}

	test("account detail and organization routes keep the LT shell", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 768 });
		await login(page);
		for (const route of ["/account/events", "/account/quotes", "/account/files", "/organization"]) {
			await page.goto(new URL(route, BASE_URL).toString(), { waitUntil: "networkidle" });
			await dismissCookieBanner(page);
			await expect(page.locator("[data-lt-customer-portal]")).toBeVisible();
			await expect(page.locator(".lt-portal__hero")).toBeVisible();
			await expect(page.locator(".lt-portal__card").first()).toBeVisible();
			const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
			expect(overflow, `${route} overflow`).toBeLessThanOrEqual(2);
		}
	});
});
