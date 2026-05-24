const { test, expect } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const ASSET_PREFIX = "/assets/locally_twisted/images/heroes/";
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const MANIFEST_PATH = path.join(
	REPO_ROOT,
	"_resources",
	"generated-hero-sources",
	"2026-05-22",
	"shop-category-generated-hero-manifest.json",
);

const VIEWPORTS = [
	{ name: "mobile", width: 390, height: 844, key: "mobile", expectedHeroHeight: 220 },
	{ name: "tablet", width: 820, height: 1180, key: "tablet", expectedHeroHeight: 250 },
	{ name: "desktop", width: 1366, height: 768, key: "desktop", expectedHeroHeight: 280 },
];

const CATEGORY_HEROES = [
	{ route: "/shop-items/arches", title: "Arches", file: "classic-arch-category-hero" },
	{ route: "/shop-items/columns", title: "Columns", file: "classic-column-category-hero" },
	{ route: "/shop-items/bouquets", title: "Bouquets", file: "mothers-day-bouquet-category-hero" },
	{
		route: "/shop-items/get-well-bouquets",
		title: "Get-Well Bouquets",
		file: "bandage-get-well-bouquet-latex-free-category-hero",
	},
	{ route: "/shop-items/garlands", title: "Garlands", file: "classic-organic-balloon-garland-category-hero" },
	{ route: "/shop-items/drops", title: "Drops", file: "balloon-drop-category-hero" },
	{ route: "/shop-items/grab-go", title: "Grab & Go", file: "graduation-grab-n-go-category-hero" },
	{ route: "/shop-items/table-decor", title: "Table Decor", file: "marble-table-decor-category-hero" },
	{ route: "/shop-items/stands-easels", title: "Stands & Easels", file: "6-graduation-stands-category-hero" },
	{ route: "/shop-items/deliveries", title: "Deliveries", file: "birthday-deliveries-category-hero" },
	{ route: "/shop-items/seasonal-specialty", title: "Seasonal & Specialty", file: "easter-balloon-cups-category-hero" },
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

test("shop category hero generation manifest preserves color-source authority", () => {
	const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf8"));
	expect(manifest.items).toHaveLength(CATEGORY_HEROES.length);
	expect(manifest.note).toContain("Owner/Odoo swatches");
	expect(manifest.note).toContain("sampled hex values are not");

	for (const category of CATEGORY_HEROES) {
		const item = manifest.items.find((entry) => entry.route === category.route);
		expect(item, `${category.route} should have a generated hero manifest entry`).toBeTruthy();
		expect(item.slug).toBe(category.file);
		expect(item.palette.length).toBeGreaterThan(0);
		expect(item.swatch_refs.length).toBe(item.palette.length);
		expect(item.prompt).toContain("owner/Odoo balloon color names");
		expect(item.prompt).toContain("not hex values");
		for (const swatchRef of item.swatch_refs) {
			expect(swatchRef).toMatch(/^\/assets\/locally_twisted\/images\/color-swatches\/odoo\//);
		}
		for (const derivative of item.derivatives) {
			expect(derivative.path).toBe(`${category.file}-${derivative.key}.webp`);
		}
	}
});
