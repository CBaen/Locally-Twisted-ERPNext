const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const CONTAINER = "locally-twisted-erpnext-v15-backend-1";
const SITE = "frontend";
const PASSWORD = `PortalLogin-${Date.now()}!`;
const OUTPUT_DIR = path.join("output", "playwright", "customer-login");

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

async function dismissCookieBanner(page) {
	const accept = page.getByRole("button", { name: "Accept" });
	if (await accept.isVisible({ timeout: 1500 }).catch(() => false)) {
		await accept.click();
	}
}

async function assertBrandedLogin(page, screenshotName) {
	await page.goto(new URL("/login#login", BASE_URL).toString(), { waitUntil: "networkidle" });
	await dismissCookieBanner(page);

	await expect(page.locator("[data-lt-customer-login]")).toBeVisible();
	await expect(page.locator('link[href*="lt-login.css"]')).toHaveCount(1);
	await expect(page.locator("section.for-login .login-content.page-card")).toBeVisible();
	await expect(page.locator("#login_email")).toBeVisible();
	await expect(page.locator("#login_password")).toBeVisible();
	await expect(page.locator("section.for-login .btn-login").first()).toBeVisible();
	await expect(page.locator("body")).toContainText("Welcome back");
	await expect(page.locator("body")).toContainText("Private customer account");
	await expect(page.locator("body")).not.toContainText("SHORT NOTICE");
	await expect(page.locator("body")).not.toContainText("Stay in the loop");
	await expect(page.locator("body")).not.toContainText("Sign up");

	const logoLoaded = await page
		.locator(".lt-login__brand > img")
		.first()
		.evaluate((img) => img.complete && img.naturalWidth > 0);
	expect(logoLoaded).toBe(true);
	const logoSrc = await page.locator(".lt-login__brand > img").first().getAttribute("src");
	expect(logoSrc).toContain("portal-balloon-dog-red.png");

	const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
	expect(overflow).toBeLessThanOrEqual(2);

	await page.screenshot({
		path: path.join(OUTPUT_DIR, screenshotName),
		fullPage: true,
	});
}

test.describe("Customer login branded visual contract", () => {
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
		test(`login page is branded and contained on ${viewport.name}`, async ({ page }) => {
			await page.setViewportSize(viewport);
			await assertBrandedLogin(page, `login-${viewport.name}.png`);
		});
	}

	test("website customer can sign in from the branded form", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await assertBrandedLogin(page, "login-before-signin.png");

		await page.locator("#login_email").fill(fixture.email);
		await page.locator("#login_password").fill(PASSWORD);
		await page.locator("section.for-login .btn-login").first().click();

		await expect
			.poll(
				async () => {
					const cookies = await page.context().cookies(BASE_URL);
					const sid = cookies.find((cookie) => cookie.name === "sid");
					return Boolean(sid && sid.value && sid.value !== "Guest");
				},
				{ timeout: 15000, message: "customer login did not set an authenticated sid cookie" },
			)
			.toBe(true);

		await page.goto(new URL("/me", BASE_URL).toString(), { waitUntil: "networkidle" });
		await dismissCookieBanner(page);
		await expect(page.locator("[data-lt-customer-portal][data-lt-account-dashboard]")).toBeVisible();
		await expect(page.locator(".lt-portal__identity")).toContainText("Private account view");
	});

	test("public signup route stays invite-first and branded", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await page.goto(new URL("/login#signup", BASE_URL).toString(), { waitUntil: "networkidle" });
		await dismissCookieBanner(page);

		await expect(page.locator("[data-lt-customer-login]")).toBeVisible();
		await expect(page.locator("section.for-signup")).toBeVisible();
		await expect(page.locator("section.for-signup")).toContainText("Create an account");
		await expect(page.locator("section.for-signup")).toContainText("Accounts are invite-only");
		await expect(page.locator("section.for-signup")).toContainText("Customer accounts are created by invitation");
		await expect(page.locator("body")).not.toContainText("SHORT NOTICE");
		await expect(page.locator("body")).not.toContainText("Stay in the loop");

		const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
		expect(overflow).toBeLessThanOrEqual(2);

		await page.screenshot({
			path: path.join(OUTPUT_DIR, "signup-invite-first-mobile.png"),
			fullPage: true,
		});
	});
});
