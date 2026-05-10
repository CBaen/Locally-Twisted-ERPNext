const { test, expect } = require("@playwright/test");
const { gotoAndSettle } = require("./layout_helpers");

const EVENT_BALLOONS_AUDIENCE_ROUTES = [
	{ name: "civic community", path: "/civic-community" },
	{ name: "corporate events", path: "/corporate-events" },
	{ name: "schools campuses", path: "/schools-campuses" },
	{ name: "private celebrations", path: "/private-celebrations" },
];

const PHONE_VIEWPORTS = [
	{ name: "small phone", width: 320, height: 812 },
	{ name: "standard phone", width: 390, height: 844 },
	{ name: "large phone", width: 414, height: 896 },
];

async function expectSuccessfulResponse(response, path) {
	expect(response, `${path} should return a response`).not.toBeNull();
	expect(response.status(), `${path} HTTP status`).toBeLessThan(400);
}

test.describe("Event Balloons mobile audience heroes", () => {
	for (const viewport of PHONE_VIEWPORTS) {
		for (const route of EVENT_BALLOONS_AUDIENCE_ROUTES) {
			test(`${route.name} keeps text and CTA visible at ${viewport.name}`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, route.path);
				await expectSuccessfulResponse(response, route.path);

				const result = await page.evaluate(() => {
					const hero = document.querySelector(".lt-authority-hero");
					const content = document.querySelector(".lt-authority-hero__content");
					const title = document.querySelector(".lt-authority-hero h1");
					const primary = document.querySelector(".lt-authority-hero .lt-authority-button");
					const visual = document.querySelector(".lt-authority-hero__visual");
					const proof = document.querySelector(".lt-authority-proof");
					if (!hero || !content || !title || !primary || !proof) return { found: false };
					const heroRect = hero.getBoundingClientRect();
					const contentRect = content.getBoundingClientRect();
					const titleRect = title.getBoundingClientRect();
					const primaryRect = primary.getBoundingClientRect();
					const proofRect = proof.getBoundingClientRect();
					return {
						found: true,
						heroHeight: Math.round(heroRect.height),
						contentTop: Math.round(contentRect.top),
						contentBottom: Math.round(contentRect.bottom),
						titleBottom: Math.round(titleRect.bottom),
						primaryBottom: Math.round(primaryRect.bottom),
						proofTop: Math.round(proofRect.top),
						heroTop: Math.round(heroRect.top),
						heroBottom: Math.round(heroRect.bottom),
						visualPresent: Boolean(visual),
						visualVisible: visual ? visual.getBoundingClientRect().height > 0 : false,
					};
				});

				expect(result.found, `${route.path} audience hero should expose content, CTA, and proof band`).toBe(true);
				expect(result.heroHeight, `${route.path} should keep the compact mobile hero height`).toBe(220);
				expect(result.contentTop, `${route.path} hero content should not be clipped above the hero`).toBeGreaterThanOrEqual(result.heroTop);
				expect(result.titleBottom, `${route.path} hero title should stay visible`).toBeLessThanOrEqual(result.heroBottom);
				expect(result.primaryBottom, `${route.path} hero CTA should stay visible`).toBeLessThanOrEqual(result.heroBottom);
				expect(result.contentBottom, `${route.path} hero content should fit before the proof band`).toBeLessThanOrEqual(result.heroBottom);
				expect(result.proofTop, `${route.path} proof should start after the compact hero`).toBeGreaterThanOrEqual(result.heroBottom - 1);
				expect(result.visualPresent, `${route.path} should not render the old real-photo panel inside the compact mobile hero`).toBe(false);
				expect(result.visualVisible, `${route.path} old real-photo panel should not consume mobile hero height`).toBe(false);
			});
		}
	}
});
