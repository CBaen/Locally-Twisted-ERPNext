const { test, expect } = require("@playwright/test");
const {
	BASE_URL,
	HEADER_VIEWPORTS,
	MOBILE_DRAWER_VIEWPORTS,
	PUBLIC_ROUTES,
	gotoAndSettle,
	auditPageLayout,
	expectNoLayoutFailures,
} = require("./layout_helpers");

const PLATFORM_WORDS = /\b(?:ERPNext|Frappe)\b/i;

const COMPACT_HERO_VIEWPORTS = [
	{ name: "mobile", width: 390, height: 844, expectedHeight: 220, maxPadding: 24, maxTitle: 32 },
	{ name: "desktop", width: 1366, height: 768, expectedHeight: 280, maxPadding: 32, maxTitle: 44 },
];

const COMPACT_HERO_ROUTES = [
	{
		name: "home",
		path: "/",
		heroSelector: ".lt-hero",
		contentSelector: ".lt-hero__content",
		titleSelector: ".lt-hero__title",
	},
	{
		name: "event balloons",
		path: "/event-balloons",
		heroSelector: ".lt-authority-hero",
		contentSelector: ".lt-authority-hero__content",
		titleSelector: ".lt-authority-hero h1",
	},
	{
		name: "civic community",
		path: "/civic-community",
		heroSelector: ".lt-authority-hero",
		contentSelector: ".lt-authority-hero__content",
		titleSelector: ".lt-authority-hero h1",
	},
	{
		name: "corporate events",
		path: "/corporate-events",
		heroSelector: ".lt-authority-hero",
		contentSelector: ".lt-authority-hero__content",
		titleSelector: ".lt-authority-hero h1",
	},
	{
		name: "schools campuses",
		path: "/schools-campuses",
		heroSelector: ".lt-authority-hero",
		contentSelector: ".lt-authority-hero__content",
		titleSelector: ".lt-authority-hero h1",
	},
	{
		name: "private celebrations",
		path: "/private-celebrations",
		heroSelector: ".lt-authority-hero",
		contentSelector: ".lt-authority-hero__content",
		titleSelector: ".lt-authority-hero h1",
	},
	{
		name: "portfolio",
		path: "/portfolio",
		heroSelector: ".lt-portfolio__hero",
		contentSelector: ".lt-portfolio__hero-inner",
		titleSelector: ".lt-portfolio__title",
	},
	{
		name: "twisting and face painting",
		path: "/balloon-twisting-and-face-painting",
		heroSelector: ".lt-btfp__intro",
		contentSelector: ".lt-btfp__intro-inner",
		titleSelector: ".lt-btfp__intro-title",
	},
	{
		name: "contact",
		path: "/contact",
		heroSelector: ".lt-contact__intro",
		contentSelector: ".lt-contact__intro .container",
		titleSelector: ".lt-contact__intro h1",
	},
	{
		name: "shop",
		path: "/shop",
		heroSelector: ".lt-shop__hero",
		contentSelector: ".lt-shop__hero-inner",
		titleSelector: ".lt-shop__hero-title",
	},
	{
		name: "shop category",
		path: "/shop-items/seasonal-specialty",
		heroSelector: ".lt-shop__hero",
		contentSelector: ".lt-shop__hero-inner",
		titleSelector: ".lt-shop__title",
	},
];

async function expectSuccessfulResponse(response, path) {
	expect(response, `${path} should return a response`).not.toBeNull();
	expect(response.status(), `${path} HTTP status`).toBeLessThan(400);
}

async function dismissCookieNotice(page) {
	const banner = page.locator(".lt-cookie-consent");
	if ((await banner.count()) === 0) return;
	if (!(await banner.isVisible().catch(() => false))) return;
	await page.locator(".lt-cookie-consent__button--secondary").click();
	await expect(banner).toHaveCount(0);
}

test.describe("Locally Twisted interactive layout states", () => {
	test.describe("compact hero height contract", () => {
		for (const viewport of COMPACT_HERO_VIEWPORTS) {
			for (const route of COMPACT_HERO_ROUTES) {
				test(`${route.name} hero uses the ${viewport.name} standard`, async ({ page }) => {
					await page.setViewportSize({ width: viewport.width, height: viewport.height });
					const response = await gotoAndSettle(page, route.path);
					await expectSuccessfulResponse(response, route.path);

					const result = await page.evaluate(({ route, viewport }) => {
						const hero = document.querySelector(route.heroSelector);
						const content = document.querySelector(route.contentSelector);
						const title = document.querySelector(route.titleSelector);
						if (!hero || !content || !title) {
							return {
								found: false,
								missing: {
									hero: !hero,
									content: !content,
									title: !title,
								},
							};
						}

						const heroStyle = window.getComputedStyle(hero);
						const contentStyle = window.getComputedStyle(content);
						const titleStyle = window.getComputedStyle(title);
						const header = document.querySelector(".lt-mega-header, .navbar");
						const heroRect = hero.getBoundingClientRect();
						const headerRect = header ? header.getBoundingClientRect() : null;
						const titleRect = title.getBoundingClientRect();
						const next = hero.nextElementSibling;
						const nextRect = next ? next.getBoundingClientRect() : null;
						const paddingTop = Math.max(parseFloat(heroStyle.paddingTop), parseFloat(contentStyle.paddingTop));
						const paddingBottom = Math.max(parseFloat(heroStyle.paddingBottom), parseFloat(contentStyle.paddingBottom));

						return {
							found: true,
							height: Math.round(heroRect.height),
							expectedHeight: viewport.expectedHeight,
							paddingTop,
							paddingBottom,
							maxPadding: viewport.maxPadding,
							titleFontSize: parseFloat(titleStyle.fontSize),
							maxTitle: viewport.maxTitle,
							contentFitsHero: hero.scrollHeight <= hero.clientHeight + 2,
							titleFitsHero: titleRect.bottom <= heroRect.bottom + 1,
							headerToHeroGap: headerRect ? Math.round(heroRect.top - headerRect.bottom) : null,
							nextBandTop: nextRect ? nextRect.top : null,
							viewportHeight: window.innerHeight,
						};
					}, { route, viewport });

					expect(result.found, `${route.path} should expose the named hero contract elements`).toBe(true);
					expect(result.height, `${route.path} hero height should match the approved ${viewport.name} standard`).toBe(result.expectedHeight);
					expect(result.paddingTop, `${route.path} hero top padding should not exceed the approved ${viewport.name} cap`).toBeLessThanOrEqual(result.maxPadding);
					expect(result.paddingBottom, `${route.path} hero bottom padding should not exceed the approved ${viewport.name} cap`).toBeLessThanOrEqual(result.maxPadding);
					expect(result.titleFontSize, `${route.path} hero title should not overwhelm the page`).toBeLessThanOrEqual(result.maxTitle);
					expect(result.contentFitsHero, `${route.path} hero content should fit inside the standard height`).toBe(true);
					expect(result.titleFitsHero, `${route.path} hero title should not spill below the hero`).toBe(true);
					expect(result.headerToHeroGap, `${route.path} hero should sit flush under the public header`).not.toBeNull();
					expect(Math.abs(result.headerToHeroGap), `${route.path} should not expose a Frappe wrapper gap above the hero`).toBeLessThanOrEqual(1);
					if (viewport.name === "desktop" && result.nextBandTop !== null) {
						expect(result.nextBandTop, `${route.path} should show the next section in the first laptop viewport`).toBeLessThan(result.viewportHeight - 16);
					}
				});
			}
		}
	});

	test.describe("white-label platform leakage", () => {
		for (const route of [...PUBLIC_ROUTES, { name: "login", path: "/login" }]) {
			test(`${route.name} has no platform names in visible text`, async ({ page }) => {
				await page.setViewportSize({ width: 1200, height: 900 });
				const response = await gotoAndSettle(page, route.path);
				await expectSuccessfulResponse(response, route.path);
				const visibleText = await page.locator("body").innerText();
				expect(visibleText, `${route.path} visible body text should stay white-labeled`).not.toMatch(PLATFORM_WORDS);
			});
		}

		test("desktop and mobile menu states keep platform names out of visible text", async ({ page }) => {
			await page.setViewportSize({ width: 1200, height: 900 });
			const desktopResponse = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(desktopResponse, "/");

			for (const trigger of ["lt-mega-events", "lt-mega-products"]) {
				await page.locator(`[data-lt-megamenu-trigger="${trigger}"]`).click();
				await expect(page.locator(`#${trigger}`)).toBeVisible();
				const visibleText = await page.locator("body").innerText();
				expect(visibleText, `${trigger} visible menu text should stay white-labeled`).not.toMatch(PLATFORM_WORDS);
				await page.locator(`[data-lt-megamenu-trigger="${trigger}"]`).click();
			}

			await page.setViewportSize({ width: 390, height: 844 });
			const mobileResponse = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(mobileResponse, "/");
			await dismissCookieNotice(page);

			await page.locator("#lt-mobile-toggle").click();
			await expect(page.locator("#lt-mobile-nav")).toBeVisible();
			for (const panel of ["lt-mobile-events", "lt-mobile-products"]) {
				await page.locator(`[data-lt-drawer-accordion-trigger="${panel}"]`).click();
				await expect(page.locator(`#${panel}`)).toBeVisible();
			}
			const drawerText = await page.locator("body").innerText();
			expect(drawerText, "expanded mobile drawer text should stay white-labeled").not.toMatch(PLATFORM_WORDS);
		});

		for (const route of ["/", "/login"]) {
			test(`${route} uses Locally Twisted favicon and login logo chrome`, async ({ page }) => {
				await page.setViewportSize({ width: 1200, height: 900 });
				const response = await gotoAndSettle(page, route);
				await expectSuccessfulResponse(response, route);

				const html = await page.content();
				expect(html, `${route} source should not expose the platform generator banner`).not.toContain("Built on Frappe");
				expect(html, `${route} source should not expose the platform generator meta tag`).not.toContain('name="generator" content="frappe"');
				expect(html, `${route} source should not expose LT-authored framework comments`).not.toContain("custom Frappe app");

				const iconHrefs = await page
					.locator('link[rel*="icon"]')
					.evaluateAll((links) => links.map((link) => link.getAttribute("href") || ""));
				expect(iconHrefs.length, `${route} should declare an icon`).toBeGreaterThan(0);
				for (const href of iconHrefs) {
					expect(href, `${route} icon href should not expose ERPNext/Frappe default branding`).not.toMatch(/\/assets\/(?:erpnext|frappe)\//i);
					const iconUrl = new URL(href, response.url()).toString();
					const iconResponse = await page.request.get(iconUrl);
					expect(iconResponse.status(), `${route} icon ${iconUrl} should be served`).toBeLessThan(400);
					const iconBody = await iconResponse.body();
					expect(iconBody.length, `${route} favicon should be a small browser icon, not a full-size brand asset`).toBeLessThanOrEqual(50_000);
					const dimensions = await page.evaluate(async (source) => {
						const image = new Image();
						image.src = source;
						await image.decode();
						return {
							width: image.naturalWidth,
							height: image.naturalHeight,
						};
					}, iconUrl);
					expect(dimensions.width, `${route} favicon width should be favicon-sized`).toBeLessThanOrEqual(128);
					expect(dimensions.height, `${route} favicon height should be favicon-sized`).toBeLessThanOrEqual(128);
				}

				const appLogoSrcs = await page
					.locator("img.app-logo")
					.evaluateAll((images) => images.map((image) => image.getAttribute("src") || ""));
				for (const src of appLogoSrcs) {
					expect(src, `${route} login/app logo should not use default platform artwork`).not.toMatch(/(?:erpnext|frappe)-(?:logo|favicon)|\/assets\/(?:erpnext|frappe)\//i);
				}
			});
		}

		test("homepage serves the current site-preferences cache buster", async ({ page }) => {
			await page.setViewportSize({ width: 1200, height: 900 });
			const response = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(response, "/");

			const scriptSrcs = await page
				.locator('script[src*="lt-site-preferences.js"]')
				.evaluateAll((scripts) => scripts.map((script) => script.getAttribute("src") || ""));
			expect(
				scriptSrcs.some((src) => src.includes("lt-site-preferences.js?v=20260510-form-inline-1")),
				"site-preferences script should be cache-busted when inline notice behavior changes"
			).toBe(true);
		});
	});

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

		test("small mobile header keeps logo clear of cart and menu controls", async ({ page }) => {
			await page.setViewportSize({ width: 320, height: 812 });
			const response = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(response, "/");

			const result = await page.evaluate(() => {
				const logo = document.querySelector(".lt-mega-header__mobile-logo");
				const actions = document.querySelector(".lt-mega-header__mobile-actions");
				const logoRect = logo ? logo.getBoundingClientRect() : null;
				const actionsRect = actions ? actions.getBoundingClientRect() : null;
				return {
					found: Boolean(logo && actions),
					mobileActionCount: document.querySelectorAll(".lt-mega-header__mobile-actions .lt-mega-header__mobile-action").length,
					mobileSearchCount: document.querySelectorAll(".lt-mega-header__mobile-search").length,
					logoRight: logoRect ? logoRect.right : null,
					actionsLeft: actionsRect ? actionsRect.left : null,
				};
			});

			expect(result.found, "mobile header should expose the logo and action group").toBe(true);
			expect(result.mobileActionCount, "mobile header should only carry cart and menu controls").toBe(2);
			expect(result.mobileSearchCount, "mobile search belongs at the bottom of the drawer").toBe(0);
			expect(result.logoRight, "logo should not collide with cart/menu controls").toBeLessThanOrEqual(result.actionsLeft - 8);
		});
	});

	test.describe("header search overlay", () => {
		for (const viewport of [
			{ name: "mobile", width: 390, height: 844, toggle: ".lt-mega-drawer__search", openDrawer: true },
			{ name: "desktop", width: 1366, height: 768, toggle: ".lt-mega-header__search" },
		]) {
			test(`search opens as an overlay on ${viewport.name}`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/");
				await expectSuccessfulResponse(response, "/");
				await dismissCookieNotice(page);

				const beforeUrl = page.url();
				if (viewport.openDrawer) {
					await page.locator("#lt-mobile-toggle").click();
					await expect(page.locator("#lt-mobile-nav")).toHaveClass(/is-open/);
				}
				const toggle = page.locator(viewport.toggle);
				await expect(toggle).toHaveCount(1);
				await expect(toggle).not.toHaveAttribute("href", /.+/);
				await toggle.click();
				if (viewport.openDrawer) {
					await expect(page.locator("#lt-mobile-nav")).not.toHaveClass(/is-open/);
				}

				const panel = page.locator("#lt-site-search-panel");
				await expect(panel).toBeVisible();
				await expect(page.locator("#lt-site-search-input")).toBeFocused();
				expect(page.url(), "search overlay should not navigate").toBe(beforeUrl);

				await page.locator("#lt-site-search-input").fill("arches");
				await expect(page.locator("#lt-site-search-panel a[href='/shop-items/arches']")).toBeVisible();
				await expect(page.locator("#lt-site-search-panel a[href='/portfolio']")).toBeHidden();

				const result = await auditPageLayout(page, {
					containerSelectors: [".lt-mega-header", "#lt-site-search-panel", ".lt-site-search-panel__field"],
					targetSelectors: [
						viewport.toggle,
						"#lt-site-search-input",
						".lt-site-search-panel__field button",
						"#lt-site-search-panel a",
					],
				});
				expectNoLayoutFailures(expect, result, `search overlay at ${viewport.name}`);
			});
		}

		test("search query submits to shop results", async ({ page }) => {
			await page.setViewportSize({ width: 1366, height: 768 });
			const response = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(response, "/");

			await page.locator(".lt-mega-header__search").click();
			await page.locator("#lt-site-search-input").fill("arches");
			await Promise.all([
				page.waitForURL(/\/shop\?q=arches$/),
				page.keyboard.press("Enter"),
			]);
			await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});

			await expect(page.locator(".lt-shop__search-summary")).toContainText('Showing matches for "arches".');
			await expect(page.locator(".lt-shop__card", { hasText: "Classic Arch" })).toBeVisible();
		});

		test("shop query results are not served from the broad shop cache", async ({ page }) => {
			await page.setViewportSize({ width: 1366, height: 768 });
			const shopResponse = await gotoAndSettle(page, "/shop");
			await expectSuccessfulResponse(shopResponse, "/shop");
			await expect(page.locator("#lt-shop-count")).toContainText("53 items");

			const queryResponse = await gotoAndSettle(page, "/shop?q=zzznothing");
			await expectSuccessfulResponse(queryResponse, "/shop?q=zzznothing");
			await expect(page.locator(".lt-shop__search-summary")).toContainText('Showing matches for "zzznothing".');
			await expect(page.locator(".lt-shop__empty")).toBeVisible();
			await expect(page.locator("#lt-shop-grid")).toHaveCount(0);
		});

		test("/search is not a public page", async ({ page }) => {
			const response = await page.goto(new URL("/search", BASE_URL).toString(), {
				waitUntil: "domcontentloaded",
			});
			expect(response, "/search should return a response").not.toBeNull();
			expect(response.status(), "/search should return 404").toBe(404);
		});
	});

	test.describe("desktop mega panels", () => {
		test("event mega panel links to specialized event pages", async ({ page }) => {
			await page.setViewportSize({ width: 1366, height: 768 });
			const response = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(response, "/");

			await page.locator('[data-lt-megamenu-trigger="lt-mega-events"]').click();
			await expect(page.locator("#lt-mega-events")).toBeVisible();

			const expectedLinks = [
				["Civic & Community", "/civic-community"],
				["Corporate Events", "/corporate-events"],
				["Schools & Campuses", "/schools-campuses"],
				["Private Celebrations", "/private-celebrations"],
			];
			for (const [label, href] of expectedLinks) {
				const link = page.locator("#lt-mega-events a", { hasText: label });
				await expect(link, `${label} menu link should exist`).toHaveCount(1);
				await expect(link, `${label} menu link route`).toHaveAttribute("href", href);
			}
			await expect(page.locator("#lt-mega-events", { hasText: "Corporate Entrances" })).toHaveCount(0);
			await expect(page.locator("#lt-mega-events .lt-megamenu__card[href='/portfolio']")).toHaveCount(0);
			await expect(page.locator("#lt-mega-events .lt-megamenu__card[href='/event-balloons']")).toHaveCount(0);
		});

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
				await dismissCookieNotice(page);

				await page.locator("#lt-mobile-toggle").click();
				await expect(page.locator("#lt-mobile-nav")).toBeVisible();

				for (const panel of ["lt-mobile-events", "lt-mobile-products"]) {
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
						".lt-mega-drawer__search",
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
			test(`/shop category navigation and grid fit at ${viewport.name}px`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/shop");
				await expectSuccessfulResponse(response, "/shop");

				await expect(page.locator(".lt-shop__chip")).toHaveCount(0);
				await expect(page.locator(".lt-shop__category-select")).toHaveCount(1);
				if (viewport.width >= 992) {
					await expect(page.locator(".lt-shop__category-rail nav")).toBeVisible();
				} else {
					await expect(page.locator(".lt-shop__category-select")).toBeVisible();
				}

				const result = await auditPageLayout(page, {
					containerSelectors: [".lt-shop__category-rail", ".lt-shop__grid", ".lt-shop__card"],
					targetSelectors: [".lt-shop__category-link", ".lt-shop__category-select", ".lt-shop__card-add", ".lt-shop__cta-btn"],
				});
				expectNoLayoutFailures(expect, result, `/shop category navigation at ${viewport.name}px`);
			});

			test(`variant product selectors fit at ${viewport.name}px`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/shop-items/bouquets/unicorn-bouquet");
				await expectSuccessfulResponse(response, "/shop-items/bouquets/unicorn-bouquet");
				await expect(page.locator(".lt-product__configure")).toHaveCount(1);
				await expect(page.locator(".lt-product__attr")).toHaveCount(1);
				await expect(page.locator(".lt-product__attr[data-attribute-name='Bouquet Size']")).toHaveCount(1);
				await expect(page.locator("text=Add Foil Number")).toHaveCount(0);

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
			await expect(page.locator("#lt-add-to-cart-variant")).toBeEnabled();
			await expect(page.locator("#lt-add-to-cart-variant")).toHaveAttribute("data-item-code", /unicorn-bouquet-SMA/);
		});

		test("multi-photo product gallery avoids horizontal scrollbars and supports mobile swipe", async ({ page }) => {
			await page.setViewportSize({ width: 390, height: 844 });
			const response = await gotoAndSettle(page, "/shop-items/arches/classic-arch");
			await expectSuccessfulResponse(response, "/shop-items/arches/classic-arch");
			await expect(page.locator(".lt-product__thumbnail-button")).toHaveCount(5);

			const before = await page.locator(".product-image img.website-image").first().getAttribute("src");
			await page.locator(".product-image").dispatchEvent("pointerdown", {
				pointerId: 1,
				pointerType: "touch",
				clientX: 340,
				clientY: 300,
				isPrimary: true,
			});
			await page.locator(".product-image").dispatchEvent("pointerup", {
				pointerId: 1,
				pointerType: "touch",
				clientX: 80,
				clientY: 304,
				isPrimary: true,
			});
			await expect.poll(async () => page.locator(".product-image img.website-image").first().getAttribute("src")).not.toBe(before);

			const mobile = await page.evaluate(() => {
				const rail = document.querySelector(".lt-product__thumbnail-rail");
				const doc = document.documentElement;
				const offenders = Array.from(document.querySelectorAll("body *"))
					.map((element) => {
						const style = window.getComputedStyle(element);
						return {
							className: String(element.className || ""),
							overflowX: style.overflowX,
							scrollbarWidth: style.scrollbarWidth,
							scrollWidth: element.scrollWidth,
							clientWidth: element.clientWidth,
						};
					})
					.filter((item) => ["auto", "scroll"].includes(item.overflowX) && item.scrollWidth > item.clientWidth + 1 && item.scrollbarWidth !== "none");
				return {
					documentOverflow: doc.scrollWidth - doc.clientWidth,
					railOverflowX: rail ? window.getComputedStyle(rail).overflowX : null,
					railScrollbarWidth: rail ? window.getComputedStyle(rail).scrollbarWidth : null,
					railScrollSnapType: rail ? window.getComputedStyle(rail).scrollSnapType : null,
					offenders,
				};
			});
			expect(Math.abs(mobile.documentOverflow), "product page must not create document-level horizontal overflow").toBeLessThanOrEqual(1);
			expect(mobile.railOverflowX, "mobile gallery may be swipeable, but not with a visible native scrollbar").toBe("auto");
			expect(mobile.railScrollbarWidth, "mobile gallery must hide native scrollbar chrome").toBe("none");
			expect(mobile.railScrollSnapType, "mobile gallery should use a swipe/snap photo strip").toContain("x");
			expect(mobile.offenders, "no visible internal horizontal scrollbars are allowed").toEqual([]);

			await page.setViewportSize({ width: 1366, height: 900 });
			await gotoAndSettle(page, "/shop-items/arches/classic-arch");
			const desktop = await page.evaluate(() => {
				const doc = document.documentElement;
				const offenders = Array.from(document.querySelectorAll("body *"))
					.map((element) => {
						const style = window.getComputedStyle(element);
						return {
							className: String(element.className || ""),
							overflowX: style.overflowX,
							scrollbarWidth: style.scrollbarWidth,
							scrollWidth: element.scrollWidth,
							clientWidth: element.clientWidth,
						};
					})
					.filter((item) => ["auto", "scroll"].includes(item.overflowX) && item.scrollWidth > item.clientWidth + 1 && item.scrollbarWidth !== "none");
				return {
					documentOverflow: doc.scrollWidth - doc.clientWidth,
					offenders,
				};
			});
			expect(Math.abs(desktop.documentOverflow), "desktop product page must not create horizontal overflow").toBeLessThanOrEqual(1);
			expect(desktop.offenders, "desktop product gallery must not expose internal horizontal scrollbars").toEqual([]);
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
				await dismissCookieNotice(page);

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
			test(`portfolio front-photo state fits at ${viewport.name}px`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, "/portfolio");
				await expectSuccessfulResponse(response, "/portfolio");
				await dismissCookieNotice(page);

				await page.waitForSelector(".lt-photo");
				await page.locator(".lt-photo").first().scrollIntoViewIfNeeded();
				await page.locator(".lt-photo").first().click({ force: true });
				await expect(page.locator(".lt-photo.is-front")).toHaveCount(1);

				const result = await auditPageLayout(page, {
					targetSelectors: [".lt-photo.is-front"],
				});
				expectNoLayoutFailures(expect, result, `portfolio front-photo state at ${viewport.name}px`);
			});
		}
	});

	test.describe("homepage review marquee", () => {
		for (const viewport of [
			{ name: "mobile", width: 375, height: 900 },
			{ name: "desktop", width: 1366, height: 900 },
		]) {
			test(`reviews crawl left-to-right and stay full-stage on ${viewport.name}`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				await page.emulateMedia({ reducedMotion: "no-preference" });
				const response = await gotoAndSettle(page, "/");
				await expectSuccessfulResponse(response, "/");
				await page.waitForFunction(() => document.documentElement.dataset.ltCrawlSpeed === "synced", null, { timeout: 5000 });

				const before = await page.evaluate(() => {
					const track = document.querySelector(".lt-reviews-block__track");
					const cards = Array.from(document.querySelectorAll(".lt-reviews-block__quote")).slice(0, 4);
					const matrix = new DOMMatrixReadOnly(window.getComputedStyle(track).transform);
					const tops = cards.map((card) => Math.round(card.getBoundingClientRect().top));
					return {
						x: matrix.m41,
						topDelta: Math.max(...tops) - Math.min(...tops),
						cardCount: cards.length,
						quotesRect: document.querySelector(".lt-reviews-block__quotes").getBoundingClientRect(),
						overflowX: window.getComputedStyle(document.querySelector(".lt-reviews-block__quotes")).overflowX,
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
				expect(Math.round(before.quotesRect.left), "review banner should start at the viewport edge").toBeLessThanOrEqual(1);
				expect(Math.round(before.quotesRect.right), "review banner should reach the viewport edge").toBeGreaterThanOrEqual(viewport.width - 1);
				expect(before.overflowX).toBe("hidden");
				expect(after.x, "review track should move left-to-right over time").toBeGreaterThan(before.x);
			});
		}

		test("mobile review proof keeps the compact sizing contract", async ({ page }) => {
			await page.setViewportSize({ width: 390, height: 844 });
			const response = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(response, "/");

			const result = await page.evaluate(() => {
				function box(selector) {
					const element = document.querySelector(selector);
					if (!element) return null;
					const rect = element.getBoundingClientRect();
					const style = window.getComputedStyle(element);
					return {
						height: rect.height,
						width: rect.width,
						paddingTop: parseFloat(style.paddingTop),
						paddingBottom: parseFloat(style.paddingBottom),
						paddingLeft: parseFloat(style.paddingLeft),
						paddingRight: parseFloat(style.paddingRight),
					};
				}

				const cards = Array.from(document.querySelectorAll(".lt-reviews-block__quote")).map((card) => {
					const rect = card.getBoundingClientRect();
					return { height: rect.height, width: rect.width };
				});

				return {
					block: box(".lt-reviews-block"),
					badge: box(".lt-reviews-block__badge"),
					quotes: box(".lt-reviews-block__quotes"),
					card: box(".lt-reviews-block__quote"),
					cardCount: cards.length,
					maxCardHeight: Math.max(...cards.map((card) => card.height)),
					maxCardWidth: Math.max(...cards.map((card) => card.width)),
				};
			});

			expect(result.block, "reviews block should render").not.toBeNull();
			expect(result.cardCount, "reviews crawl should include customer cards").toBeGreaterThanOrEqual(4);
			expect(result.block.height, "mobile Google review section should not dominate the first scroll").toBeLessThanOrEqual(380);
			expect(result.block.paddingTop, "mobile review section top padding should stay compact").toBeLessThanOrEqual(26);
			expect(result.block.paddingBottom, "mobile review section bottom padding should stay compact").toBeLessThanOrEqual(30);
			expect(result.badge.height, "mobile Google rating badge should stay compact").toBeLessThanOrEqual(76);
			expect(result.quotes.height, "mobile review marquee should not be a tall card stack").toBeLessThanOrEqual(240);
			expect(result.quotes.paddingTop, "global section padding must not leak into mobile review marquee").toBe(0);
			expect(result.quotes.paddingBottom, "global section padding must not leak into mobile review marquee").toBe(0);
			expect(result.maxCardWidth, "mobile review cards should stay narrower than the viewport").toBeLessThanOrEqual(270);
			expect(result.maxCardHeight, "mobile review cards should stay compact").toBeLessThanOrEqual(240);
			expect(result.card.paddingLeft, "mobile review card horizontal padding should stay tight").toBeLessThanOrEqual(17);
			expect(result.card.paddingRight, "mobile review card horizontal padding should stay tight").toBeLessThanOrEqual(17);
		});
	});

	test.describe("homepage client crawl banner", () => {
		for (const viewport of [
			{ name: "mobile", width: 375, height: 900 },
			{ name: "desktop", width: 1366, height: 900 },
		]) {
			test(`trusted-business crawl moves and stays full-stage on ${viewport.name}`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				await page.emulateMedia({ reducedMotion: "no-preference" });
				const response = await gotoAndSettle(page, "/");
				await expectSuccessfulResponse(response, "/");
				await page.waitForFunction(() => document.documentElement.dataset.ltCrawlSpeed === "synced", null, { timeout: 5000 });

				const before = await page.evaluate(() => {
					const reviewTrack = document.querySelector(".lt-reviews-block__track");
					const track = document.querySelector(".lt-crawl__track");
					const viewport = document.querySelector(".lt-crawl__viewport");
					const items = Array.from(document.querySelectorAll(".lt-crawl__item")).slice(0, 6);
					const reviewMatrix = new DOMMatrixReadOnly(window.getComputedStyle(reviewTrack).transform);
					const matrix = new DOMMatrixReadOnly(window.getComputedStyle(track).transform);
					const tops = items.map((item) => Math.round(item.getBoundingClientRect().top));
					const rect = viewport.getBoundingClientRect();
					return {
						reviewX: reviewMatrix.m41,
						x: matrix.m41,
						topDelta: Math.max(...tops) - Math.min(...tops),
						itemCount: items.length,
						bannerLeft: rect.left,
						bannerRight: rect.right,
						overflowX: window.getComputedStyle(viewport).overflowX,
						animationName: window.getComputedStyle(track).animationName,
						animationDuration: window.getComputedStyle(track).animationDuration,
					};
				});

				await page.waitForTimeout(1200);

				const after = await page.evaluate(() => {
					const reviewTrack = document.querySelector(".lt-reviews-block__track");
					const track = document.querySelector(".lt-crawl__track");
					const reviewMatrix = new DOMMatrixReadOnly(window.getComputedStyle(reviewTrack).transform);
					const matrix = new DOMMatrixReadOnly(window.getComputedStyle(track).transform);
					return { reviewX: reviewMatrix.m41, x: matrix.m41 };
				});
				const reviewDelta = after.reviewX - before.reviewX;
				const crawlDelta = after.x - before.x;

				expect(before.itemCount).toBeGreaterThanOrEqual(6);
				expect(before.animationName).toBe("lt-crawl-scroll");
				expect(before.topDelta, "trusted-business names should share one horizontal row").toBeLessThanOrEqual(1);
				expect(Math.round(before.bannerLeft), "trusted-business banner should start at the viewport edge").toBeLessThanOrEqual(1);
				expect(Math.round(before.bannerRight), "trusted-business banner should reach the viewport edge").toBeGreaterThanOrEqual(viewport.width - 1);
				expect(before.overflowX).toBe("hidden");
				expect(crawlDelta, "trusted-business track should move left-to-right like review cards").toBeGreaterThan(0);
				expect(Math.abs(Math.abs(crawlDelta) - Math.abs(reviewDelta)), "trusted-business crawl should match review-card pixel speed").toBeLessThanOrEqual(2.5);
			});
		}
	});

	test("homepage reduced motion keeps proof crawls moving without scrollbars", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await page.emulateMedia({ reducedMotion: "reduce" });
		const response = await gotoAndSettle(page, "/");
		await expectSuccessfulResponse(response, "/");
		await page.waitForFunction(() => document.documentElement.dataset.ltCrawlSpeed === "synced", null, { timeout: 5000 });

		const before = await page.evaluate(() => {
			function transformX(value) {
				if (!value || value === "none") return 0;
				return new DOMMatrixReadOnly(value).m41;
			}
			function animation(selector) {
				const element = document.querySelector(selector);
				if (!element) return null;
				const style = window.getComputedStyle(element);
				return {
					animationName: style.animationName,
					animationDuration: style.animationDuration,
					x: transformX(style.transform),
				};
			}
			function banner(selector) {
				const element = document.querySelector(selector);
				const style = window.getComputedStyle(element);
				const rect = element.getBoundingClientRect();
				return {
					left: rect.left,
					right: rect.right,
					overflowX: style.overflowX,
					width: rect.width,
				};
			}
			function rowDelta(selector) {
				const items = Array.from(document.querySelectorAll(selector)).slice(0, 4);
				const tops = items.map((item) => Math.round(item.getBoundingClientRect().top));
				return {
					count: items.length,
					topDelta: Math.max(...tops) - Math.min(...tops),
				};
			}
			return {
				hero: animation(".lt-hero__title"),
				reviews: animation(".lt-reviews-block__track"),
				crawl: animation(".lt-crawl__track"),
				reviewBanner: banner(".lt-reviews-block__quotes"),
				clientBanner: banner(".lt-crawl__viewport"),
				reviewRow: rowDelta(".lt-reviews-block__quote"),
				clientRow: rowDelta(".lt-crawl__item"),
			};
		});

		await page.waitForTimeout(1200);

		const after = await page.evaluate(() => {
			function transformX(value) {
				if (!value || value === "none") return 0;
				return new DOMMatrixReadOnly(value).m41;
			}
			function x(selector) {
				const element = document.querySelector(selector);
				return transformX(window.getComputedStyle(element).transform);
			}
			return {
				reviewsX: x(".lt-reviews-block__track"),
				crawlX: x(".lt-crawl__track"),
			};
		});

		const reviewDelta = after.reviewsX - before.reviews.x;
		const crawlDelta = after.crawlX - before.crawl.x;
		expect(before.hero && before.hero.animationName).toBe("none");
		expect(before.reviews && before.reviews.animationName).toBe("lt-reviews-scroll");
		expect(before.reviews && before.reviews.animationDuration).toBe("540s");
		expect(before.crawl && before.crawl.animationName).toBe("lt-crawl-scroll");
		expect(before.reviewRow.count).toBeGreaterThanOrEqual(4);
		expect(before.clientRow.count).toBeGreaterThanOrEqual(4);
		expect(before.reviewRow.topDelta, "review cards should not stack in reduced-motion environments").toBeLessThanOrEqual(1);
		expect(before.clientRow.topDelta, "client names should not stack in reduced-motion environments").toBeLessThanOrEqual(1);
		expect(Math.round(before.reviewBanner.left), "review banner should start at the viewport edge").toBeLessThanOrEqual(1);
		expect(Math.round(before.reviewBanner.right), "review banner should reach the viewport edge").toBeGreaterThanOrEqual(389);
		expect(Math.round(before.clientBanner.left), "client banner should start at the viewport edge").toBeLessThanOrEqual(1);
		expect(Math.round(before.clientBanner.right), "client banner should reach the viewport edge").toBeGreaterThanOrEqual(389);
		expect(before.reviewBanner.overflowX).toBe("hidden");
		expect(before.clientBanner.overflowX).toBe("hidden");
		expect(reviewDelta, "review track should continue left-to-right in reduced-motion mode").toBeGreaterThan(0);
		expect(crawlDelta, "client track should continue left-to-right in reduced-motion mode").toBeGreaterThan(0);
		expect(Math.abs(Math.abs(crawlDelta) - Math.abs(reviewDelta)), "client crawl should match review-card speed in reduced-motion mode").toBeLessThanOrEqual(2.5);
	});

	test("homepage leads with Google review proof immediately after the hero", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 900 });
		const response = await gotoAndSettle(page, "/");
		await expectSuccessfulResponse(response, "/");

		const result = await page.evaluate(() => {
			const hero = document.querySelector(".lt-hero");
			const featured = document.querySelector(".lt-featured");
			const reviews = document.querySelector(".lt-reviews-block");
			const heroNext = hero ? hero.nextElementSibling : null;
			const authorityCount = document.querySelectorAll(".lt-authority").length;
			const authorityIconCount = document.querySelectorAll(".lt-authority__icon").length;
			const badge = document.querySelector(".lt-reviews-block__badge");
			const ctaBody = document.querySelector(".lt-cta__body");
			return {
				heroBottom: hero.getBoundingClientRect().bottom + window.scrollY,
				featuredTop: featured.getBoundingClientRect().top + window.scrollY,
				reviewsTop: reviews.getBoundingClientRect().top + window.scrollY,
				heroNextIsReviews: heroNext ? heroNext.classList.contains("lt-reviews-block") : false,
				authorityCount,
				authorityIconCount,
				badgeText: badge ? badge.innerText.replace(/\s+/g, " ").trim() : "",
				ctaText: ctaBody ? ctaBody.innerText.replace(/\s+/g, " ").trim() : "",
			};
		});

		expect(result.heroNextIsReviews, "Google reviews should be the first homepage band after the hero").toBe(true);
		expect(result.reviewsTop, "Google reviews should start after the hero").toBeGreaterThanOrEqual(result.heroBottom - 1);
		expect(result.reviewsTop, "Google review proof should appear before the installed-work proof band").toBeLessThan(result.featuredTop);
		expect(result.authorityCount, "homepage should not render a trust/authority bar right now").toBe(0);
		expect(result.authorityIconCount, "trust bar icons should stay as assets, not render as a homepage bar").toBe(0);
		expect(result.badgeText, "the first post-hero proof band should be clearly Google reviews").toMatch(/Google reviews/i);
		expect(result.ctaText, "closing CTA should lead with corporate, school, civic, and community work").toMatch(/corporate, school, civic, and community/i);
		expect(result.ctaText, "closing CTA should keep private celebrations secondary").toMatch(/private celebrations/i);
	});

	test("homepage installed-work proof uses a wide custom-install gallery", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 900 });
		const response = await gotoAndSettle(page, "/");
		await expectSuccessfulResponse(response, "/");

		const result = await page.evaluate(() => {
			const featured = document.querySelector(".lt-featured");
			const inner = document.querySelector(".lt-featured__inner");
			const heading = document.querySelector(".lt-featured__heading");
			const grid = document.querySelector(".lt-featured__grid");
			const cards = Array.from(document.querySelectorAll(".lt-featured__card"));
			const images = Array.from(document.querySelectorAll(".lt-featured__image"));
			const rect = (el) => {
				if (!el) return null;
				const r = el.getBoundingClientRect();
				return { left: Math.round(r.left), right: Math.round(r.right), width: Math.round(r.width), height: Math.round(r.height) };
			};
			const gridStyle = grid ? window.getComputedStyle(grid) : null;
			return {
				headingText: heading ? heading.textContent.trim() : "",
				featured: rect(featured),
				inner: rect(inner),
				grid: rect(grid),
				cardRects: cards.map(rect),
				imageRects: images.map(rect),
				gridColumnCount: gridStyle ? gridStyle.gridTemplateColumns.split(" ").filter(Boolean).length : 0,
				gridGap: gridStyle ? Number.parseFloat(gridStyle.columnGap) : null,
				documentOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
			};
		});

		expect(result.headingText).toBe("One of a Kind Designs");
		expect(result.inner.width, "featured work should use the visual proof width instead of the narrow reading max").toBeGreaterThanOrEqual(1300);
		expect(result.gridColumnCount, "featured work should remain a three-photo desktop row").toBe(3);
		expect(Math.max(...result.cardRects.map((card) => card.width)), "featured cards should stretch wider than the old cramped cards").toBeGreaterThanOrEqual(420);
		expect(result.gridGap, "featured gallery gap should be restrained").toBeLessThanOrEqual(24);
		expect(result.imageRects.every((image) => image.height < image.width), "featured images should use landscape installation crops").toBe(true);
		expect(Math.abs(result.documentOverflow), "wide featured gallery should not create document overflow").toBeLessThanOrEqual(1);
	});

	test("homepage hero uses one visible stable headline", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 900 });
		await page.emulateMedia({ reducedMotion: "no-preference" });
		const response = await gotoAndSettle(page, "/");
		await expectSuccessfulResponse(response, "/");

		const result = await page.evaluate(() => {
			const headings = Array.from(document.querySelectorAll("h1"));
			const heroTitle = document.querySelector(".lt-hero__title");
			const heroImage = document.querySelector(".lt-hero__image");
			const reviews = document.querySelector(".lt-reviews-block");
			const titleStyle = heroTitle ? window.getComputedStyle(heroTitle) : null;
			const heroImageStyle = heroImage ? window.getComputedStyle(heroImage) : null;
			const titleRect = heroTitle ? heroTitle.getBoundingClientRect() : null;
			const reviewsRect = reviews ? reviews.getBoundingClientRect() : null;
			return {
				h1Count: headings.length,
				h1Text: headings.map((heading) => heading.innerText.trim()),
				heroTitleText: heroTitle ? heroTitle.innerText.trim() : "",
				titleVisible: Boolean(titleRect && titleRect.width > 0 && titleRect.height > 0 && titleStyle.display !== "none" && titleStyle.visibility !== "hidden"),
				animationName: titleStyle ? titleStyle.animationName : null,
				heroImage: heroImageStyle ? heroImageStyle.backgroundImage : "",
				cyclingCount: document.querySelectorAll(".lt-hero__cycling .lt-hero__title").length,
				nextBandTop: reviewsRect ? reviewsRect.top : Number.POSITIVE_INFINITY,
				viewportHeight: window.innerHeight,
			};
		});

		expect(result.h1Count, "homepage should expose exactly one page-level H1").toBe(1);
		expect(result.h1Text[0], "homepage H1 should be the visible hero headline").toBe(result.heroTitleText);
		expect(result.titleVisible, "homepage H1 should be visible, not screen-reader-only").toBe(true);
		expect(result.animationName, "homepage H1 should not rotate or fade").toBe("none");
		expect(result.heroImage, "homepage hero should prove a real balloon install, not only a scenic Utah background").toContain("corporate-weberstock-photo-opt.webp");
		expect(result.cyclingCount, "homepage should not render hidden rotating H2/H1 headline copies").toBe(0);
		expect(result.nextBandTop, "desktop first viewport should show the next band below the hero").toBeLessThan(result.viewportHeight - 16);
	});

	test("small mobile homepage hero leaves a next-band hint without hiding CTAs", async ({ page }) => {
		await page.setViewportSize({ width: 320, height: 700 });
		const response = await gotoAndSettle(page, "/");
		await expectSuccessfulResponse(response, "/");

		const result = await page.evaluate(() => {
			const reviews = document.querySelector(".lt-reviews-block");
			const cookie = document.querySelector(".lt-cookie-consent");
			const buttons = Array.from(document.querySelectorAll(".lt-hero__cta"));
			const reviewsRect = reviews ? reviews.getBoundingClientRect() : null;
			const cookieRect = cookie ? cookie.getBoundingClientRect() : null;
			return {
				reviewsTop: reviewsRect ? reviewsRect.top : null,
				cookieTop: cookieRect ? cookieRect.top : null,
				viewportHeight: window.innerHeight,
				buttonBottoms: buttons.map((button) => button.getBoundingClientRect().bottom),
				buttonCount: buttons.length,
			};
		});

		expect(result.buttonCount, "small mobile homepage should keep both hero CTAs visible").toBe(2);
		expect(Math.max(...result.buttonBottoms), "small mobile hero CTAs should fit before the Google reviews band").toBeLessThan(result.reviewsTop);
		expect(result.reviewsTop, "small mobile first viewport should show the Google reviews band hint").toBeLessThan(result.viewportHeight - 16);
		expect(result.cookieTop, "homepage cookie notice should sit after the Google reviews band").toBeGreaterThan(result.reviewsTop);
	});

	for (const viewport of [
		{ name: "320", width: 320, height: 700 },
		{ name: "375", width: 375, height: 812 },
	]) {
		test(`mobile cookie notice does not cover hero CTAs at ${viewport.name}px`, async ({ page }) => {
			await page.setViewportSize({ width: viewport.width, height: viewport.height });
			const response = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(response, "/");

			const result = await page.evaluate(() => {
				const notice = document.querySelector(".lt-cookie-consent");
				const buttons = Array.from(document.querySelectorAll(".lt-hero__cta"));
				function rect(element) {
					const box = element.getBoundingClientRect();
					return {
						top: box.top,
						right: box.right,
						bottom: box.bottom,
						left: box.left,
					};
				}
				function overlaps(a, b) {
					return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
				}
				const noticeRect = rect(notice);
				return buttons.map((button) => ({
					text: button.innerText.trim(),
					overlap: overlaps(noticeRect, rect(button)),
				}));
			});

			expect(result, "homepage should render hero buttons").toHaveLength(2);
			expect(result.filter((item) => item.overlap), "cookie notice should not cover either hero button").toHaveLength(0);
		});
	}

	test("desktop homepage cookie notice is an inline band instead of a floating overlay", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 900 });
		const response = await gotoAndSettle(page, "/");
		await expectSuccessfulResponse(response, "/");

		const result = await page.evaluate(() => {
			const notice = document.querySelector(".lt-cookie-consent");
			const previous = notice && notice.previousElementSibling;
			const style = notice && window.getComputedStyle(notice);
			const rect = notice && notice.getBoundingClientRect();
			return {
				hasNotice: Boolean(notice),
				isInline: notice ? notice.classList.contains("lt-cookie-consent--inline") : false,
				position: style ? style.position : null,
				previousIsReviews: previous ? previous.classList.contains("lt-reviews-block") : false,
				left: rect ? rect.left : null,
				right: rect ? rect.right : null,
			};
		});

		expect(result.hasNotice, "homepage should render the cookie notice when no choice is stored").toBe(true);
		expect(result.isInline, "desktop homepage cookie notice should use the same inline document band as mobile").toBe(true);
		expect(result.position, "inline homepage cookie notice should not float over content").not.toBe("fixed");
		expect(result.previousIsReviews, "inline homepage cookie notice should sit after the Google review proof band").toBe(true);
		expect(Math.round(result.left), "inline cookie band should start at the viewport edge").toBeLessThanOrEqual(1);
		expect(Math.round(result.right), "inline cookie band should reach the viewport edge").toBeGreaterThanOrEqual(1365);
	});
});
