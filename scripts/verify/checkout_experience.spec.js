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

test.describe("Locally Twisted checkout experience", () => {
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
		await expect(page.locator("#co-submit")).toHaveText("Send delivery quote request");

		// A stale prior preview response must not flip the UI back to paid checkout.
		await page.waitForTimeout(750);
		await expect(page.locator("#lt-checkout-summary-delivery")).toHaveText("Quote needed");
		await expect(page.locator("#co-submit")).toHaveText("Send delivery quote request");

		await page.check('input[name="fulfillment_method"][value="pickup"]');
		await page.selectOption("#co-pickup-location", "Riverdale");
		await expect(page.locator("#lt-checkout-summary-delivery")).toHaveText("$0.00");
		await expect(page.locator("#lt-checkout-summary-tax")).toHaveText(/\$\d+\.\d{2}/);
		await expect(page.locator("#co-submit")).toHaveText("Continue to payment");
	});
});
