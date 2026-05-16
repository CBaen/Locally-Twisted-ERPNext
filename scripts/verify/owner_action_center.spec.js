const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const DESK_USER = process.env.LT_DESK_TEST_USER;
const DESK_PASSWORD = process.env.LT_DESK_TEST_PASSWORD;
const PLATFORM_WORDS = /\b(?:ERPNext|Frappe|Opportunity|Pipeline Stage|Lead Owner)\b/i;

test.describe("Owner phone action center", () => {
	test.skip(!DESK_USER || !DESK_PASSWORD, "Set LT_DESK_TEST_USER and LT_DESK_TEST_PASSWORD.");

	test("owner can open a phone-first call/text surface", async ({ page }) => {
		await page.goto(new URL("/login", BASE_URL).toString(), { waitUntil: "domcontentloaded" });

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

				return {
					status: response.status,
					body: await response.text(),
				};
			},
			{ user: DESK_USER, password: DESK_PASSWORD },
		);

		expect(login.status, login.body).toBe(200);

		await page.goto(new URL("/owner-actions", BASE_URL).toString(), { waitUntil: "domcontentloaded" });
		await page.waitForLoadState("networkidle", { timeout: 10_000 }).catch(() => {});

		const body = page.locator("body");
		await expect(body).toContainText("Call or text");
		await expect(body).toContainText("Urgent contacts");
		await expect(body).toContainText("Upcoming bookings");
		await expect(page.locator("[data-owner-action-card]").first()).toBeVisible();
		await expect(page.locator("[data-owner-booking-card]").first()).toBeVisible();

		const callLinks = page.locator('a[href^="tel:"]');
		const textLinks = page.locator('a[href^="sms:"]');
		await expect(callLinks.first()).toBeVisible();
		await expect(textLinks.first()).toBeVisible();
		await expect(page.locator("a", { hasText: "Record" }).first()).toHaveAttribute("href", /\/app\//);

		const visibleText = await body.innerText();
		expect(visibleText).not.toMatch(PLATFORM_WORDS);
		await expect(body).not.toContainText("Page not found");
	});
});
