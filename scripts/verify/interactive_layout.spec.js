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

const PLATFORM_WORDS = /\b(?:ERPNext|Frappe|Odoo)\b/i;
const DESK_USER = process.env.LT_DESK_TEST_USER;
const DESK_PASSWORD = process.env.LT_DESK_TEST_PASSWORD;

const COMPACT_HERO_VIEWPORTS = [
	{ name: "mobile", width: 390, height: 844, expectedHeight: 220, maxPadding: 24, maxTitle: 32, imageKey: "mobile" },
	{ name: "tablet", width: 820, height: 1180, expectedHeight: 250, maxPadding: 28, maxTitle: 40, imageKey: "tablet" },
	{ name: "desktop", width: 1366, height: 768, expectedHeight: 280, maxPadding: 32, maxTitle: 44, imageKey: "desktop" },
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
		name: "about",
		path: "/about",
		heroSelector: ".lt-about__hero",
		contentSelector: ".lt-about__hero-inner",
		titleSelector: ".lt-about__hero h1",
	},
	{
		name: "faq",
		path: "/faq",
		heroSelector: ".lt-faq__hero",
		contentSelector: ".lt-faq__hero-inner",
		titleSelector: ".lt-faq__hero h1",
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

async function loginThroughApi(page) {
	await page.goto(new URL("/login", BASE_URL).toString(), { waitUntil: "domcontentloaded" });
	const result = await page.evaluate(
		async ({ user, password }) => {
			const response = await fetch("/api/method/login", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Requested-With": "XMLHttpRequest",
				},
				body: JSON.stringify({ usr: user, pwd: password }),
			});
			return { status: response.status, body: await response.text() };
		},
		{ user: DESK_USER, password: DESK_PASSWORD },
	);
	expect(result.status, result.body).toBe(200);
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

		for (const viewport of COMPACT_HERO_VIEWPORTS) {
			for (const route of COMPACT_HERO_ROUTES) {
				test(`${route.name} hero uses a generated lifestyle crop and black readability overlay at ${viewport.name}`, async ({ page }) => {
					await page.setViewportSize({ width: viewport.width, height: viewport.height });
					const response = await gotoAndSettle(page, route.path);
					await expectSuccessfulResponse(response, route.path);

					const result = await page.evaluate(({ route }) => {
						const hero = document.querySelector(route.heroSelector);
						if (!hero) return { found: false };
						const before = window.getComputedStyle(hero, "::before");
						const after = window.getComputedStyle(hero, "::after");
						const nestedImage = hero.querySelector(".lt-hero__image");
						const nestedImageStyle = nestedImage ? window.getComputedStyle(nestedImage) : null;
						const heroStyle = window.getComputedStyle(hero);
						const photoBackground = [
							before.backgroundImage,
							nestedImageStyle ? nestedImageStyle.backgroundImage : "",
							heroStyle.backgroundImage,
						].find((value) => value && value !== "none") || "";
						return {
							found: true,
							photoBackground,
							beforeZ: before.zIndex,
							afterBackground: after.backgroundImage,
							afterZ: after.zIndex,
						};
					}, { route });

					expect(result.found, `${route.path} should expose the named hero contract element`).toBe(true);
					expect(result.photoBackground, `${route.path} hero should use a generated responsive lifestyle photo layer`).toContain(`generated-lifestyle-${viewport.imageKey}.webp`);
					expect(result.afterBackground, `${route.path} hero should include the landing-page-style black readability overlay`).toContain("rgba(10, 10, 11");
					expect(Number.parseInt(result.afterZ, 10), `${route.path} overlay should sit above the image layer`).toBeGreaterThan(Number.parseInt(result.beforeZ || "0", 10));
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

			for (const trigger of ["lt-mega-events"]) {
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
			for (const panel of ["lt-mobile-events"]) {
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

		test("logged-in public header exposes logout and clears the session", async ({ page }) => {
			test.skip(!DESK_USER || !DESK_PASSWORD, "Set LT_DESK_TEST_USER and LT_DESK_TEST_PASSWORD.");
			await loginThroughApi(page);

			await page.setViewportSize({ width: 1366, height: 900 });
			const blockedResponse = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(blockedResponse, "/");
			await expect(page.locator("[data-lt-portal-access-blocked]")).toBeVisible();
			await expect(page.locator("[data-lt-portal-access-blocked]").getByRole("link", { name: /Log Out/i }).first()).toBeVisible();

			const desktopResponse = await gotoAndSettle(page, "/home");
			await expectSuccessfulResponse(desktopResponse, "/home");
			await expect(page.locator("body")).toHaveAttribute("frappe-session-status", "logged-in");
			await expect(page.locator(".lt-mega-header__top-links").getByRole("link", { name: /My Account/i })).toBeVisible();
			await expect(page.locator(".lt-mega-header__top-links").getByRole("link", { name: /Log Out/i })).toHaveAttribute("href", "/?cmd=web_logout");

			await page.setViewportSize({ width: 390, height: 844 });
			const mobileResponse = await gotoAndSettle(page, "/home");
			await expectSuccessfulResponse(mobileResponse, "/home");
			await dismissCookieNotice(page);
			await page.locator("#lt-mobile-toggle").click();
			await expect(page.locator("#lt-mobile-nav")).toBeVisible();
			const mobileLogout = page.locator("#lt-mobile-nav").getByRole("link", { name: /Log Out/i });
			await expect(mobileLogout).toBeVisible();
			await mobileLogout.click();
			await page.waitForLoadState("networkidle");

			const loggedOutResponse = await gotoAndSettle(page, "/home");
			await expectSuccessfulResponse(loggedOutResponse, "/home");
			await expect(page.locator("body")).toHaveAttribute("frappe-session-status", "logged-out");
			await page.locator("#lt-mobile-toggle").click();
			await expect(page.locator("#lt-mobile-nav").getByRole("link", { name: /Sign In/i })).toBeVisible();
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
					targetSelectors: [".lt-mega-header__mobile-action", ".lt-mega-header__search", ".lt-mega-header__cta"],
				});
				expectNoLayoutFailures(expect, result, `header at ${viewport.name}px`);
			});
		}

		test("small mobile header keeps logo clear of menu controls", async ({ page }) => {
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
			expect(result.mobileActionCount, "mobile header should only carry the menu control").toBe(1);
			expect(result.mobileSearchCount, "mobile search belongs at the bottom of the drawer").toBe(0);
			expect(result.logoRight, "logo should not collide with menu controls").toBeLessThanOrEqual(result.actionsLeft - 8);
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

				await page.locator("#lt-site-search-input").fill("portfolio");
				await expect(page.locator("#lt-site-search-panel a[href='/portfolio']")).toBeVisible();
				await expect(page.locator("#lt-site-search-panel a[href='/event-balloons']")).toBeHidden();

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

		test("search query submits to the active commerce/search lane", async ({ page }) => {
			await page.setViewportSize({ width: 1366, height: 768 });
			const response = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(response, "/");

			await page.locator(".lt-mega-header__search").click();
			const formAction = await page.locator("#lt-site-search-panel form").getAttribute("action");
			await page.locator("#lt-site-search-input").fill("balloons");
			await Promise.all([page.waitForURL(new RegExp(`${formAction}\\?q=balloons$`)), page.keyboard.press("Enter")]);
			await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});

			if (formAction === "/shop") {
				await expect(page.locator(".lt-shop--landing")).toBeVisible();
			} else {
				await expect(page.locator(".lt-contact__intro h1")).toBeVisible();
			}
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
			for (const trigger of ["lt-mega-events"]) {
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

				for (const panel of ["lt-mobile-events"]) {
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

	test.describe("configured ecommerce states", () => {
		for (const viewport of [
			{ name: "320", width: 320, height: 812 },
			{ name: "390", width: 390, height: 844 },
			{ name: "820", width: 820, height: 1180 },
			{ name: "1200", width: 1200, height: 900 },
		]) {
			for (const path of ["/shop", "/shop-items/bouquets/unicorn-bouquet", "/cart", "/checkout"]) {
				test(`${path} configured commerce page fits at ${viewport.name}px`, async ({ page }) => {
					await page.setViewportSize({ width: viewport.width, height: viewport.height });
					const response = await gotoAndSettle(page, path);
					await expectSuccessfulResponse(response, path);
					const isPaused = page.url().includes("/ready-to-order-paused");
					if (isPaused) {
						await expect(page.locator(".lt-ecommerce-paused__title")).toContainText("Ready-to-order is paused.");
					} else {
						await expect(page.locator("body")).not.toContainText("Ready-to-order is paused");
					}

					const result = isPaused
						? await auditPageLayout(page, {
								containerSelectors: [".lt-ecommerce-paused", ".lt-ecommerce-paused__inner"],
								targetSelectors: [".lt-ecommerce-paused__button", ".lt-ecommerce-paused__help a"],
							})
						: await auditPageLayout(page);
					expectNoLayoutFailures(expect, result, `${path} configured commerce page at ${viewport.name}px`);
				});
			}
		}
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

		test("review cards keep all curated Google quotes and five-star rows in both marquee copies", async ({ page }) => {
			await page.setViewportSize({ width: 1366, height: 900 });
			const response = await gotoAndSettle(page, "/");
			await expectSuccessfulResponse(response, "/");

			const result = await page.evaluate(() => {
				const groups = Array.from(document.querySelectorAll(".lt-reviews-block__group"));
				const cards = Array.from(document.querySelectorAll("[data-lt-review-card]"));
				const text = (card, selector) => (card.querySelector(selector)?.textContent || "").replace(/\s+/g, " ").trim();
				const compactStars = (card) => text(card, ".lt-reviews-block__quote-stars").replace(/\s+/g, "");
				const starCount = (card) => Array.from(compactStars(card)).filter((character) => character.charCodeAt(0) === 9733).length;
				const cardInfo = (card, index) => {
					const rect = card.getBoundingClientRect();
					return {
						index,
						text: text(card, ".lt-reviews-block__quote-text"),
						stars: compactStars(card),
						starCount: starCount(card),
						starLabel: card.querySelector(".lt-reviews-block__quote-stars")?.getAttribute("aria-label") || "",
						rating: card.getAttribute("data-lt-review-rating") || "",
						visible: rect.left < window.innerWidth && rect.right > 0,
					};
				};
				const infos = cards.map(cardInfo);
				const groupTexts = groups.map((group) =>
					Array.from(group.querySelectorAll("[data-lt-review-card]")).map((card) => text(card, ".lt-reviews-block__quote-text"))
				);

				return {
					groupCount: groups.length,
					groupSizes: groups.map((group) => group.querySelectorAll("[data-lt-review-card]").length),
					uniqueReviewCount: new Set(infos.map((card) => card.text)).size,
					emptyCards: infos.filter((card) => !card.text).map((card) => card.index),
					pendingCards: infos.filter((card) => /pending/i.test(card.text)).map((card) => card.index),
					missingStarCards: infos.filter((card) => card.starCount !== 5 || card.stars.length !== 5 || card.starLabel !== "5 out of 5 stars").map((card) => card.index),
					nonFiveRatingCards: infos.filter((card) => card.rating !== "5").map((card) => card.index),
					visibleCount: infos.filter((card) => card.visible).length,
					visibleMissingStarCards: infos.filter((card) => card.visible && card.starCount !== 5).map((card) => card.index),
					duplicateMatchesSource: JSON.stringify(groupTexts[0] || []) === JSON.stringify(groupTexts[1] || []),
				};
			});

			expect(result.groupCount, "review marquee should have one readable copy and one duplicate copy").toBe(2);
			expect(result.groupSizes[0], "homepage should preserve the curated Google review set").toBeGreaterThanOrEqual(19);
			expect(result.groupSizes[1], "duplicate marquee copy should include every source review").toBe(result.groupSizes[0]);
			expect(result.uniqueReviewCount, "review copy should not silently disappear").toBeGreaterThanOrEqual(19);
			expect(result.duplicateMatchesSource, "marquee duplicate should match the readable review copy").toBe(true);
			expect(result.emptyCards, "review cards must not render empty text").toEqual([]);
			expect(result.pendingCards, "homepage must not show placeholder review cards").toEqual([]);
			expect(result.nonFiveRatingCards, "homepage review cards should only use five-star reviews").toEqual([]);
			expect(result.missingStarCards, "every rendered review card should show the five-star row").toEqual([]);
			expect(result.visibleCount, "the review crawl should show several cards at load").toBeGreaterThanOrEqual(3);
			expect(result.visibleMissingStarCards, "visible review cards should not be the starless duplicate copy").toEqual([]);
		});

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
						gap: parseFloat(style.gap) || 0,
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
					group: box(".lt-reviews-block__group"),
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
			expect(result.group.gap, "mobile review card gap should stay tight").toBeLessThanOrEqual(9);
			expect(result.maxCardWidth, "mobile review cards should stay narrower than the viewport").toBeLessThanOrEqual(255);
			expect(result.maxCardHeight, "mobile review cards should stay compact").toBeLessThanOrEqual(240);
			expect(result.card.paddingLeft, "mobile review card horizontal padding should stay tight").toBeLessThanOrEqual(17);
			expect(result.card.paddingRight, "mobile review card horizontal padding should stay tight").toBeLessThanOrEqual(17);
		});

		test("desktop review proof spacing stays compact", async ({ page }) => {
			await page.setViewportSize({ width: 1366, height: 900 });
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
						gap: parseFloat(style.gap) || 0,
						marginBottom: parseFloat(style.marginBottom) || 0,
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
					group: box(".lt-reviews-block__group"),
					maxCardHeight: Math.max(...cards.map((card) => card.height)),
					maxCardWidth: Math.max(...cards.map((card) => card.width)),
				};
			});

			expect(result.block, "reviews block should render").not.toBeNull();
			expect(result.block.height, "desktop Google review section should stay compact").toBeLessThanOrEqual(475);
			expect(result.block.paddingTop, "desktop review section top padding should stay tight").toBeLessThanOrEqual(36);
			expect(result.block.paddingBottom, "desktop review section bottom padding should stay tight").toBeLessThanOrEqual(40);
			expect(result.badge.marginBottom, "desktop badge-to-cards spacing should stay tight").toBeLessThanOrEqual(18);
			expect(result.quotes.paddingTop, "global section padding must not leak into desktop review marquee").toBe(0);
			expect(result.quotes.paddingBottom, "global section padding must not leak into desktop review marquee").toBe(0);
			expect(result.group.gap, "desktop review card gap should stay tight").toBeLessThanOrEqual(12);
			expect(result.maxCardWidth, "desktop review cards should stay compact").toBeLessThanOrEqual(300);
			expect(result.maxCardHeight, "desktop review cards should not stretch short reviews into blank cards").toBeLessThanOrEqual(245);
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
			let heroNext = hero ? hero.nextElementSibling : null;
			while (heroNext && ["SCRIPT", "STYLE", "TEMPLATE"].includes(heroNext.tagName)) {
				heroNext = heroNext.nextElementSibling;
			}
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

	test("twisting and face painting inquiry starts with no service checkbox selected", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		const response = await gotoAndSettle(page, "/balloon-twisting-and-face-painting");
		await expectSuccessfulResponse(response, "/balloon-twisting-and-face-painting");

		const checkedServices = await page.locator('input[name="x_services"]:checked').evaluateAll((inputs) => inputs.map((input) => input.value));
		expect(checkedServices, "BTFP booking form should let the visitor choose services from a blank state").toEqual([]);
	});

	test("twisting and face painting service photos expose working carousels", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await page.emulateMedia({ reducedMotion: "reduce" });
		const response = await gotoAndSettle(page, "/balloon-twisting-and-face-painting");
		await expectSuccessfulResponse(response, "/balloon-twisting-and-face-painting");

		const carousels = page.locator("[data-btfp-carousel]");
		await expect(carousels).toHaveCount(2);
		await expect(carousels.first().locator(".lt-btfp__carousel-img")).toHaveCount(10);
		await expect(carousels.nth(1).locator(".lt-btfp__carousel-img")).toHaveCount(10);

		await expect(carousels.first().locator("[data-btfp-carousel-status]")).toHaveText("1 / 10");
		await carousels.first().locator("[data-btfp-carousel-next]").click();
		await expect(carousels.first().locator("[data-btfp-carousel-status]")).toHaveText("2 / 10");
	});

	test("twisting and face painting event crawl replaces the short-notice band and keeps moving", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 768 });
		await page.emulateMedia({ reducedMotion: "no-preference" });
		const response = await gotoAndSettle(page, "/balloon-twisting-and-face-painting");
		await expectSuccessfulResponse(response, "/balloon-twisting-and-face-painting");

		const contract = await page.evaluate(() => {
			const crawl = document.querySelector(".lt-btfp__event-crawl");
			const oldCopy = document.body.innerText.includes("Need help on short notice?") || document.body.innerText.includes("Give us a call or send a message");
			const events = Array.from(document.querySelectorAll(".lt-btfp__event-crawl-group:first-child .lt-btfp__event-crawl-item")).map((node) => node.textContent.trim());
			const track = document.querySelector(".lt-btfp__event-crawl-track");
			const style = track ? window.getComputedStyle(track) : null;
			return {
				oldBannerCount: document.querySelectorAll(".lt-btfp__banner").length,
				oldCopy,
				previousClass: crawl?.previousElementSibling?.className || "",
				nextClass: crawl?.nextElementSibling?.className || "",
				events,
				viewportOverflowX: crawl ? window.getComputedStyle(crawl.querySelector(".lt-btfp__event-crawl-viewport")).overflowX : null,
				animationName: style?.animationName || "",
				animationPlayState: style?.animationPlayState || "",
				animationIterationCount: style?.animationIterationCount || "",
			};
		});

		expect(contract.oldBannerCount, "old short-notice contact band should be removed").toBe(0);
		expect(contract.oldCopy, "old short-notice contact copy should not remain on the route").toBe(false);
		expect(contract.previousClass, "event crawl should sit directly after the BTFP hero").toContain("lt-btfp__intro");
		expect(contract.nextClass, "event crawl should sit before the service cards in the old banner slot").toContain("lt-btfp__services");
		expect(contract.events.length, "event crawl should include a fuller BTFP event suggestion set").toBeGreaterThanOrEqual(16);
		for (const eventName of ["Birthday Parties", "School Carnivals", "Company Picnics", "Library Programs", "City Celebrations", "Trunk-or-Treats"]) {
			expect(contract.events, `event crawl should include ${eventName}`).toContain(eventName);
		}
		expect(contract.viewportOverflowX).toBe("hidden");
		expect(contract.animationName).toBe("lt-btfp-event-crawl-scroll");
		expect(contract.animationPlayState).toBe("running");
		expect(contract.animationIterationCount).toBe("infinite");

		const sampleCrawl = async () => page.evaluate(() => {
			const track = document.querySelector(".lt-btfp__event-crawl-track");
			if (!track) return null;
			const style = window.getComputedStyle(track);
			const matrix = new DOMMatrixReadOnly(style.transform);
			return {
				x: matrix.m41,
				animationPlayState: style.animationPlayState,
				animationIterationCount: style.animationIterationCount,
			};
		});

		const first = await sampleCrawl();
		await page.waitForTimeout(700);
		const second = await sampleCrawl();
		expect(first).not.toBeNull();
		expect(second).not.toBeNull();
		expect(second.x - first.x, "crawl should keep moving left-to-right after page load").toBeGreaterThan(0);

		await page.locator(".lt-btfp__event-crawl").hover();
		const hoverStart = await sampleCrawl();
		await page.waitForTimeout(700);
		const hoverEnd = await sampleCrawl();
		expect(hoverStart.animationPlayState).toBe("running");
		expect(hoverEnd.animationPlayState).toBe("running");
		expect(hoverEnd.x - hoverStart.x, "crawl should not pause on hover").toBeGreaterThan(0);

		await page.evaluate(() => {
			const track = document.querySelector(".lt-btfp__event-crawl-track");
			track?.setAttribute("tabindex", "-1");
			track?.focus();
		});
		const focusStart = await sampleCrawl();
		await page.waitForTimeout(700);
		const focusEnd = await sampleCrawl();
		expect(focusStart.animationPlayState).toBe("running");
		expect(focusEnd.animationPlayState).toBe("running");
		expect(focusEnd.x - focusStart.x, "crawl should not pause on focus").toBeGreaterThan(0);
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
		expect(result.heroImage, "homepage hero carousel should open with the graduation-season image").toContain("school-grad-garland.webp");
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
			const buttons = Array.from(document.querySelectorAll(".lt-hero__slide:first-child .lt-hero__cta"));
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
				const buttons = Array.from(document.querySelectorAll(".lt-hero__slide--active .lt-hero__cta"));
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
