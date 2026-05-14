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
	await page.locator("#book_phone").fill("801-555-0101");
	await page.locator("#book_email").fill("form-ux-test@example.com");
	await page.locator("#book_preferred_contact_method").selectOption("Email");
	await page.locator("#book_occasion").selectOption("corporate");
	await page.locator("#book_date").fill("2026-06-20");
	await page.locator("#book_location").fill("Ogden, UT");
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
		await expect(form.locator("#book_name")).toHaveAttribute("autocomplete", "name");
		await expect(form.locator("#book_email")).toHaveAttribute("autocomplete", "email");
		await expect(form.locator("#book_phone")).toHaveAttribute("autocomplete", "tel");
		await expect(form.locator("#book_email_helper")).toContainText("Please double-check your email so we can respond to your inquiry.");
		await expect(form.locator("#book_phone_helper")).toContainText("We ask for a phone number so we have a second way to contact you about your inquiry.");
		await expect(form.locator("#book_phone")).toHaveAttribute("required", "");
		await expect(form.locator("#book_preferred_contact_method")).toHaveAttribute("required", "");
		await expect(form.locator("#book_occasion")).toHaveAttribute("required", "");
		await expect(form.locator("#book_date")).toHaveAttribute("required", "");
		await expect(form.locator("#book_location")).toHaveAttribute("required", "");
		await expect(form.locator("#book_preferred_contact_method option")).toHaveText([
			"Select one...",
			"Email",
			"Text",
			"Phone",
		]);
		await expect(form.locator("#book_occasion option").first()).toHaveText("Select an event type");
	});

	test("direct #received visits do not show fake success", async ({ page }) => {
		await page.goto(`${BASE_URL}/contact#received`);
		await dismissCookieNotice(page);

		await expect(page.locator("#received")).toBeHidden();
		await expect(page.locator("[data-lt-form-status]")).toBeHidden();
	});

	test("required contact basics fail before the request is sent", async ({ page }) => {
		let requests = 0;
		await page.route("**/api/method/locally_twisted.www.book.submit_book_inquiry", async (route) => {
			requests += 1;
			await route.fulfill({ status: 500, body: "" });
		});

		await page.goto(`${BASE_URL}/contact`);
		await dismissCookieNotice(page);
		await page.locator("#book_name").fill("Form UX Test");
		await page.locator("#book_email").fill("form-ux-test@gamil.com");
		await page.locator("#book_email").blur();
		await expect(page.locator("#book_email_hint")).toContainText("form-ux-test@gmail.com");

		await page.locator("#book_submit").click();
		await expect(page.locator("#book_feedback")).toContainText("Please enter a phone number so we have a second way to contact you about your inquiry.");
		expect(requests).toBe(0);

		await page.locator("#book_phone").fill("801-555-0101");
		await page.locator("#book_submit").click();
		await expect(page.locator("#book_feedback")).toContainText("Please choose how you prefer to be contacted.");
		expect(requests).toBe(0);

		await page.locator("#book_preferred_contact_method").selectOption("Email");
		await page.locator("#book_submit").click();
		await expect(page.locator("#book_feedback")).toContainText("Please choose an event type.");
		expect(requests).toBe(0);

		await page.locator("#book_occasion").selectOption("corporate");
		await page.locator("#book_submit").click();
		await expect(page.locator("#book_feedback")).toContainText("Please choose the event date.");
		expect(requests).toBe(0);

		await page.locator("#book_date").fill("2026-06-20");
		await page.locator("#book_submit").click();
		await expect(page.locator("#book_feedback")).toContainText("Please tell us the city or location for the event.");
		expect(requests).toBe(0);
	});

	test("invalid email fails loudly before the request is sent", async ({ page }) => {
		let requests = 0;
		await page.route("**/api/method/locally_twisted.www.book.submit_book_inquiry", async (route) => {
			requests += 1;
			await route.fulfill({ status: 500, body: "" });
		});

		await page.goto(`${BASE_URL}/contact`);
		await dismissCookieNotice(page);
		await page.locator("#book_name").fill("Form UX Test");
		await page.locator("#book_phone").fill("801-555-0101");
		await page.locator("#book_email").fill("not-an-email");
		await page.locator("#book_preferred_contact_method").selectOption("Email");

		await page.locator("#book_submit").click();
		await expect(page.locator("#book_feedback")).toContainText("Please enter a valid email address.");
		expect(requests).toBe(0);
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
