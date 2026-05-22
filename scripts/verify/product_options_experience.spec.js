const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const UNICORN_URL = new URL("/shop-items/bouquets/unicorn-bouquet", BASE_URL).toString();
const CHECKOUT_BOUQUET_SLUGS = [
	"elsa-bouquet",
	"encanto-bouquet",
	"flamingo-bouquet",
	"football-bouquet",
	"holy-cow-bouquet",
	"mickey-mouse-bouquet",
	"minion-bouquet",
	"over-the-hill-bouquet",
	"paw-patrol-bouquet",
	"soccer-bouquet",
	"space-bouquet",
	"stitch-bouquet",
	"unicorn-bouquet",
];

test("bouquet size controls stay short and move contents into What's Included", async ({ page }) => {
	await page.goto(UNICORN_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".lt-product__configure");

	const sizeLabels = page.locator('.lt-product__attr[data-attribute-name="Bouquet Size"] .lt-product__chip-label');
	await expect(sizeLabels).toHaveText(["Small", "Medium", "Large"]);
	const visibleSizeLabels = await sizeLabels.allTextContents();
	expect(visibleSizeLabels.join(" ")).not.toContain("featured foil balloon");
	expect(visibleSizeLabels.join(" ")).not.toContain("latex balloons");

	await page.locator('.lt-product__chip', { hasText: "Small" }).click();
	await expect(page.locator(".js-lt-product-details")).toContainText(
		"Small includes 1 featured foil balloon, 2 coordinating foil balloons, 7 latex balloons",
	);

	await page.locator('.lt-product__chip', { hasText: "Large" }).click();
	await expect(page.locator(".js-lt-product-details")).toContainText(
		"Large includes 3 featured foil balloons, 5 coordinating foil balloons, 16 latex balloons",
	);
	await expect(
		page.locator('.lt-product__attr[data-attribute-name="Bouquet Size"] .lt-product__attr-selected'),
	).toHaveText("");
});

test("foil number add-on accepts up to three duplicate digits and updates visible price", async ({ page }) => {
	await page.goto(UNICORN_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".lt-product__configure");

	await expect(page.locator(".lt-product__addons-intro")).toContainText(
		"Add number foils to make it a birthday bouquet",
	);
	await page.locator('.lt-product__chip', { hasText: "Small" }).click();
	const price = page.locator("#lt-product-price-text");
	await expect(price).toContainText(/\$\s*35\.00/);

	await page.locator(".js-lt-addon-toggle").check();
	const input = page.locator(".js-lt-addon-value");
	await expect(input).toHaveAttribute("maxlength", "3");
	await input.fill("111");
	await expect(input).toHaveValue("111");
	await expect(price).toContainText(/\$\s*71\.00/);
	await expect(price).toContainText("including");

	await input.fill("1111");
	await expect(input).toHaveValue("111");
	await expect(price).toContainText(/\$\s*71\.00/);

	await input.fill("12a");
	await expect(input).toHaveValue("12");
	await expect(price).toContainText(/\$\s*59\.00/);
});

test("all checkout bouquet pages keep size labels clean and foil number input capped", async ({ page }) => {
	for (const slug of CHECKOUT_BOUQUET_SLUGS) {
		await page.goto(new URL(`/shop-items/bouquets/${slug}`, BASE_URL).toString(), { waitUntil: "domcontentloaded" });
		await page.waitForSelector(".lt-product__configure");

		const sizeLabels = page.locator('.lt-product__attr[data-attribute-name="Bouquet Size"] .lt-product__chip-label');
		await expect(sizeLabels, `${slug} size labels`).toHaveText(["Small", "Medium", "Large"]);
		const visibleSizeLabels = await sizeLabels.allTextContents();
		expect(visibleSizeLabels.join(" "), `${slug} should not put contents in size labels`).not.toMatch(
			/featured foil|coordinating foil|latex balloon|super shape/i,
		);

		await expect(page.locator(".js-lt-addon-value"), `${slug} foil input max length`).toHaveAttribute("maxlength", "3");
	}
});

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
