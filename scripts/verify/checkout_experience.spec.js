const { test, expect } = require("@playwright/test");
const { gotoAndSettle } = require("./layout_helpers");

const CART_KEY = "lt_cart";
const RETAIL_ITEM = "mothers-day-bouquet";

async function seedRetailCart(page) {
	await page.evaluate(
		({ key, itemCode }) => {
			window.localStorage.setItem(
				key,
				JSON.stringify({
					v: 3,
					items: [{ item_code: itemCode, qty: 1, line_key: itemCode + "::" }],
					updated_at: new Date().toISOString(),
				}),
			);
		},
		{ key: CART_KEY, itemCode: RETAIL_ITEM },
	);
}

test.describe("Locally Twisted checkout experience", () => {
	test.setTimeout(90000);

	test("public checkout follows the configured commerce lane", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await gotoAndSettle(page, "/");
		await seedRetailCart(page);
		await gotoAndSettle(page, "/checkout");

		if (page.url().includes("/ready-to-order-paused")) {
			await expect(page).toHaveURL(/\/ready-to-order-paused\?from=%2Fcheckout/);
			await expect(page.locator("body")).toContainText("Ready-to-order is paused");
			await expect(page.locator("body")).toContainText("Start a custom event quote");
			await expect(page.locator("#lt-checkout-form")).toHaveCount(0);
		} else {
			await expect(page).toHaveURL(/\/checkout$/);
			await expect(page.locator("body")).not.toContainText("Ready-to-order is paused");
			await expect(page.locator("#lt-checkout-form")).toBeVisible();
		}
	});

	test("public cart follows the configured commerce lane", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await gotoAndSettle(page, "/");
		await seedRetailCart(page);
		await gotoAndSettle(page, "/cart");

		if (page.url().includes("/ready-to-order-paused")) {
			await expect(page).toHaveURL(/\/ready-to-order-paused\?from=%2Fcart/);
			await expect(page.locator("body")).toContainText("Ready-to-order is paused");
			await expect(page.locator("#lt-cart-checkout-btn")).toHaveCount(0);
			await expect(page.locator("[data-item-code]")).toHaveCount(0);
		} else {
			await expect(page).toHaveURL(/\/cart$/);
			await expect(page.locator("body")).not.toContainText("Ready-to-order is paused");
			await expect(page.locator("#lt-cart-checkout-btn")).toBeVisible();
			await expect(page.locator("[data-item-code]").first()).toBeVisible();
		}
	});
});
