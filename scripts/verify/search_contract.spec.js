const { test, expect } = require("@playwright/test");
const { gotoAndSettle } = require("./layout_helpers");

test.describe("Locally Twisted search contract", () => {
	test("header search overlay finds public launch pages", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 768 });
		const response = await gotoAndSettle(page, "/");
		expect(response, "home should return a response").not.toBeNull();
		expect(response.status(), "home should load").toBeLessThan(400);

		await page.locator(".lt-mega-header__search").click();
		await page.locator("#lt-site-search-input").fill("portfolio");

		const panel = page.locator("#lt-site-search-panel");
		await expect(panel).toBeVisible();
		await expect(panel.locator("a[href='/portfolio']")).toBeVisible();
		await expect(panel.locator("a[href^='/shop']")).toHaveCount(0);
		await expect(panel.locator("[data-lt-search-empty]")).toBeHidden();
	});

	test("submitted search query lands on contact fallback while ecommerce is paused", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 768 });
		const response = await gotoAndSettle(page, "/");
		expect(response, "home should return a response").not.toBeNull();
		expect(response.status(), "home should load").toBeLessThan(400);

		await page.locator(".lt-mega-header__search").click();
		await page.locator("#lt-site-search-input").fill("balloons");
		await Promise.all([
			page.waitForURL(/\/contact\?q=balloons$/),
			page.keyboard.press("Enter"),
		]);
		await expect(page.locator(".lt-contact__intro h1")).toBeVisible();
	});
});
