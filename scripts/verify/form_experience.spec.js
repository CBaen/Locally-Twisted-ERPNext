const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";

async function dismissCookieNotice(page) {
	const banner = page.locator(".lt-cookie-consent");
	if ((await banner.count()) === 0) return;
	if (!(await banner.isVisible().catch(() => false))) return;
	await page.locator(".lt-cookie-consent__button--secondary").click();
	await expect(banner).toHaveCount(0);
}

async function fillRequiredFields(page) {
	await page.locator("#book_name").fill("Form UX Test");
	await page.locator("#book_email").fill("form-ux-test@example.com");
}

test.describe("Locally Twisted inquiry form experience", () => {
	test("cookie notice sits inline on form pages instead of covering fields", async ({ page }) => {
		await page.goto(`${BASE_URL}/contact`);

		const banner = page.locator(".lt-cookie-consent");
		await expect(banner).toBeVisible();
		await expect(banner).toHaveClass(/lt-cookie-consent--inline/);
	});

	test("shared inquiry form exposes an accessible submit status panel", async ({ page }) => {
		await page.goto(`${BASE_URL}/contact`);
		await dismissCookieNotice(page);

		const form = page.locator("form[data-form-contract='inquiry-v1']");
		await expect(form).toBeVisible();

		const status = form.locator("[data-lt-form-status]");
		await expect(status).toHaveCount(1);
		await expect(status).toHaveAttribute("aria-live", "polite");
		await expect(status).toBeHidden();
		await expect(form.locator("[data-lt-form-status-step='details']")).toHaveCount(1);
		await expect(form.locator("[data-lt-form-status-step='send']")).toHaveCount(1);
		await expect(form.locator("[data-lt-form-status-step='save']")).toHaveCount(1);
	});

	test("direct #received visits do not show fake success", async ({ page }) => {
		await page.goto(`${BASE_URL}/contact#received`);
		await dismissCookieNotice(page);

		await expect(page.locator("#received")).toBeHidden();
		await expect(page.locator("[data-lt-form-status]")).toBeHidden();
	});

	test("successful submit shows next steps without forcing the customer away", async ({ page }) => {
		await page.route("**/api/method/locally_twisted.www.book.submit_book_inquiry", async (route) => {
			await route.fulfill({
				status: 200,
				contentType: "application/json",
				body: JSON.stringify({
					message: {
						ok: true,
						lead: "LEAD-FORM-UX-TEST",
						photo_uploads: {
							customer_message: "",
						},
					},
				}),
			});
		});

		await page.goto(`${BASE_URL}/contact`);
		await dismissCookieNotice(page);
		await fillRequiredFields(page);

		await page.locator("#book_submit").click();

		const status = page.locator("[data-lt-form-status]");
		await expect(status).toBeVisible();
		await expect(status).toContainText("Request received");

		const modal = page.locator("#received");
		await expect(modal).toBeVisible();
		await expect(modal).toContainText("Request received");
		await expect(modal).toContainText("We will review it and follow up");
		await expect(modal.locator("[data-lt-modal-action='stay']")).toBeVisible();
		await expect(modal.locator("[data-lt-modal-action='home']")).toBeVisible();

		await page.waitForTimeout(4300);
		await expect(page).toHaveURL(`${BASE_URL}/contact#received`);
	});
});
