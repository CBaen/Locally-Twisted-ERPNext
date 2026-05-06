const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";

const EDGE_TOLERANCE_PX = 2;
const TEXT_TOLERANCE_PX = 2;

const PUBLIC_ROUTES = [
	{ name: "home", path: "/" },
	{ name: "book-alias", path: "/book" },
	{ name: "contact", path: "/contact" },
	{ name: "event-balloons", path: "/event-balloons" },
	{ name: "portfolio", path: "/portfolio" },
	{ name: "process", path: "/process" },
	{ name: "btfp", path: "/balloon-twisting-and-face-painting" },
	{ name: "faq", path: "/faq" },
	{ name: "privacy", path: "/privacy" },
	{ name: "terms", path: "/terms-of-service" },
	{ name: "refund-policy", path: "/refund-policy" },
	{ name: "accessibility", path: "/accessibility" },
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
	gotoAndSettle,
	auditPageLayout,
	expectNoLayoutFailures,
};
