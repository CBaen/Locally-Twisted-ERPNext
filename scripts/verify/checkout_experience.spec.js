const { test, expect } = require("@playwright/test");
const { BASE_URL, gotoAndSettle } = require("./layout_helpers");

const CART_KEY = "lt_cart";
const RETAIL_ITEM = "mothers-day-bouquet";

function futureDate(days = 30) {
	const date = new Date();
	date.setDate(date.getDate() + days);
	return date.toISOString().slice(0, 10);
}

async function seedRetailCart(page) {
	await gotoAndSettle(page, "/shop");
	await page.evaluate(
		({ key, itemCode }) => {
			window.localStorage.setItem(
				key,
				JSON.stringify({
					v: 1,
					items: [{ item_code: itemCode, qty: 1 }],
					updated_at: new Date().toISOString(),
				}),
			);
		},
		{ key: CART_KEY, itemCode: RETAIL_ITEM },
	);
	await gotoAndSettle(page, "/checkout");
	await expect(page.locator("#lt-checkout-summary-lines .lt-checkout__line-name")).toContainText(
		"Mother",
	);
}

async function chooseRequestedWindow(page) {
	await page.fill("#co-date", futureDate());
	await page.selectOption("#co-window-start", "13:00");
}

async function fillRequiredCustomerFields(page) {
	await page.fill("#co-name", "Casey Delivery");
	await page.fill("#co-phone", "801-555-0144");
	await page.fill("#co-email", "casey@example.invalid");
	await page.fill("#co-addr1", "123 Red Rock Road");
	await page.fill("#co-notes", "Please call before delivery.");
}

test.describe("Locally Twisted checkout experience", () => {
	test.setTimeout(90000);

	test("delivery, out-of-area quote, and pickup previews stay in sync", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await seedRetailCart(page);
		await chooseRequestedWindow(page);

		await page.fill("#co-city", "West Jordan");
		await page.fill("#co-zip", "84088");
		await page.locator("#co-zip").blur();
		await expect(page.locator("#lt-checkout-summary-delivery")).toHaveText("$15.00");
		await expect(page.locator("#co-submit")).toHaveText("Continue to payment");

		await page.fill("#co-city", "St George");
		await page.fill("#co-zip", "84770");
		await page.locator("#co-zip").blur();
		await expect(page.locator("#lt-checkout-summary-delivery")).toHaveText("Quote needed");
		await expect(page.locator("#lt-checkout-summary-tax")).toHaveText("Reviewed with quote");
		await expect(page.locator("#co-submit")).toHaveText("Request delivery quote");

		// A stale prior preview response must not flip the UI back to paid checkout.
		await page.waitForTimeout(750);
		await expect(page.locator("#lt-checkout-summary-delivery")).toHaveText("Quote needed");
		await expect(page.locator("#co-submit")).toHaveText("Request delivery quote");

		await page.check('input[name="fulfillment_method"][value="pickup"]');
		await page.selectOption("#co-pickup-location", "Riverdale");
		await expect(page.locator("#lt-checkout-summary-delivery")).toHaveText("$0.00");
		await expect(page.locator("#lt-checkout-summary-tax")).toHaveText(/\$\d+\.\d{2}/);
		await expect(page.locator("#co-submit")).toHaveText("Continue to payment");
	});

	test("out-of-area delivery quote request redirects to prefilled contact form", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await seedRetailCart(page);
		await fillRequiredCustomerFields(page);
		await chooseRequestedWindow(page);

		await page.fill("#co-city", "St George");
		await page.fill("#co-zip", "84770");
		await page.locator("#co-zip").blur();
		await expect(page.locator("#co-submit")).toHaveText("Request delivery quote");

		await page.click("#co-submit");
		await page.waitForURL(/\/contact\?intent=quote&source=checkout-delivery/, { timeout: 15000 });
		await expect(page.locator("#book_name")).toHaveValue("Casey Delivery");
		await expect(page.locator("#book_phone")).toHaveValue("801-555-0144");
		await expect(page.locator("#book_email")).toHaveValue("casey@example.invalid");
		await expect(page.locator("#book_location")).toHaveValue(/123 Red Rock Road/);
		await expect(page.locator("#book_location")).toHaveValue(/84770/);
		await expect(page.locator("#book_notes")).toHaveValue(/Interested item: Mother's Day Bouquet/);
		await expect(page.locator("#book_notes")).toHaveValue(/Please call before delivery/);
		await expect(page.locator('input[name="x_services"][value="Delivery"]')).toBeChecked();
		await expect(page.locator("#book_delivery_notes")).toHaveValue(/out of standard delivery area/i);
	});
});
