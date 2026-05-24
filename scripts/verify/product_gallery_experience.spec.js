const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const CLASSIC_ARCH_URL = new URL("/shop-items/arches/classic-arch", BASE_URL).toString();
const LARGE_GARLAND_URL = new URL("/shop-items/garlands/large-garland", BASE_URL).toString();
const ENCANTO_BOUQUET_URL = new URL("/shop-items/bouquets/encanto-bouquet", BASE_URL).toString();

function imagePath(src) {
	return new URL(src || "", BASE_URL).pathname;
}

test("Classic Arch renders permanent product gallery thumbnails on desktop", async ({ page }) => {
	await page.setViewportSize({ width: 1366, height: 900 });
	await page.goto(CLASSIC_ARCH_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".product-image img.website-image");

	const shell = page.locator(".lt-product__media-shell.has-thumbnails");
	await expect(shell).toBeVisible();

	const rail = page.locator('[data-lt-gallery-role="standard-product-thumbnails"]');
	const mainImage = page.locator(".product-image");
	await expect(rail).toBeVisible();
	await expect(mainImage).toBeVisible();

	const thumbs = page.locator(".lt-product__thumbnail-button");
	const thumbCount = await thumbs.count();
	expect(thumbCount, "Classic Arch should render more than two gallery thumbnails").toBeGreaterThan(2);
	await expect(page.getByText("Other product photos")).toHaveCount(0);

	const firstSrc = await page.locator(".product-image img.website-image").getAttribute("src");
	const sources = await page.locator(".lt-product__thumbnail-button img").evaluateAll((imgs) =>
		imgs.map((img) => img.getAttribute("src")).filter(Boolean),
	);
	expect(new Set(sources).size, "gallery thumbnails should not duplicate source images").toBe(sources.length);
	const firstPath = imagePath(firstSrc);
	expect(imagePath(sources[0]), "the initial product photo should stay available as the first thumbnail").toBe(firstPath);

	const boxes = await page.evaluate(() => {
		const rail = document.querySelector('[data-lt-gallery-role="standard-product-thumbnails"]');
		const main = document.querySelector(".product-image");
		const railBox = rail?.getBoundingClientRect();
		const mainBox = main?.getBoundingClientRect();
		return {
			rail: railBox ? { x: railBox.x, y: railBox.y, width: railBox.width, height: railBox.height } : null,
			main: mainBox ? { x: mainBox.x, y: mainBox.y, width: mainBox.width, height: mainBox.height } : null,
			overflowY: rail ? getComputedStyle(rail).overflowY : "",
			scrollHeight: rail?.scrollHeight || 0,
			clientHeight: rail?.clientHeight || 0,
			documentOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
		};
	});
	expect(boxes.rail.x, "thumbnail rail should be left of the main image").toBeLessThan(boxes.main.x);
	expect(boxes.rail.height, "thumbnail rail cannot exceed main image height").toBeLessThanOrEqual(boxes.main.height + 2);
	expect(Math.abs(boxes.documentOverflow), "product gallery must not create horizontal overflow").toBeLessThanOrEqual(1);
	if (boxes.scrollHeight > boxes.clientHeight + 2) {
		expect(["auto", "scroll"].includes(boxes.overflowY), "overflow stays inside the thumbnail rail").toBeTruthy();
	}

	await thumbs.nth(1).click();
	await expect(page.locator(".lt-product__thumbnail-button[aria-pressed='true']")).toHaveCount(1);
	await expect.poll(async () => imagePath(await page.locator(".product-image img.website-image").getAttribute("src"))).not.toBe(firstPath);
	await thumbs.first().click();
	await expect.poll(async () => imagePath(await page.locator(".product-image img.website-image").getAttribute("src"))).toBe(firstPath);
});

test("single-extra projected galleries still render the permanent thumbnail rail", async ({ page }) => {
	await page.setViewportSize({ width: 1366, height: 900 });
	await page.goto(LARGE_GARLAND_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".product-image img.website-image");

	const rail = page.locator('[data-lt-gallery-role="standard-product-thumbnails"]');
	await expect(rail).toBeVisible();

	const thumbs = page.locator(".lt-product__thumbnail-button");
	const thumbCount = await thumbs.count();
	expect(thumbCount, "a projected one-extra-or-more Website Slideshow must render primary plus gallery thumbnails").toBeGreaterThan(1);

	const mainImage = page.locator(".product-image");
	const boxes = await page.evaluate(() => {
		const rail = document.querySelector('[data-lt-gallery-role="standard-product-thumbnails"]');
		const main = document.querySelector(".product-image");
		const railBox = rail?.getBoundingClientRect();
		const mainBox = main?.getBoundingClientRect();
		return {
			rail: railBox ? { x: railBox.x, height: railBox.height } : null,
			main: mainBox ? { x: mainBox.x, height: mainBox.height } : null,
			overflowY: rail ? getComputedStyle(rail).overflowY : "",
			scrollHeight: rail?.scrollHeight || 0,
			clientHeight: rail?.clientHeight || 0,
			documentOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
		};
	});
	await expect(mainImage).toBeVisible();
	expect(boxes.rail.x, "thumbnail rail should be left of the main image").toBeLessThan(boxes.main.x);
	expect(boxes.rail.height, "thumbnail rail cannot exceed main image height").toBeLessThanOrEqual(boxes.main.height + 2);
	expect(Math.abs(boxes.documentOverflow), "product gallery must not create horizontal overflow").toBeLessThanOrEqual(1);
	if (boxes.scrollHeight > boxes.clientHeight + 2) {
		expect(["auto", "scroll"].includes(boxes.overflowY), "overflow stays inside the thumbnail rail").toBeTruthy();
	}
});

test("product gallery survives variant selection and supports mobile swipe", async ({ page }) => {
	await page.setViewportSize({ width: 390, height: 844 });
	await page.goto(CLASSIC_ARCH_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".product-image img.website-image");

	const rail = page.locator('[data-lt-gallery-role="standard-product-thumbnails"]');
	await expect(rail).toBeVisible();
	const thumbCount = await page.locator(".lt-product__thumbnail-button").count();
	expect(thumbCount, "mobile gallery should retain thumbnails/indicators").toBeGreaterThan(2);

	const sizeChip = page.locator('.lt-product__chip').filter({ hasText: /20ft|25ft|30ft|35ft/i }).first();
	if ((await sizeChip.count()) > 0) {
		await sizeChip.click();
		await expect(rail, "variant selection should not remove the gallery rail").toBeVisible();
		await expect(page.locator(".lt-product__thumbnail-button")).toHaveCount(thumbCount);
	}

	const before = await page.locator(".product-image img.website-image").getAttribute("src");
	const box = await page.locator(".product-image").boundingBox();
	expect(box).toBeTruthy();
	await page.locator(".product-image").dispatchEvent("pointerdown", {
		clientX: box.x + box.width * 0.75,
		clientY: box.y + box.height * 0.5,
		pointerId: 1,
		pointerType: "touch",
	});
	await page.locator(".product-image").dispatchEvent("pointerup", {
		clientX: box.x + box.width * 0.25,
		clientY: box.y + box.height * 0.5,
		pointerId: 1,
		pointerType: "touch",
	});
	await expect.poll(async () => page.locator(".product-image img.website-image").getAttribute("src")).not.toBe(before);

	const mobileMetrics = await page.evaluate(() => {
		const rail = document.querySelector('[data-lt-gallery-role="standard-product-thumbnails"]');
		const main = document.querySelector(".product-image");
		const railBox = rail?.getBoundingClientRect();
		const mainBox = main?.getBoundingClientRect();
		return {
			rail: railBox ? { x: railBox.x, y: railBox.y, width: railBox.width, height: railBox.height } : null,
			main: mainBox ? { x: mainBox.x, y: mainBox.y, width: mainBox.width, height: mainBox.height } : null,
			overflowX: rail ? getComputedStyle(rail).overflowX : "",
			documentOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
		};
	});
	expect(mobileMetrics.rail.y, "mobile rail should sit below the main image").toBeGreaterThanOrEqual(
		mobileMetrics.main.y,
	);
	expect(["auto", "scroll"].includes(mobileMetrics.overflowX), "mobile gallery should scroll horizontally").toBeTruthy();
	expect(Math.abs(mobileMetrics.documentOverflow), "mobile gallery must not create horizontal overflow").toBeLessThanOrEqual(1);
});

test("configured bouquet keeps the base product photo available after selecting a size", async ({ page }) => {
	await page.setViewportSize({ width: 1366, height: 900 });
	await page.goto(ENCANTO_BOUQUET_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".product-image img.website-image");

	const basePath = imagePath(await page.locator(".product-image img.website-image").getAttribute("src"));
	await expect(page.locator(".lt-product__thumbnail-button").first().locator("img")).toHaveAttribute("src", /encanto-bouquet/);

	await page.getByRole("radio", { name: "Small" }).evaluate((input) => {
		input.checked = true;
		input.dispatchEvent(new Event("change", { bubbles: true }));
	});
	await expect(page.locator('[data-lt-gallery-role="standard-product-thumbnails"]')).toBeVisible();
	await expect
		.poll(async () => {
			const sources = await page.locator(".lt-product__thumbnail-button img").evaluateAll((imgs) =>
				imgs.map((img) => img.getAttribute("src")).filter(Boolean),
			);
			return sources.some((src) => imagePath(src) === basePath);
		})
		.toBeTruthy();

	await page.locator(".lt-product__thumbnail-button").first().click();
	await expect.poll(async () => imagePath(await page.locator(".product-image img.website-image").getAttribute("src"))).toBe(basePath);
});
