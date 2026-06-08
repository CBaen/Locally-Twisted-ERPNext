const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const ASSET_PREFIX = "/assets/locally_twisted/images/heroes/";

const VIEWPORTS = [
	{ name: "mobile", width: 390, height: 844, key: "mobile", expectedHeroHeight: 220 },
	{ name: "tablet", width: 820, height: 1180, key: "tablet", expectedHeroHeight: 250 },
	{ name: "desktop", width: 1366, height: 768, key: "desktop", expectedHeroHeight: 280 },
];

const CATEGORY_HEROES = [
	{ route: "/shop-items/arches", title: "Arches", file: "arches-category-generated-hero" },
	{ route: "/shop-items/balloon-drops", title: "Balloon Drops", file: "balloon-drops-category-generated-hero" },
	{ route: "/shop-items/bouquets", title: "Bouquets", file: "bouquets-category-generated-hero" },
	{ route: "/shop-items/columns", title: "Columns", file: "columns-category-generated-hero" },
	{ route: "/shop-items/garlands", title: "Garlands", file: "garlands-category-generated-hero" },
	{
		route: "/shop-items/photo-ops-backdrops",
		title: "Photo Ops & Backdrops",
		file: "photo-ops-backdrops-category-generated-hero",
	},
	{ route: "/shop-items/stands-easels", title: "Stands & Easels", file: "stands-easels-category-generated-hero" },
	{ route: "/shop-items/table-decor", title: "Table Decor", file: "table-decor-category-generated-hero" },
];

for (const viewport of VIEWPORTS) {
	test.describe(`shop category hero imagery at ${viewport.name}`, () => {
		for (const category of CATEGORY_HEROES) {
			test(`${category.title} uses its own representative hero`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const assetPath = `${ASSET_PREFIX}${category.file}-${viewport.key}.webp`;
				const assetResponse = await page.request.get(new URL(assetPath, BASE_URL).toString());
				expect(assetResponse.status(), `${assetPath} should be web-served`).toBe(200);

				await page.goto(new URL(category.route, BASE_URL).toString(), { waitUntil: "domcontentloaded" });
				await page.waitForSelector(".lt-shop__hero");

				const result = await page.evaluate(() => {
					const hero = document.querySelector(".lt-shop__hero");
					const title = document.querySelector(".lt-shop__title");
					const before = hero ? window.getComputedStyle(hero, "::before") : null;
					const after = hero ? window.getComputedStyle(hero, "::after") : null;
					return {
						title: title ? title.textContent.trim() : "",
						beforeImage: before ? before.backgroundImage : "",
						overlay: after ? after.backgroundImage : "",
						height: hero ? Math.round(hero.getBoundingClientRect().height) : 0,
					};
				});

				expect(result.title).toBe(category.title);
				expect(result.beforeImage).toContain(`${category.file}-${viewport.key}.webp`);
				expect(result.beforeImage).not.toContain(`shop-generated-lifestyle-${viewport.key}.webp`);
				expect(result.overlay).toContain("rgba(10, 10, 11");
				expect(result.height).toBe(viewport.expectedHeroHeight);
			});
		}
	});
}

test("shop category hero assignments are unique across category routes", () => {
	expect(new Set(CATEGORY_HEROES.map((category) => category.file)).size).toBe(CATEGORY_HEROES.length);
});
