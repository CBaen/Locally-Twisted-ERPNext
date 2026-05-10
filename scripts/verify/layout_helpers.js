const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";

const EDGE_TOLERANCE_PX = 2;
const TEXT_TOLERANCE_PX = 2;

const PUBLIC_ROUTES = [
	{ name: "home", path: "/" },
	{ name: "book-alias", path: "/book" },
	{ name: "contact", path: "/contact" },
	{ name: "event-balloons", path: "/event-balloons" },
	{ name: "civic-community", path: "/civic-community" },
	{ name: "corporate-events", path: "/corporate-events" },
	{ name: "schools-campuses", path: "/schools-campuses" },
	{ name: "private-celebrations", path: "/private-celebrations" },
	{ name: "portfolio", path: "/portfolio" },
	{ name: "btfp", path: "/balloon-twisting-and-face-painting" },
	{ name: "faq", path: "/faq" },
	{ name: "privacy", path: "/privacy" },
	{ name: "terms", path: "/terms-of-service" },
	{ name: "refund-policy", path: "/refund-policy" },
	{ name: "accessibility", path: "/accessibility" },
	{ name: "ready-to-order-paused", path: "/ready-to-order-paused" },
	{ name: "shop", path: "/shop" },
	{ name: "shop-by-category", path: "/shop-by-category" },
	{ name: "variant-product", path: "/shop-items/garlands/baby-shower-garland" },
	{ name: "single-product", path: "/shop-items/seasonal-specialty/easter-balloon-cups" },
	{ name: "seasonal-category", path: "/shop-items/seasonal-specialty" },
	{ name: "cart", path: "/cart" },
	{ name: "checkout", path: "/checkout" },
	{ name: "thank-you", path: "/thank-you" },
];

const PASSIVE_VIEWPORTS = [
	{ name: "mobile-320", width: 320, height: 812 },
	{ name: "mobile-360", width: 360, height: 800 },
	{ name: "mobile-375", width: 375, height: 812 },
	{ name: "mobile-390", width: 390, height: 844 },
	{ name: "mobile-414", width: 414, height: 896 },
	{ name: "tablet-768", width: 768, height: 1024 },
	{ name: "tablet-820", width: 820, height: 1180 },
	{ name: "desktop-edge-991", width: 991, height: 900 },
	{ name: "desktop-edge-992", width: 992, height: 900 },
	{ name: "desktop-edge-1024", width: 1024, height: 768 },
	{ name: "desktop-edge-1199", width: 1199, height: 900 },
	{ name: "desktop-1200", width: 1200, height: 900 },
	{ name: "desktop-1366", width: 1366, height: 768 },
];

const HEADER_VIEWPORTS = [
	{ name: "991", width: 991, height: 900, expectedMode: "mobile" },
	{ name: "992", width: 992, height: 900, expectedMode: "mobile" },
	{ name: "1024", width: 1024, height: 768, expectedMode: "mobile" },
	{ name: "1199", width: 1199, height: 900, expectedMode: "mobile" },
	{ name: "1200", width: 1200, height: 900, expectedMode: "desktop" },
	{ name: "1280", width: 1280, height: 800, expectedMode: "desktop" },
	{ name: "1440", width: 1440, height: 900, expectedMode: "desktop" },
];

const MOBILE_DRAWER_VIEWPORTS = [
	{ name: "320", width: 320, height: 812 },
	{ name: "360", width: 360, height: 800 },
	{ name: "375", width: 375, height: 812 },
	{ name: "390", width: 390, height: 844 },
	{ name: "414", width: 414, height: 896 },
	{ name: "768", width: 768, height: 1024 },
	{ name: "991", width: 991, height: 900 },
	{ name: "992", width: 992, height: 900 },
	{ name: "1024", width: 1024, height: 768 },
	{ name: "1199", width: 1199, height: 900 },
];

const CONTAINER_CONTRACT_VIEWPORTS = [
	{ name: "mobile-320", width: 320, height: 812 },
	{ name: "tablet-820", width: 820, height: 1180 },
	{ name: "desktop-1366", width: 1366, height: 768 },
];

const PAGE_MAX = 1160;
const NARROW_MAX = 760;
const FORM_MAX = 920;
const SHOP_MAX = 1500;

const CONTACT_SURFACES = [
	{ selector: ".lt-contact__intro", mode: "band", inner: ".lt-contact__intro > .container", maxWidth: PAGE_MAX },
	{ selector: ".lt-contact", mode: "band", inner: ".lt-contact > .container", maxWidth: PAGE_MAX },
	{ selector: ".lt-contact__grid", mode: "contained", maxWidth: PAGE_MAX },
	{ selector: ".lt-locations", mode: "band", inner: ".lt-locations > .container", maxWidth: PAGE_MAX },
];

const SHOP_LANDING_SURFACES = [
	{ selector: ".lt-shop--landing", mode: "root" },
	{ selector: ".lt-shop__hero", mode: "band", inner: ".lt-shop__hero-inner", maxWidth: SHOP_MAX },
	{ selector: ".lt-shop__band", mode: "raw-band" },
	{ selector: ".lt-shop__listing", mode: "band", inner: ".lt-shop__listing-inner", maxWidth: SHOP_MAX },
	{ selector: ".lt-shop__cta", mode: "band", inner: ".lt-shop__cta-inner", maxWidth: SHOP_MAX },
];

const ECOMMERCE_PAUSED_SURFACES = [
	{ selector: ".lt-ecommerce-paused", mode: "band", inner: ".lt-ecommerce-paused__inner", maxWidth: PAGE_MAX },
];

const EVENT_TYPE_SURFACES = [
	{ selector: ".lt-authority-page", mode: "root" },
	{ selector: ".lt-authority-hero", mode: "fullbleed", inner: ".lt-authority-hero__inner", maxWidth: PAGE_MAX },
	{ selector: ".lt-authority-proof", mode: "fullbleed", inner: ".lt-authority-proof__inner", maxWidth: PAGE_MAX },
	{ selector: ".lt-authority-section", mode: "band", inner: ".lt-authority-section__inner", maxWidth: PAGE_MAX, allowMultiple: true },
	{ selector: ".lt-authority-cta", mode: "fullbleed", inner: ".lt-authority-cta__inner", maxWidth: PAGE_MAX },
];

const CONTAINER_CONTRACT_ROUTES = [
	{
		name: "home",
		path: "/",
		topLevel: [
			".lt-hero.lt-fullbleed",
			".lt-reviews-block.lt-fullbleed",
			".lt-cookie-consent.lt-cookie-consent--inline",
			".lt-featured.lt-fullbleed",
			".lt-categories.lt-fullbleed",
			".lt-divider",
			".lt-crawl.lt-fullbleed",
			".lt-cta.lt-fullbleed",
			".lt-twisting-spotlight.lt-fullbleed",
		],
		surfaces: [
			{ selector: ".lt-hero", mode: "fullbleed", inner: ".lt-hero__content", maxWidth: PAGE_MAX },
			{ selector: ".lt-reviews-block", mode: "fullbleed", inner: ".lt-reviews-block__inner", maxWidth: PAGE_MAX },
			{ selector: ".lt-reviews-block__quotes", mode: "clip", clipMustSpan: true },
			{ selector: ".lt-cookie-consent--inline", mode: "raw-band" },
			{ selector: ".lt-featured", mode: "fullbleed", inner: ".lt-featured__inner", maxWidth: 1700 },
			{
				selector: ".lt-categories",
				mode: "fullbleed",
				innerSelectors: [".lt-categories__heading", ".lt-categories__lede", ".lt-categories__grid"],
				maxWidth: 1500,
			},
			{ selector: ".lt-divider", mode: "raw-band" },
			{ selector: ".lt-crawl", mode: "fullbleed", inner: ".lt-crawl__heading", maxWidth: PAGE_MAX },
			{ selector: ".lt-crawl__viewport", mode: "clip", clipMustSpan: true },
			{ selector: ".lt-cta", mode: "fullbleed", inner: ".lt-cta__inner", maxWidth: PAGE_MAX },
			{ selector: ".lt-twisting-spotlight", mode: "fullbleed", inner: ".lt-twisting-spotlight__inner", maxWidth: PAGE_MAX },
		],
	},
	{
		name: "book-alias",
		path: "/book",
		topLevel: [".lt-contact__intro", ".lt-contact", ".lt-locations"],
		surfaces: CONTACT_SURFACES,
	},
	{
		name: "contact",
		path: "/contact",
		topLevel: [".lt-contact__intro", ".lt-contact", ".lt-locations"],
		surfaces: CONTACT_SURFACES,
	},
	{
		name: "event-balloons",
		path: "/event-balloons",
		topLevel: [".lt-authority-page"],
		surfaces: EVENT_TYPE_SURFACES,
	},
	{
		name: "civic-community",
		path: "/civic-community",
		topLevel: [".lt-authority-page.lt-event-type-page"],
		surfaces: EVENT_TYPE_SURFACES,
	},
	{
		name: "corporate-events",
		path: "/corporate-events",
		topLevel: [".lt-authority-page.lt-event-type-page"],
		surfaces: EVENT_TYPE_SURFACES,
	},
	{
		name: "schools-campuses",
		path: "/schools-campuses",
		topLevel: [".lt-authority-page.lt-event-type-page"],
		surfaces: EVENT_TYPE_SURFACES,
	},
	{
		name: "private-celebrations",
		path: "/private-celebrations",
		topLevel: [".lt-authority-page.lt-event-type-page"],
		surfaces: EVENT_TYPE_SURFACES,
	},
	{
		name: "portfolio",
		path: "/portfolio",
		topLevel: [".lt-portfolio"],
		surfaces: [
			{ selector: ".lt-portfolio", mode: "root" },
			{ selector: ".lt-portfolio__hero", mode: "fullbleed", inner: ".lt-portfolio__hero-inner", maxWidth: PAGE_MAX },
			{ selector: ".lt-reel", mode: "visual-field" },
		],
	},
	{
		name: "btfp",
		path: "/balloon-twisting-and-face-painting",
		topLevel: [
			".lt-btfp__intro",
			".lt-btfp__banner",
			".lt-btfp__services",
			".lt-btfp__event-crawl",
			".lt-btfp__booking",
		],
		surfaces: [
			{ selector: ".lt-btfp__intro", mode: "fullbleed", inner: ".lt-btfp__intro-inner", maxWidth: PAGE_MAX },
			{ selector: ".lt-btfp__banner", mode: "fullbleed", inner: ".lt-btfp__banner-inner", maxWidth: PAGE_MAX },
			{ selector: ".lt-btfp__services", mode: "band", inner: ".lt-btfp__services-grid", maxWidth: PAGE_MAX },
			{ selector: ".lt-btfp__event-crawl", mode: "fullbleed" },
			{ selector: ".lt-btfp__event-crawl-viewport", mode: "clip", clipMustSpan: true },
			{ selector: ".lt-btfp__booking", mode: "band", inner: ".lt-btfp__booking-grid", maxWidth: PAGE_MAX },
		],
	},
	{
		name: "faq",
		path: "/faq",
		topLevel: [".lt-faq"],
		surfaces: [{ selector: ".lt-faq", mode: "band", inner: ".lt-faq__inner", maxWidth: NARROW_MAX }],
	},
	{
		name: "privacy",
		path: "/privacy",
		topLevel: [".lt-policy"],
		surfaces: [{ selector: ".lt-policy", mode: "band", inner: ".lt-policy__inner", maxWidth: NARROW_MAX }],
	},
	{
		name: "terms",
		path: "/terms-of-service",
		topLevel: [".lt-policy"],
		surfaces: [{ selector: ".lt-policy", mode: "band", inner: ".lt-policy__inner", maxWidth: NARROW_MAX }],
	},
	{
		name: "refund-policy",
		path: "/refund-policy",
		topLevel: [".lt-policy"],
		surfaces: [{ selector: ".lt-policy", mode: "band", inner: ".lt-policy__inner", maxWidth: NARROW_MAX }],
	},
	{
		name: "accessibility",
		path: "/accessibility",
		topLevel: [".lt-accessibility"],
		surfaces: [{ selector: ".lt-accessibility", mode: "band", inner: ".lt-accessibility__inner", maxWidth: NARROW_MAX }],
	},
	{
		name: "ready-to-order-paused",
		path: "/ready-to-order-paused",
		topLevel: [".lt-ecommerce-paused"],
		surfaces: ECOMMERCE_PAUSED_SURFACES,
	},
	{
		name: "shop",
		path: "/shop",
		topLevel: [".lt-ecommerce-paused"],
		surfaces: ECOMMERCE_PAUSED_SURFACES,
	},
	{
		name: "shop-by-category",
		path: "/shop-by-category",
		topLevel: [".lt-ecommerce-paused"],
		surfaces: ECOMMERCE_PAUSED_SURFACES,
	},
	{
		name: "variant-product",
		path: "/shop-items/garlands/baby-shower-garland",
		topLevel: [".lt-ecommerce-paused"],
		surfaces: ECOMMERCE_PAUSED_SURFACES,
	},
	{
		name: "single-product",
		path: "/shop-items/seasonal-specialty/easter-balloon-cups",
		topLevel: [".lt-ecommerce-paused"],
		surfaces: ECOMMERCE_PAUSED_SURFACES,
	},
	{
		name: "seasonal-category",
		path: "/shop-items/seasonal-specialty",
		topLevel: [".lt-ecommerce-paused"],
		surfaces: ECOMMERCE_PAUSED_SURFACES,
	},
	{
		name: "cart",
		path: "/cart",
		topLevel: [".lt-ecommerce-paused"],
		surfaces: ECOMMERCE_PAUSED_SURFACES,
	},
	{
		name: "checkout",
		path: "/checkout",
		topLevel: [".lt-ecommerce-paused"],
		surfaces: ECOMMERCE_PAUSED_SURFACES,
	},
	{
		name: "thank-you",
		path: "/thank-you",
		topLevel: [".lt-thanks"],
		surfaces: [{ selector: ".lt-thanks", mode: "band", inner: ".lt-thanks__inner", maxWidth: PAGE_MAX }],
	},
];

async function gotoAndSettle(page, path) {
	const response = await page.goto(new URL(path, BASE_URL).toString(), {
		waitUntil: "domcontentloaded",
		timeout: 30000,
	});
	await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});
	await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {});
	return response;
}

async function auditPageLayout(page, options = {}) {
	const {
		containerSelectors = [],
		targetSelectors = [],
		edgeTolerance = EDGE_TOLERANCE_PX,
		textTolerance = TEXT_TOLERANCE_PX,
		minTargetWidth = 44,
		minTargetHeight = 40,
	} = options;

	return page.evaluate(
		({
			containerSelectors,
			targetSelectors,
			edgeTolerance,
			textTolerance,
			minTargetWidth,
			minTargetHeight,
		}) => {
			const viewportWidth = document.documentElement.clientWidth || window.innerWidth;
			const docWidth = Math.max(
				document.documentElement.scrollWidth,
				document.body ? document.body.scrollWidth : 0,
			);
			const failures = [];

			if (docWidth > viewportWidth + edgeTolerance) {
				failures.push({
					type: "document-overflow",
					selector: "document",
					message: `document scrollWidth ${docWidth}px exceeds viewport ${viewportWidth}px`,
				});
			}

			function selectorFor(element) {
				if (!element || !element.tagName) return "unknown";
				const parts = [];
				let current = element;
				while (current && current.nodeType === Node.ELEMENT_NODE && parts.length < 4) {
					let part = current.tagName.toLowerCase();
					if (current.id) {
						part += `#${current.id}`;
						parts.unshift(part);
						break;
					}
					const classes = Array.from(current.classList || []).slice(0, 3);
					if (classes.length) part += `.${classes.join(".")}`;
					parts.unshift(part);
					current = current.parentElement;
				}
				return parts.join(" > ");
			}

			function hasDirectText(element) {
				return Array.from(element.childNodes || []).some(
					(node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim().length > 0,
				);
			}

			function isVisible(element, style) {
				if (!style || style.display === "none" || style.visibility === "hidden") return false;
				if (Number.parseFloat(style.opacity || "1") === 0) return false;
				const rect = element.getBoundingClientRect();
				return rect.width > 0 && rect.height > 0;
			}

			function clipsOrScrollsX(element) {
				if (!element || element === document.documentElement || element === document.body) {
					return false;
				}
				const style = window.getComputedStyle(element);
				const overflowX = style.overflowX || style.overflow;
				return ["hidden", "clip", "auto", "scroll"].includes(overflowX);
			}

			function hasClippingAncestor(element) {
				let current = element.parentElement;
				while (current && current !== document.documentElement) {
					if (clipsOrScrollsX(current)) return true;
					current = current.parentElement;
				}
				return false;
			}

			for (const element of Array.from(document.body.querySelectorAll("*"))) {
				const style = window.getComputedStyle(element);
				if (!isVisible(element, style)) continue;

				const rect = element.getBoundingClientRect();
				const outsideViewport =
					rect.left < -edgeTolerance || rect.right > viewportWidth + edgeTolerance;

				if (outsideViewport && !hasClippingAncestor(element)) {
					failures.push({
						type: "element-overflow",
						selector: selectorFor(element),
						message: `left ${Math.round(rect.left)}px, right ${Math.round(rect.right)}px, viewport ${viewportWidth}px`,
					});
				}

				const overflowX = style.overflowX || style.overflow;
				if (
					hasDirectText(element) &&
					overflowX === "visible" &&
					element.scrollWidth > element.clientWidth + textTolerance
				) {
					failures.push({
						type: "text-overflow",
						selector: selectorFor(element),
						message: `scrollWidth ${element.scrollWidth}px exceeds clientWidth ${element.clientWidth}px`,
					});
				}
			}

			for (const selector of containerSelectors) {
				for (const element of Array.from(document.querySelectorAll(selector))) {
					const style = window.getComputedStyle(element);
					if (!isVisible(element, style)) continue;
					const overflowX = style.overflowX || style.overflow;
					const intentionallyScrollable = ["auto", "scroll"].includes(overflowX);
					if (
						!intentionallyScrollable &&
						element.scrollWidth > element.clientWidth + textTolerance
					) {
						failures.push({
							type: "container-internal-overflow",
							selector: selectorFor(element),
							message: `scrollWidth ${element.scrollWidth}px exceeds clientWidth ${element.clientWidth}px`,
						});
					}
				}
			}

			for (const selector of targetSelectors) {
				for (const element of Array.from(document.querySelectorAll(selector))) {
					const style = window.getComputedStyle(element);
					if (!isVisible(element, style)) continue;
					const rect = element.getBoundingClientRect();
					if (rect.width < minTargetWidth || rect.height < minTargetHeight) {
						failures.push({
							type: "small-target",
							selector: selectorFor(element),
							message: `${Math.round(rect.width)}px by ${Math.round(rect.height)}px target is below ${minTargetWidth}px by ${minTargetHeight}px`,
						});
					}
				}
			}

			return {
				viewportWidth,
				docWidth,
				failures: failures.slice(0, 30),
				totalFailures: failures.length,
			};
		},
		{
			containerSelectors,
			targetSelectors,
			edgeTolerance,
			textTolerance,
			minTargetWidth,
			minTargetHeight,
		},
	);
}

async function auditContainerContract(page, routeContract) {
	return page.evaluate(
		({ routeContract, edgeTolerance }) => {
			const viewportWidth = document.documentElement.clientWidth || window.innerWidth;
			const docWidth = Math.max(
				document.documentElement.scrollWidth,
				document.body ? document.body.scrollWidth : 0,
			);
			const failures = [];

			function fail(type, selector, message) {
				failures.push({ type, selector, message });
			}

			function selectorFor(element) {
				if (!element || !element.tagName) return "unknown";
				const parts = [];
				let current = element;
				while (current && current.nodeType === Node.ELEMENT_NODE && parts.length < 4) {
					let part = current.tagName.toLowerCase();
					if (current.id) {
						part += `#${current.id}`;
						parts.unshift(part);
						break;
					}
					const classes = Array.from(current.classList || []).slice(0, 4);
					if (classes.length) part += `.${classes.join(".")}`;
					parts.unshift(part);
					current = current.parentElement;
				}
				return parts.join(" > ");
			}

			function isVisible(element) {
				if (!element) return false;
				const style = window.getComputedStyle(element);
				if (!style || style.display === "none" || style.visibility === "hidden") return false;
				if (Number.parseFloat(style.opacity || "1") === 0) return false;
				const rect = element.getBoundingClientRect();
				return rect.width > 0 && rect.height > 0;
			}

			function visibleMatches(selector) {
				return Array.from(document.querySelectorAll(selector)).filter(isVisible);
			}

			function findVisibleInside(root, selector) {
				if (!root || !selector) return null;
				const matches = Array.from(document.querySelectorAll(selector));
				return matches.find((element) => isVisible(element) && (element === root || root.contains(element))) || null;
			}

			function overflowXFor(element) {
				const style = window.getComputedStyle(element);
				return style.overflowX || style.overflow;
			}

			function checkInsideViewport(element, selector, context = "surface") {
				const rect = element.getBoundingClientRect();
				if (rect.left < -edgeTolerance || rect.right > viewportWidth + edgeTolerance) {
					fail(
						`${context}-viewport-overflow`,
						selectorFor(element),
						`${selector} left ${Math.round(rect.left)}px, right ${Math.round(rect.right)}px, viewport ${viewportWidth}px`,
					);
				}
			}

			function checkSpansStage(element, selector, context = "surface") {
				const rect = element.getBoundingClientRect();
				if (rect.left > edgeTolerance || rect.right < viewportWidth - edgeTolerance) {
					fail(
						`${context}-does-not-span-stage`,
						selectorFor(element),
						`${selector} left ${Math.round(rect.left)}px, right ${Math.round(rect.right)}px, viewport ${viewportWidth}px`,
					);
				}
			}

			function checkNoScrollbar(element, selector) {
				const overflowX = overflowXFor(element);
				if (["auto", "scroll"].includes(overflowX)) {
					fail(
						"scrollbar-container",
						selectorFor(element),
						`${selector} uses overflow-x:${overflowX}; marquee/crawl surfaces must clip, not expose scrollbars`,
					);
				}
			}

			function checkContained(element, selector, maxWidth, options = {}) {
				checkInsideViewport(element, selector, "contained");
				const rect = element.getBoundingClientRect();
				if (maxWidth && viewportWidth > maxWidth + 48 && rect.width > maxWidth + 4) {
					fail(
						"contained-max-width",
						selectorFor(element),
						`${selector} width ${Math.round(rect.width)}px exceeds max ${maxWidth}px at viewport ${viewportWidth}px`,
					);
				}
				if (!options.allowFlush && viewportWidth <= 480) {
					const minGutter = 12;
					if (rect.left < -edgeTolerance || rect.right > viewportWidth + edgeTolerance) {
						fail(
							"contained-mobile-overflow",
							selectorFor(element),
							`${selector} escapes the mobile viewport`,
						);
					}
					if (rect.width < viewportWidth - edgeTolerance && rect.left < minGutter && rect.right > viewportWidth - minGutter) {
						fail(
							"contained-mobile-gutter",
							selectorFor(element),
							`${selector} is nearly full-width but has less than ${minGutter}px mobile gutter`,
						);
					}
				}
			}

			function checkInner(surface, root, innerSelector) {
				const inner = findVisibleInside(root, innerSelector);
				if (!inner) {
					fail(
						"missing-container-inner",
						surface.selector,
						`${surface.selector} declares inner ${innerSelector}, but no visible matching descendant was found`,
					);
					return;
				}
				checkContained(inner, innerSelector, surface.maxWidth, { allowFlush: Boolean(surface.allowFlush) });
			}

			if (docWidth > viewportWidth + edgeTolerance) {
				fail(
					"document-overflow",
					"document",
					`document scrollWidth ${docWidth}px exceeds viewport ${viewportWidth}px`,
				);
			}

			const wrapper = document.querySelector(".page-content-wrapper");
			const mainContainer = document.querySelector("main.container");
			const pageContent = document.querySelector(".page_content");

			if (!wrapper) fail("missing-frappe-wrapper", ".page-content-wrapper", "Frappe page wrapper is missing");
			if (!mainContainer) fail("missing-main-container", "main.container", "Frappe main container is missing");
			if (!pageContent) fail("missing-page-content", ".page_content", "Frappe page_content wrapper is missing");

			if (mainContainer) {
				const mainRect = mainContainer.getBoundingClientRect();
				const mainStyle = window.getComputedStyle(mainContainer);
				checkInsideViewport(mainContainer, "main.container", "frappe-main");
				if (
					viewportWidth >= 992 &&
					mainRect.width < viewportWidth - 4 &&
					!["none", "100%"].includes(mainStyle.maxWidth)
				) {
					fail(
						"frappe-main-container-not-neutralized",
						"main.container",
						`main.container is ${Math.round(mainRect.width)}px wide with max-width ${mainStyle.maxWidth}; LT pages must own their own containers`,
					);
				}
			}

			if (pageContent) {
				const declaredTopLevel = routeContract.topLevel || [];
				const visibleTopLevel = Array.from(pageContent.children).filter((element) => {
					if (["SCRIPT", "STYLE", "NOSCRIPT"].includes(element.tagName)) return false;
					return isVisible(element);
				});

				for (const element of visibleTopLevel) {
					if (element.matches("[data-container-contract-ignore]")) continue;
					const declared = declaredTopLevel.some((selector) => element.matches(selector));
					if (!declared) {
						fail(
							"unclassified-top-level-surface",
							selectorFor(element),
							`${selectorFor(element)} is a visible direct child of .page_content but is not in the route container contract`,
						);
					}
				}

				for (const selector of declaredTopLevel) {
					const found = visibleTopLevel.some((element) => element.matches(selector));
					if (!found) {
						fail(
							"missing-top-level-surface",
							selector,
							`${routeContract.path} declares ${selector} as a top-level surface, but it was not visible`,
						);
					}
				}
			}

			for (const surface of routeContract.surfaces || []) {
				const elements = visibleMatches(surface.selector);
				if (!elements.length) {
					if (!surface.optional) {
						fail(
							"missing-surface",
							surface.selector,
							`${routeContract.path} declares ${surface.selector}, but it was not visible`,
						);
					}
					continue;
				}

				for (const element of elements) {
					checkNoScrollbar(element, surface.selector);

					if (surface.mode === "root") {
						checkInsideViewport(element, surface.selector, "root");
						continue;
					}

					if (surface.mode === "raw-band") {
						checkInsideViewport(element, surface.selector, "raw-band");
						continue;
					}

					if (surface.mode === "visual-field") {
						checkInsideViewport(element, surface.selector, "visual-field");
						continue;
					}

					if (surface.mode === "clip") {
						const overflowX = overflowXFor(element);
						if (!["hidden", "clip"].includes(overflowX)) {
							fail(
								"clip-surface-not-clipped",
								selectorFor(element),
								`${surface.selector} must use overflow-x:hidden or clip, but uses ${overflowX}`,
							);
						}
						if (surface.clipMustSpan) checkSpansStage(element, surface.selector, "clip");
						continue;
					}

					if (surface.mode === "fullbleed") {
						checkSpansStage(element, surface.selector, "fullbleed");
						if (!surface.allowNoClass && !element.classList.contains("lt-fullbleed")) {
							fail(
								"fullbleed-missing-class",
								selectorFor(element),
								`${surface.selector} is a full-bleed surface but does not use .lt-fullbleed`,
							);
						}
						if (surface.inner) checkInner(surface, element, surface.inner);
						for (const innerSelector of surface.innerSelectors || []) {
							checkInner(surface, element, innerSelector);
						}
						continue;
					}

					if (surface.mode === "band") {
						checkInsideViewport(element, surface.selector, "band");
						if (surface.inner) checkInner(surface, element, surface.inner);
						for (const innerSelector of surface.innerSelectors || []) {
							checkInner(surface, element, innerSelector);
						}
						continue;
					}

					if (surface.mode === "contained") {
						checkContained(element, surface.selector, surface.maxWidth, {
							allowFlush: Boolean(surface.allowFlush),
						});
						continue;
					}

					fail(
						"unknown-container-mode",
						surface.selector,
						`${surface.selector} declares unsupported container mode ${surface.mode}`,
					);
				}
			}

			return {
				viewportWidth,
				docWidth,
				failures: failures.slice(0, 40),
				totalFailures: failures.length,
			};
		},
		{ routeContract, edgeTolerance: EDGE_TOLERANCE_PX },
	);
}

function expectNoLayoutFailures(expect, result, label) {
	expect(
		result.failures,
		[
			`${label} has ${result.totalFailures} layout fit issue(s).`,
			JSON.stringify(result.failures, null, 2),
		].join("\n"),
	).toEqual([]);
}

module.exports = {
	BASE_URL,
	PUBLIC_ROUTES,
	PASSIVE_VIEWPORTS,
	HEADER_VIEWPORTS,
	MOBILE_DRAWER_VIEWPORTS,
	CONTAINER_CONTRACT_ROUTES,
	CONTAINER_CONTRACT_VIEWPORTS,
	gotoAndSettle,
	auditPageLayout,
	auditContainerContract,
	expectNoLayoutFailures,
};
