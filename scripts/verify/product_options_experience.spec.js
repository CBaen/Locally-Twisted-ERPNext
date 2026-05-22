const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";

test("checkout bouquet chip selections do not show a duplicate selected-size label", async ({ page }) => {
	const examples = [
		["elsa-bouquet", "Large"],
		["mickey-mouse-bouquet", "Medium"],
	];

	for (const [slug, size] of examples) {
		await page.goto(new URL(`/shop-items/bouquets/${slug}`, BASE_URL).toString(), { waitUntil: "domcontentloaded" });
		await page.waitForSelector(".lt-product__configure");

		const sizeGroup = page.locator('.lt-product__attr[data-attribute-name="Bouquet Size"]');
		await sizeGroup.locator(".lt-product__chip", { hasText: size }).click();

		const selectedSummary = sizeGroup.locator(".lt-product__attr-selected");
		await expect(selectedSummary, `${slug} should not leak selected ${size} text outside the chip`).toHaveText("");
		await expect(selectedSummary, `${slug} selected-size summary should stay hidden`).toBeHidden();
	}
});
