const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const CLASSIC_ARCH_URL = new URL("/shop-items/arches/classic-arch", BASE_URL).toString();
const LARGE_GARLAND_URL = new URL("/shop-items/garlands/large-garland", BASE_URL).toString();
const MICKEY_BOUQUET_URL = new URL("/shop-items/bouquets/mickey-mouse-bouquet", BASE_URL).toString();

async function normalizedMainImagePath(page) {
	return page.locator(".product-image img.website-image").evaluate((img) => new URL(img.getAttribute("src"), location.href).pathname);
}

async function normalizedThumbnailPaths(page) {
	return page.locator(".lt-product__thumbnail-button img").evaluateAll((imgs) =>
		imgs.map((img) => new URL(img.getAttribute("src"), location.href).pathname),
	);
}

test("Classic Arch renders permanent product gallery thumbnails on desktop", async ({ page }) => {
	await page.setViewportSize({ width: 1366, height: 900 });
	await page.goto(CLASSIC_ARCH_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".product-image img.website-image");

	const shell = page.locator(".lt-product__media-shell.has-thumbnails");
	await expect(shell).toBeVisible();
	await expect(page.getByText("Other product photos", { exact: true })).toHaveCount(0);

	const rail = page.locator('[data-lt-gallery-role="standard-product-thumbnails"]');
	const mainImage = page.locator(".product-image");
	await expect(rail).toBeVisible();
	await expect(mainImage).toBeVisible();

	const thumbs = page.locator(".lt-product__thumbnail-button");
	const thumbCount = await thumbs.count();
	expect(thumbCount, "Classic Arch should render more than two gallery thumbnails").toBeGreaterThan(2);

	const sources = await page.locator(".lt-product__thumbnail-button img").evaluateAll((imgs) =>
		imgs.map((img) => img.getAttribute("src")).filter(Boolean),
	);
	expect(new Set(sources).size, "gallery thumbnails should not duplicate source images").toBe(sources.length);

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

	const firstSrc = await page.locator(".product-image img.website-image").getAttribute("src");
	await thumbs.nth(1).click();
	await expect(page.locator(".lt-product__thumbnail-button[aria-pressed='true']")).toHaveCount(1);
	await expect.poll(async () => page.locator(".product-image img.website-image").getAttribute("src")).not.toBe(firstSrc);
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

test("Mickey Mouse Bouquet gallery exposes the full selectable product-photo set", async ({ page }) => {
	await page.setViewportSize({ width: 1366, height: 900 });
	await page.goto(MICKEY_BOUQUET_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".product-image img.website-image");

	const thumbs = page.locator(".lt-product__thumbnail-button");
	const paths = await normalizedThumbnailPaths(page);
	expect(paths, "Mickey should show the primary image plus the two distinct approved product photos").toHaveLength(3);
	expect(paths[0], "the initial main product photo must also be the first thumbnail").toBe(
		"/files/mickey-mouse-bouquet.png",
	);
	expect(paths, "large bouquet photo should be available without selecting a size first").toContain(
		"/files/mickey-mouse-bouquet-large.webp",
	);

	const firstMain = await normalizedMainImagePath(page);
	await thumbs.nth(2).click();
	await expect.poll(async () => normalizedMainImagePath(page)).not.toBe(firstMain);
	await thumbs.nth(0).click();
	await expect.poll(async () => normalizedMainImagePath(page)).toBe(firstMain);
	await expect(page.locator(".lt-product__thumbnail-button[aria-pressed='true']")).toHaveCount(1);
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
