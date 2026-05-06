const { test, expect } = require("@playwright/test");
const {
	HEADER_VIEWPORTS,
	MOBILE_DRAWER_VIEWPORTS,
	gotoAndSettle,
	auditPageLayout,
	expectNoLayoutFailures,
} = require("./layout_helpers");

async function expectSuccessfulResponse(response, path) {
	expect(response, `${path} should return a response`).not.toBeNull();
	expect(response.status(), `${path} HTTP status`).toBeLessThan(400);
}

test.describe("Locally Twisted interactive layout states", () => {
	test.describe("header breakpoint contract", () => {
		for (const viewport of HEADER_VIEWPORTS) {
			test(`header uses ${viewport.expectedMode} mode at ${viewport.name}px`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/");
				await expectSuccessfulResponse(response, "/");

				const modes = await page.evaluate(() => {
					function visible(selector) {
						const element = document.querySelector(selector);
						if (!element) return false;
						const style = window.getComputedStyle(element);
						const rect = element.getBoundingClientRect();
						return (
							style.display !== "none" &&
							style.visibility !== "hidden" &&
							rect.width > 0 &&
							rect.height > 0
						);
					}
					return {
						desktopVisible: visible(".lt-mega-header__desktop"),
						mobileVisible: visible(".lt-mega-header__mobile"),
					};
				});

				if (viewport.expectedMode === "desktop") {
					expect(modes.desktopVisible).toBe(true);
					expect(modes.mobileVisible).toBe(false);
				} else {
					expect(modes.desktopVisible).toBe(false);
					expect(modes.mobileVisible).toBe(true);
				}

				const colorContract = await page.evaluate(() => {
					function background(selector) {
						const element = document.querySelector(selector);
						return element ? window.getComputedStyle(element).backgroundColor : null;
					}
					return {
						header: background(".lt-mega-header"),
						top: background(".lt-mega-header__top"),
						mobile: background(".lt-mega-header__mobile"),
					};
				});
				expect(colorContract.header, "header shell should use the warm-white style-guide surface").toBe("rgb(250, 247, 242)");
				expect(colorContract.header, "header shell should not regress to the black ink band").not.toBe("rgb(10, 10, 11)");
				if (viewport.expectedMode === "desktop") {
					expect(colorContract.top, "desktop proof row should keep the deep-navy authority band").toBe("rgb(14, 34, 64)");
				} else {
					expect(colorContract.mobile, "mobile header should use the warm-white style-guide surface").toBe("rgb(250, 247, 242)");
				}

				const result = await auditPageLayout(page, {
					containerSelectors: [".lt-mega-header", ".lt-mega-header__main-row", ".lt-mega-header__mobile-row"],
					targetSelectors: [".lt-mega-header__mobile-action", ".lt-mega-header__cart", ".lt-mega-header__search", ".lt-mega-header__cta"],
				});
				expectNoLayoutFailures(expect, result, `header at ${viewport.name}px`);
			});
		}
	});

	test.describe("desktop mega panels", () => {
		for (const viewport of HEADER_VIEWPORTS.filter((item) => item.expectedMode === "desktop")) {
			for (const trigger of ["lt-mega-events", "lt-mega-products"]) {
				test(`${trigger} panel fits at ${viewport.name}px`, async ({ page }) => {
					await page.setViewportSize({ width: viewport.width, height: viewport.height });
					const response = await gotoAndSettle(page, "/");
					await expectSuccessfulResponse(response, "/");

					await page.locator(`[data-lt-megamenu-trigger="${trigger}"]`).click();
					await expect(page.locator(`#${trigger}`)).toBeVisible();

					const result = await auditPageLayout(page, {
						containerSelectors: [
							".lt-mega-header",
							".lt-mega-header__main-row",
							".lt-megamenu__panel:not([hidden])",
							".lt-megamenu__grid",
						],
						targetSelectors: [
							".lt-mega-nav__button",
							".lt-mega-nav__link",
							".lt-mega-header__cart",
							".lt-mega-header__search",
							".lt-mega-header__cta",
						],
					});
					expectNoLayoutFailures(expect, result, `${trigger} at ${viewport.name}px`);
				});
			}
		}
	});

	test.describe("mobile and tablet drawer", () => {
		for (const viewport of MOBILE_DRAWER_VIEWPORTS) {
			test(`expanded drawer fits at ${viewport.name}px`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/");
				await expectSuccessfulResponse(response, "/");

				await page.locator("#lt-mobile-toggle").click();
				await expect(page.locator("#lt-mobile-nav")).toBeVisible();

				for (const panel of ["lt-mobile-events", "lt-mobile-products", "lt-mobile-help"]) {
					await page.locator(`[data-lt-drawer-accordion-trigger="${panel}"]`).click();
					await expect(page.locator(`#${panel}`)).toBeVisible();
				}

				const result = await auditPageLayout(page, {
					containerSelectors: [".lt-mega-drawer", ".lt-mega-drawer__panel:not([hidden])", ".lt-mega-drawer__cta"],
					targetSelectors: [
						"#lt-mobile-close",
						".lt-mega-header__mobile-action",
						".lt-mega-drawer__toggle",
						".lt-mega-drawer__cta",
					],
				});
				expectNoLayoutFailures(expect, result, `expanded drawer at ${viewport.name}px`);
			});
		}
	});

	test.describe("shop and product states", () => {
		for (const viewport of [
			{ name: "320", width: 320, height: 812 },
			{ name: "390", width: 390, height: 844 },
			{ name: "820", width: 820, height: 1180 },
			{ name: "1200", width: 1200, height: 900 },
		]) {
			test(`/shop filtered grid fits at ${viewport.name}px`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/shop");
				await expectSuccessfulResponse(response, "/shop");

				const secondChip = page.locator(".lt-shop__chip").nth(1);
				if ((await secondChip.count()) > 0) {
					await secondChip.click();
				}

				const result = await auditPageLayout(page, {
					containerSelectors: [".lt-shop__filters", ".lt-shop__grid", ".lt-shop__card"],
					targetSelectors: [".lt-shop__chip", ".lt-shop__card-add", ".lt-shop__cta-btn"],
				});
				expectNoLayoutFailures(expect, result, `/shop filtered at ${viewport.name}px`);
			});

			test(`variant product selectors fit at ${viewport.name}px`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/shop-items/bouquets/unicorn-bouquet");
				await expectSuccessfulResponse(response, "/shop-items/bouquets/unicorn-bouquet");
				await expect(page.locator(".lt-product__configure")).toHaveCount(1);
				await expect(page.locator(".lt-product__attr")).not.toHaveCount(0);

				const result = await auditPageLayout(page, {
					containerSelectors: [".lt-product__configure", ".lt-product__attr", ".lt-product__actions", ".lt-product__details"],
					targetSelectors: [".lt-product__chip", "#lt-add-to-cart-variant", ".lt-product__configure select"],
				});
				expectNoLayoutFailures(expect, result, `variant product at ${viewport.name}px`);
			});
		}

		test("desktop mega panel closes before product option interaction after scroll", async ({ page }) => {
			await page.setViewportSize({ width: 1200, height: 900 });
			const response = await gotoAndSettle(page, "/shop-items/bouquets/unicorn-bouquet");
			await expectSuccessfulResponse(response, "/shop-items/bouquets/unicorn-bouquet");

			await page.locator('[data-lt-megamenu-trigger="lt-mega-products"]').click();
			await expect(page.locator("#lt-mega-products")).toBeVisible();
			await page.evaluate(() => window.scrollBy(0, 320));
			await expect(page.locator("#lt-mega-products")).toBeHidden();

			await page.locator(".lt-product__attr[data-attribute-name='Bouquet Size'] .lt-product__chip").first().click();
			await expect(page.locator("#lt-add-to-cart-variant")).toBeDisabled();
		});
	});

	test.describe("content-heavy interactive states", () => {
		for (const viewport of [
			{ name: "320", width: 320, height: 812 },
			{ name: "414", width: 414, height: 896 },
			{ name: "820", width: 820, height: 1180 },
			{ name: "1200", width: 1200, height: 900 },
		]) {
			test(`contact expanded conditionals fit at ${viewport.name}px`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/contact");
				await expectSuccessfulResponse(response, "/contact");

				for (const value of ["Balloon Decor", "Events Inquiry", "Balloon Twisting"]) {
					await page.locator(`input[name="x_services"][value="${value}"]`).check({ force: true });
				}
				await page.waitForTimeout(250);

				const result = await auditPageLayout(page, {
					containerSelectors: [
						".lt-book",
						".lt-book__form-wrap",
						".lt-book__conditional:not([hidden])",
						".lt-book__services",
					],
					targetSelectors: [
						".lt-book__submit",
						".lt-book__check",
						".lt-book input:not([type='checkbox'])",
						".lt-book select",
						".lt-book textarea",
					],
				});
				expectNoLayoutFailures(expect, result, `contact expanded at ${viewport.name}px`);
			});
		}

		for (const viewport of [
			{ name: "320", width: 320, height: 812 },
			{ name: "820", width: 820, height: 1180 },
			{ name: "1366", width: 1366, height: 768 },
		]) {
			test(`portfolio modal fits at ${viewport.name}px`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/portfolio");
				await expectSuccessfulResponse(response, "/portfolio");

				await page.locator("[data-portfolio-card]").first().click();
				await expect(page.locator("[data-portfolio-modal]")).toBeVisible();

				const result = await auditPageLayout(page, {
					containerSelectors: ["[data-portfolio-modal]", ".lt-portfolio-modal__panel", ".lt-portfolio-modal__caption"],
					targetSelectors: [".lt-portfolio-modal__close"],
				});
				expectNoLayoutFailures(expect, result, `portfolio modal at ${viewport.name}px`);
			});
		}
	});

	test.describe("homepage review marquee", () => {
		for (const viewport of [
			{ name: "mobile", width: 375, height: 900 },
			{ name: "desktop", width: 1366, height: 900 },
		]) {
			test(`reviews crawl left-to-right and stay unstacked on ${viewport.name}`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				await page.emulateMedia({ reducedMotion: "no-preference" });
				const response = await gotoAndSettle(page, "/");
				await expectSuccessfulResponse(response, "/");

				const before = await page.evaluate(() => {
					const track = document.querySelector(".lt-reviews-block__track");
					const cards = Array.from(document.querySelectorAll(".lt-reviews-block__quote")).slice(0, 4);
					const matrix = new DOMMatrixReadOnly(window.getComputedStyle(track).transform);
					const tops = cards.map((card) => Math.round(card.getBoundingClientRect().top));
					return {
						x: matrix.m41,
						topDelta: Math.max(...tops) - Math.min(...tops),
						cardCount: cards.length,
						animationName: window.getComputedStyle(track).animationName,
						animationDuration: window.getComputedStyle(track).animationDuration,
					};
				});

				await page.waitForTimeout(1200);

				const after = await page.evaluate(() => {
					const track = document.querySelector(".lt-reviews-block__track");
					const matrix = new DOMMatrixReadOnly(window.getComputedStyle(track).transform);
					return { x: matrix.m41 };
				});

				expect(before.cardCount).toBeGreaterThanOrEqual(4);
				expect(before.animationName).toBe("lt-reviews-scroll");
				expect(before.animationDuration).toBe("540s");
				expect(before.topDelta, "first review cards should share one horizontal row").toBeLessThanOrEqual(1);
				expect(after.x, "review track should move right over time").toBeGreaterThan(before.x);
			});
		}
	});

	test("homepage reduced motion disables moving headline and marquee tracks", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await page.emulateMedia({ reducedMotion: "reduce" });
		const response = await gotoAndSettle(page, "/");
		await expectSuccessfulResponse(response, "/");

		const motion = await page.evaluate(() => {
			function animation(selector) {
				const element = document.querySelector(selector);
				if (!element) return null;
				const style = window.getComputedStyle(element);
				return {
					animationName: style.animationName,
					animationDuration: style.animationDuration,
				};
			}
			return {
				hero: animation(".lt-hero__title"),
				reviews: animation(".lt-reviews-block__track"),
				crawl: animation(".lt-crawl__track"),
			};
		});

		expect(motion.hero && motion.hero.animationName).toBe("none");
		expect(motion.reviews && motion.reviews.animationName).toBe("none");
		expect(motion.crawl && motion.crawl.animationName).toBe("none");
	});
});
