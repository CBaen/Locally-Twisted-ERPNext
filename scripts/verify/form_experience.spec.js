const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const CONFIRMATION_COPY = "A confirmation of your request will be sent to your email address shortly. We will be in contact within 24 hours!";

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
		await expect(form.locator("[data-lt-form-status-step]")).toHaveCount(0);
		await expect(page.getByText("Details checked")).toHaveCount(0);
		await expect(page.getByText("Saved for follow-up")).toHaveCount(0);
		await expect(page.getByText("No account needed")).toHaveCount(0);
		await expect(page.getByRole("button", { name: "Send Request" })).toHaveCount(0);
	});

	test("direct #received visits do not show fake success", async ({ page }) => {
		await page.goto(`${BASE_URL}/contact#received`);
		await dismissCookieNotice(page);

		await expect(page.locator("#received")).toBeHidden();
		await expect(page.locator("[data-lt-form-status]")).toBeHidden();
	});

	test("successful submit shows a quiet confirmation without forcing the customer away", async ({ page }) => {
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
		await expect(modal).toContainText(CONFIRMATION_COPY);
		await expect(modal.locator("[data-lt-modal-action='stay']")).toBeVisible();
		await expect(modal.locator("[data-lt-modal-action='home']")).toHaveCount(0);
		await expect(modal).not.toContainText("photos need a closer look");
		await expect(modal).not.toContainText("Keep browsing");

		await page.waitForTimeout(4300);
		await expect(page).toHaveURL(`${BASE_URL}/contact#received`);
	});

	test("empty photo state never shows an attachment warning", async ({ page }) => {
		await page.route("**/api/method/locally_twisted.www.book.submit_book_inquiry", async (route) => {
			await route.fulfill({
				status: 200,
				contentType: "application/json",
				body: JSON.stringify({
					message: {
						ok: true,
						lead: "LEAD-FORM-UX-NO-PHOTO",
						photo_uploads: {
							submitted: 0,
							attached: 0,
							rejected: [],
							failed: [],
							customer_message: "We received your request. The inspiration photo file(s) had a little trouble attaching, so we made a note for the team to follow up.",
						},
					},
				}),
			});
		});

		await page.goto(`${BASE_URL}/balloon-twisting-and-face-painting`);
		await dismissCookieNotice(page);
		await fillRequiredFields(page);

		await page.locator("#book_submit").click();

		const modal = page.locator("#received");
		await expect(modal).toBeVisible();
		await expect(modal).toContainText("Request received");
		await expect(modal).not.toContainText("inspiration photo file");
		await expect(modal).not.toContainText("trouble attaching");
	});
});
