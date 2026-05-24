const { test, expect } = require("@playwright/test");
const { gotoAndSettle } = require("./layout_helpers");

const CART_KEY = "lt_cart";
const RETAIL_ITEM = "mothers-day-bouquet";
const ENCANTO_URL = "/shop-items/bouquets/encanto-bouquet";

function nextIsoDateForJsDay(jsDay) {
	const date = new Date();
	date.setHours(12, 0, 0, 0);
	while (date.getDay() !== jsDay) {
		date.setDate(date.getDate() + 1);
	}
	return date.toISOString().slice(0, 10);
}

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

	test("configured bouquet cart and checkout show cart state, product links, and pickup hours", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 900 });
		await gotoAndSettle(page, ENCANTO_URL);

		if (page.url().includes("/ready-to-order-paused")) {
			await expect(page.locator("body")).toContainText("Ready-to-order is paused");
			return;
		}

		const addButton = page.locator("#lt-add-to-cart-variant");
		await page.getByRole("radio", { name: "Small" }).evaluate((input) => {
			input.checked = true;
			input.dispatchEvent(new Event("change", { bubbles: true }));
		});
		await expect(addButton).toBeEnabled();
		await addButton.click();
		await expect(page.locator(".lt-cart-count.is-populated").first()).toHaveText("1");

		await gotoAndSettle(page, "/checkout");
		if (page.url().includes("/ready-to-order-paused")) {
			await expect(page.locator("body")).toContainText("Ready-to-order is paused");
			return;
		}

		await expect(page.locator(".lt-checkout__line-name a[href='/shop-items/bouquets/encanto-bouquet']")).toBeVisible();
		await expect(page.locator("label[for='co-phone']")).toContainText("Used only for order updates");
		await expect(page.locator("label[for='co-email']")).toContainText("Used only for order updates");
		await expect(page.locator("#co-preferred-contact")).toBeVisible();

		await page.locator("input[name='fulfillment_method'][value='pickup']").check();
		await page.locator("#co-pickup-location").selectOption("West Jordan");
		await page.locator("#co-date").fill(nextIsoDateForJsDay(2));
		await expect(page.locator("#co-window-start option", { hasText: "12:00 PM - 12:30 PM" })).toHaveCount(1);
		await expect(page.locator("#co-window-start option", { hasText: "12:00 - 12:30" })).toHaveCount(0);
		await page.locator("#co-window-start").selectOption("12:00");
		await expect.poll(async () => page.locator("#lt-checkout-summary-tax").textContent()).not.toContain("Calculated");
		await expect(page.locator("#co-feedback")).not.toContainText("Tiny snag");
	});
});
