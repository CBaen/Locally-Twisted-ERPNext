const { test, expect } = require("@playwright/test");
const {
	gotoAndSettle,
	auditPageLayout,
	expectNoLayoutFailures,
} = require("./layout_helpers");

async function expectSuccessfulResponse(response, path) {
	expect(response, `${path} should return a response`).not.toBeNull();
	expect(response.status(), `${path} HTTP status`).toBeLessThan(400);
}

test.describe("portfolio proof reel", () => {
	test("desktop keeps full photos in the floating reel", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 900 });
		const response = await gotoAndSettle(page, "/portfolio");
		await expectSuccessfulResponse(response, "/portfolio");
		await page.waitForTimeout(250);

		const facts = await page.evaluate(() => {
			const reel = document.querySelector("[data-portfolio-reel]");
			const cards = Array.from(document.querySelectorAll("[data-portfolio-card]"));
			const visibleCards = cards.filter((card) => !card.hasAttribute("hidden"));
			const first = visibleCards[0];
			const firstImage = first ? first.querySelector("img") : null;
			const firstStyle = first ? window.getComputedStyle(first) : null;
			const imageStyle = firstImage ? window.getComputedStyle(firstImage) : null;
			const textBody = first ? first.querySelector(".lt-portfolio-card__body") : null;
			const textStyle = textBody ? window.getComputedStyle(textBody) : null;
			const rect = first ? first.getBoundingClientRect() : null;
			return {
				hasReel: Boolean(reel),
				cardCount: cards.length,
				visibleCount: visibleCards.length,
				firstPosition: firstStyle ? firstStyle.position : null,
				firstWidth: rect ? Math.round(rect.width) : 0,
				firstHeight: rect ? Math.round(rect.height) : 0,
				imageObjectFit: imageStyle ? imageStyle.objectFit : null,
				imageWidthAttr: firstImage ? firstImage.getAttribute("width") : null,
				imageHeightAttr: firstImage ? firstImage.getAttribute("height") : null,
				textIsScreenReaderOnly: textStyle
					? textStyle.position === "absolute" && textStyle.overflow === "hidden"
					: false,
			};
		});

		expect(facts.hasReel).toBe(true);
		expect(facts.cardCount).toBeGreaterThanOrEqual(15);
		expect(facts.visibleCount).toBe(facts.cardCount);
		expect(facts.firstPosition).toBe("absolute");
		expect(facts.firstWidth).toBeGreaterThan(450);
		expect(facts.firstHeight).toBeGreaterThan(300);
		expect(facts.imageObjectFit).toBe("contain");
		expect(Number(facts.imageWidthAttr)).toBeGreaterThan(0);
		expect(Number(facts.imageHeightAttr)).toBeGreaterThan(0);
		expect(facts.textIsScreenReaderOnly).toBe(true);

		const result = await auditPageLayout(page, {
			containerSelectors: ["[data-portfolio-filter]"],
			targetSelectors: ["[data-portfolio-card]", ".lt-portfolio-filter__pill button"],
		});
		expectNoLayoutFailures(expect, result, "portfolio proof reel desktop");
	});

	test("mobile stacks natural-ratio images without horizontal overflow", async ({ page }) => {
		await page.setViewportSize({ width: 375, height: 812 });
		const response = await gotoAndSettle(page, "/portfolio");
		await expectSuccessfulResponse(response, "/portfolio");
		await page.waitForTimeout(250);

		const facts = await page.evaluate(() => {
			const first = document.querySelector("[data-portfolio-card]");
			const firstImage = first ? first.querySelector("img") : null;
			const cardStyle = first ? window.getComputedStyle(first) : null;
			const imageStyle = firstImage ? window.getComputedStyle(firstImage) : null;
			const docWidth = Math.max(
				document.documentElement.scrollWidth,
				document.body ? document.body.scrollWidth : 0,
			);
			return {
				cardPosition: cardStyle ? cardStyle.position : null,
				cardWidth: first ? Math.round(first.getBoundingClientRect().width) : 0,
				imageObjectFit: imageStyle ? imageStyle.objectFit : null,
				docWidth,
				viewportWidth: document.documentElement.clientWidth,
			};
		});

		expect(facts.cardPosition).toBe("relative");
		expect(facts.cardWidth).toBeGreaterThanOrEqual(370);
		expect(facts.imageObjectFit).toBe("contain");
		expect(facts.docWidth).toBeLessThanOrEqual(facts.viewportWidth + 2);

		const result = await auditPageLayout(page, {
			containerSelectors: ["[data-portfolio-filter]"],
			targetSelectors: ["[data-portfolio-card]", ".lt-portfolio-filter__pill button"],
		});
		expectNoLayoutFailures(expect, result, "portfolio proof reel mobile");
	});

	test("filters relayout the reel and keep the empty state reachable", async ({ page }) => {
		await page.setViewportSize({ width: 1280, height: 900 });
		const response = await gotoAndSettle(page, "/portfolio");
		await expectSuccessfulResponse(response, "/portfolio");

		await page.locator('[data-event-pill="corporate"]').click();
		await expect(page).toHaveURL(/event=corporate/);
		const corporateVisible = await page.locator("[data-portfolio-card]:not([hidden])").count();
		expect(corporateVisible).toBeGreaterThan(0);

		await page.locator("[data-category-select]").selectOption("balloon-drops");
		await expect(page.locator("[data-portfolio-count]")).toContainText("0 pieces");
		await expect(page.locator(".lt-portfolio-empty")).toBeVisible();

		const result = await auditPageLayout(page, {
			containerSelectors: ["[data-portfolio-filter]", "[data-portfolio-grid]", ".lt-portfolio-empty"],
			targetSelectors: [".lt-portfolio-empty__cta", ".lt-portfolio-filter__clear"],
		});
		expectNoLayoutFailures(expect, result, "portfolio filtered empty state");
	});
});
