const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const EDGE_TOLERANCE_PX = 2;
const TEXT_TOLERANCE_PX = 2;

const VIEWPORTS = [
	{ name: "mobile-320", width: 320, height: 812 },
	{ name: "mobile-375", width: 375, height: 812 },
	{ name: "tablet", width: 768, height: 1024 },
	{ name: "desktop", width: 1366, height: 768 },
];

const ROUTES = [
	{ name: "home", path: "/" },
	{ name: "book-alias", path: "/book" },
	{ name: "contact", path: "/contact" },
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
];

test.describe("Locally Twisted layout fit", () => {
	for (const viewport of VIEWPORTS) {
		for (const route of ROUTES) {
			test(`${route.name} fits at ${viewport.name}`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await page.goto(new URL(route.path, BASE_URL).toString(), {
					waitUntil: "domcontentloaded",
					timeout: 30000,
				});
				expect(response, `${route.path} should return a response`).not.toBeNull();
				expect(response.status(), `${route.path} HTTP status`).toBeLessThan(400);

				await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});
				await page.evaluate(() => document.fonts && document.fonts.ready);

				const result = await page.evaluate(
					({ edgeTolerance, textTolerance }) => {
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

						return {
							viewportWidth,
							docWidth,
							failures: failures.slice(0, 20),
							totalFailures: failures.length,
						};
					},
					{ edgeTolerance: EDGE_TOLERANCE_PX, textTolerance: TEXT_TOLERANCE_PX },
				);

				expect(
					result.failures,
					[
						`${route.path} at ${viewport.name} (${viewport.width}px) has ${result.totalFailures} layout fit issue(s).`,
						JSON.stringify(result.failures, null, 2),
					].join("\n"),
				).toEqual([]);
			});
		}
	}
});
