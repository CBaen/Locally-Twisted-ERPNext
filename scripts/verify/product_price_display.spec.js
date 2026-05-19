const { test, expect } = require("@playwright/test");

test("variant size selection updates the visible product price", async ({ page }) => {
	await page.goto("http://localhost:8081/shop-items/arches/easter-balloon-arch-bunny-ear", {
		waitUntil: "domcontentloaded",
	});
	await page.waitForSelector(".lt-product__configure");

	const price = page.locator("#lt-product-price-text");
	const addButton = page.locator("#lt-add-to-cart-variant");

	await page.locator(".lt-product__chip", { hasText: "20ft" }).click();
	await page.waitForFunction(
		() =>
			document
				.querySelector("#lt-add-to-cart-variant")
				?.getAttribute("data-item-code") === "easter-balloon-arch-bunny-ear-20F",
	);
	await expect(price).toContainText(/\$\s*375\.00/);
	await expect(addButton).toHaveAttribute("data-item-code", "easter-balloon-arch-bunny-ear-20F");

	await page.locator(".lt-product__chip", { hasText: "25ft" }).click();
	await page.waitForFunction(
		() =>
			document
				.querySelector("#lt-add-to-cart-variant")
				?.getAttribute("data-item-code") === "easter-balloon-arch-bunny-ear-25F",
	);
	await expect(price).toContainText(/\$\s*440\.00/);
	await expect(addButton).toHaveAttribute("data-item-code", "easter-balloon-arch-bunny-ear-25F");
});
