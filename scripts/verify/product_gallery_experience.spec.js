const { test, expect } = require("@playwright/test");
const childProcess = require("child_process");
const crypto = require("crypto");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const CLASSIC_ARCH_URL = new URL("/shop-items/arches/classic-arch", BASE_URL).toString();
const SINGLE_EXTRA_GALLERY_URL = new URL("/shop-items/stands-easels/6-graduation-stands", BASE_URL).toString();
const BABY_SHOWER_GARLAND_URL = new URL("/shop-items/garlands/baby-shower-garland", BASE_URL).toString();
const ENCANTO_BOUQUET_URL = new URL("/shop-items/bouquets/encanto-bouquet", BASE_URL).toString();
const UNICORN_BOUQUET_URL = new URL("/shop-items/bouquets/unicorn-bouquet", BASE_URL).toString();

function imagePath(src) {
	return new URL(src || "", BASE_URL).pathname;
}

async function thumbnailPaths(page) {
	return page.locator(".lt-product__thumbnail-button img").evaluateAll((imgs) =>
		imgs.map((img) => new URL(img.getAttribute("src") || "", window.location.href).pathname).filter(Boolean),
	);
}

async function sha256ForPath(request, path) {
	const response = await request.get(new URL(path, BASE_URL).toString());
	expect(response.ok(), `${path} should be fetchable for image duplicate proof`).toBeTruthy();
	const body = await response.body();
	return crypto.createHash("sha256").update(body).digest("hex");
}

function localWebsiteItems() {
	const stdout = childProcess.execFileSync(
		"docker",
		[
			"exec",
			"locally-twisted-erpnext-v15-backend-1",
			"bench",
			"--site",
			"frontend",
			"execute",
			"frappe.get_all",
			"--args",
			JSON.stringify(["Website Item"]),
			"--kwargs",
			JSON.stringify({
				fields: ["item_code", "route", "published"],
				filters: { published: 1 },
				order_by: "item_code asc",
				limit_page_length: 0,
			}),
		],
		{ encoding: "utf8", maxBuffer: 20 * 1024 * 1024 },
	);
	return JSON.parse(stdout.trim() || "[]").filter((row) =>
		String(row.route || "").replace(/^\/+/, "").startsWith("shop-items/"),
	);
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
	await page.goto(SINGLE_EXTRA_GALLERY_URL, { waitUntil: "domcontentloaded" });
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

test("configured bouquet variant images do not mutate the Product Setup gallery rail", async ({ page }) => {
	const products = [
		{
			url: UNICORN_BOUQUET_URL,
			variantPaths: {
				Large: "/files/unicorn-bouquet-large.webp",
				Medium: "/files/unicorn-bouquet-medium.webp",
				Small: "/files/unicorn-bouquet-small.webp",
			},
		},
		{
			url: ENCANTO_BOUQUET_URL,
			variantPaths: {
				Large: "/files/encanto-bouquet-large.webp",
				Medium: "/files/encanto-bouquet-medium.webp",
				Small: "/files/encanto-bouquet-small.webp",
			},
		},
	];

	for (const product of products) {
		await page.setViewportSize({ width: 1366, height: 900 });
		await page.goto(product.url, { waitUntil: "domcontentloaded" });
		await page.waitForSelector(".product-image img.website-image");

		const initialPaths = await thumbnailPaths(page);
		const basePath = imagePath(await page.locator(".product-image img.website-image").getAttribute("src"));
		expect(initialPaths.length, `${product.url} should render the Product Setup gallery rail`).toBeGreaterThan(1);
		expect(new Set(initialPaths).size, `${product.url} thumbnails must not duplicate image URLs on load`).toBe(
			initialPaths.length,
		);
		expect(initialPaths[0], `${product.url} should keep the main photo as the first thumbnail`).toBe(basePath);

		for (const [sizeName, expectedPath] of Object.entries(product.variantPaths)) {
			await page.getByRole("radio", { name: sizeName }).first().evaluate((input) => {
				input.checked = true;
				input.dispatchEvent(new Event("change", { bubbles: true }));
			});
			await expect.poll(async () => imagePath(await page.locator(".product-image img.website-image").getAttribute("src")), {
				message: `${product.url} should show the ${sizeName} option-specific image`,
			}).toBe(expectedPath);
			await expect.poll(() => thumbnailPaths(page), {
				message: `${product.url} thumbnail rail should stay tied to Product Setup gallery rows after ${sizeName}`,
			}).toEqual(initialPaths);
		}

		await page.locator(".lt-product__thumbnail-button").first().click();
		await expect.poll(async () => imagePath(await page.locator(".product-image img.website-image").getAttribute("src"))).toBe(
			basePath,
		);
		await expect.poll(() => thumbnailPaths(page), {
			message: `${product.url} thumbnail rail should stay stable after returning to the main photo`,
		}).toEqual(initialPaths);
	}
});

test("product gallery rail does not repeat the same uploaded image content", async ({ page, request }) => {
	await page.setViewportSize({ width: 1366, height: 900 });
	await page.goto(BABY_SHOWER_GARLAND_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".product-image img.website-image");

	const mainPath = imagePath(await page.locator(".product-image img.website-image").getAttribute("src"));
	const visiblePaths = [mainPath, ...(await thumbnailPaths(page))];
	const uniquePaths = [...new Set(visiblePaths)];
	const hashes = [];
	for (const path of uniquePaths) {
		hashes.push(await sha256ForPath(request, path));
	}
	expect(new Set(hashes).size, "gallery should not show the same uploaded image under different URLs").toBe(
		hashes.length,
	);
});

test("all product pages follow the distinct-photo gallery architecture", async ({ page, request }) => {
	const products = localWebsiteItems();
	expect(products.length, "published product pages should be available for gallery architecture proof").toBeGreaterThan(0);

	for (const product of products) {
		const route = String(product.route || "").replace(/^\/+/, "");
		await page.setViewportSize({ width: 1366, height: 900 });
		await page.goto(new URL(`/${route}`, BASE_URL).toString(), { waitUntil: "domcontentloaded" });
		await page.waitForSelector(".product-image img.website-image");

		const visiblePaths = await page.evaluate(() => {
			const main = document.querySelector(".product-image img.website-image")?.getAttribute("src") || "";
			const thumbs = [...document.querySelectorAll(".lt-product__thumbnail-button img")]
				.map((img) => img.getAttribute("src") || "")
				.filter(Boolean);
			return [...new Set([main, ...thumbs].filter(Boolean).map((src) => new URL(src, window.location.href).pathname))];
		});
		const thumbPaths = await thumbnailPaths(page);
		const uniqueContentHashes = new Set();
		const hashToPaths = new Map();
		for (const path of visiblePaths) {
			const hash = await sha256ForPath(request, path);
			uniqueContentHashes.add(hash);
			hashToPaths.set(hash, [...(hashToPaths.get(hash) || []), path]);
		}

		for (const paths of hashToPaths.values()) {
			expect(paths.length, `${product.item_code} should not render the same photo content under multiple URLs`).toBe(1);
		}
		if (uniqueContentHashes.size < 2) {
			expect(thumbPaths.length, `${product.item_code} should not show a rail for one distinct product photo`).toBe(0);
		} else {
			expect(
				thumbPaths.length,
				`${product.item_code} should show one thumbnail per distinct product photo`,
			).toBe(uniqueContentHashes.size);
		}
	}
});

test("product image zoom closes from the backdrop or close button", async ({ page }) => {
	await page.setViewportSize({ width: 1366, height: 900 });
	await page.goto(UNICORN_BOUQUET_URL, { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".product-image img.website-image");

	const zoom = page.locator(".image-zoom-view");
	await page.locator(".product-image img.website-image").click();
	await expect(zoom).toBeVisible();
	await expect(zoom.locator("img")).toHaveCount(1);

	const box = await zoom.boundingBox();
	expect(box, "zoom overlay should have a visible backdrop").toBeTruthy();
	await page.mouse.click(box.x + 12, box.y + 12);
	await expect(zoom).toBeHidden();
	await expect(zoom.locator("img")).toHaveCount(0);

	await page.locator(".product-image img.website-image").click();
	await expect(zoom).toBeVisible();
	await zoom.locator("button[aria-label='Close']").click();
	await expect(zoom).toBeHidden();
	await expect(zoom.locator("img")).toHaveCount(0);
});
