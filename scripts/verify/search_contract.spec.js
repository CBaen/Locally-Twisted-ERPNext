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
		await expect(panel.locator("[data-lt-search-empty]")).toBeHidden();
	});

	test("header search overlay exposes the About Us company page", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 768 });
		const response = await gotoAndSettle(page, "/");
		expect(response, "home should return a response").not.toBeNull();
		expect(response.status(), "home should load").toBeLessThan(400);

		await page.locator(".lt-mega-header__search").click();
		await page.locator("#lt-site-search-input").fill("about");

		const panel = page.locator("#lt-site-search-panel");
		await expect(panel).toBeVisible();
		await expect(panel.locator("a[href='/about']")).toBeVisible();
		await expect(panel.locator("a[href='/about'] strong")).toHaveText("About Us");
		await expect(panel.locator("[data-lt-search-empty]")).toBeHidden();
	});

	test("header search overlay follows backend-approved product quick-link rules", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 768 });
		const response = await gotoAndSettle(page, "/");
		expect(response, "home should return a response").not.toBeNull();
		expect(response.status(), "home should load").toBeLessThan(400);

		await page.locator(".lt-mega-header__search").click();
		const formAction = await page.locator("#lt-site-search-panel form").getAttribute("action");
		await page.locator("#lt-site-search-input").fill("balloon cups");

		const panel = page.locator("#lt-site-search-panel");
		await expect(panel).toBeVisible();
		if (formAction === "/shop") {
			await expect(panel.locator("a[href='/shop-items/seasonal-specialty/easter-balloon-cups']")).toBeVisible();
			await expect(panel.locator("a[href='/shop-items/columns/7-butterfly-column']")).toBeHidden();
			await expect(panel.locator("a[href='/shop-items/arches/classic-arch']")).toHaveCount(0);
			await expect(panel.locator("a[href='/shop-items/columns/classic-column']")).toHaveCount(0);
			await expect(panel.locator("[data-lt-search-empty]")).toBeHidden();
		} else {
			await expect(panel.locator("[data-lt-search-product-entry]")).toHaveCount(0);
			await expect(panel.locator("a[href*='easter-balloon-cups']")).toHaveCount(0);
			await expect(panel.locator("[data-lt-search-empty]")).toBeVisible();
		}
	});

	test("submitted search query lands on the active commerce/search lane", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 768 });
		const response = await gotoAndSettle(page, "/");
		expect(response, "home should return a response").not.toBeNull();
		expect(response.status(), "home should load").toBeLessThan(400);

		await page.locator(".lt-mega-header__search").click();
		const formAction = await page.locator("#lt-site-search-panel form").getAttribute("action");
		await page.locator("#lt-site-search-input").fill("balloons");
		await Promise.all([page.waitForURL(new RegExp(`${formAction}\\?q=balloons$`)), page.keyboard.press("Enter")]);
		if (formAction === "/shop") {
			await expect(page.locator(".lt-shop--landing")).toBeVisible();
		} else {
			await expect(page.locator(".lt-contact__intro h1")).toBeVisible();
		}
	});
});
