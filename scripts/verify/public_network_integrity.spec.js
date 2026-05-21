const { test, expect } = require("@playwright/test");
const { PUBLIC_ROUTES, gotoAndSettle } = require("./layout_helpers");

const EXTRA_ROUTES = [
	{ name: "shop-items-root", path: "/shop-items" },
	{ name: "shop-items-arches", path: "/shop-items/arches" },
	{ name: "shop-items-bouquets", path: "/shop-items/bouquets" },
	{ name: "shop-items-garlands", path: "/shop-items/garlands" },
	{ name: "shop-items-columns", path: "/shop-items/columns" },
	{ name: "shop-items-seasonal", path: "/shop-items/seasonal-specialty" },
	{ name: "easter-bunny-ear", path: "/shop-items/arches/easter-balloon-arch-bunny-ear" },
	{ name: "unicorn-bouquet", path: "/shop-items/bouquets/unicorn-bouquet" },
];

const ROUTES = Array.from(
	new Map([...PUBLIC_ROUTES, ...EXTRA_ROUTES].map((route) => [route.path, route])).values(),
);

function expectedTypeFor(url, resourceType) {
	const pathname = new URL(url).pathname.toLowerCase();
	if (resourceType === "script" || pathname.endsWith(".js")) return "javascript";
	if (resourceType === "stylesheet" || pathname.endsWith(".css")) return "css";
	if (resourceType === "image" || /\.(png|jpe?g|webp|gif|svg|ico)$/.test(pathname)) return "image";
	if (resourceType === "font" || /\.(woff2?|ttf|otf)$/.test(pathname)) return "font";
	return null;
}

function contentTypeMatches(contentType, expectedType) {
	const normalized = (contentType || "").toLowerCase();
	if (!expectedType) return true;
	if (expectedType === "javascript") return normalized.includes("javascript") || normalized.includes("ecmascript");
	if (expectedType === "css") return normalized.includes("text/css");
	if (expectedType === "image") return normalized.startsWith("image/");
	if (expectedType === "font") return normalized.startsWith("font/") || normalized.includes("font");
	return true;
}

test.describe("public network integrity", () => {
	for (const route of ROUTES) {
		test(`${route.name} has no broken same-origin assets or console errors`, async ({ page }) => {
			const issues = [];
			page.on("console", (message) => {
				if (["error", "warning"].includes(message.type())) {
					issues.push(`console ${message.type()}: ${message.text()}`);
				}
			});
			page.on("pageerror", (error) => {
				issues.push(`page error: ${error.message}`);
			});
			page.on("requestfailed", (request) => {
				const url = new URL(request.url());
				if (url.origin === new URL(page.url()).origin) {
					issues.push(`request failed: ${request.url()} ${request.failure()?.errorText || ""}`.trim());
				}
			});
			page.on("response", (response) => {
				const url = new URL(response.url());
				const base = new URL(page.url());
				if (url.origin !== base.origin) return;
				const status = response.status();
				const resourceType = response.request().resourceType();
				const isAsset =
					url.pathname.startsWith("/assets/")
					|| url.pathname.startsWith("/files/")
					|| url.pathname === "/website_script.js"
					|| ["stylesheet", "script", "image", "font"].includes(resourceType);
				if (!isAsset) return;
				if (status >= 400) {
					issues.push(`${response.url()} returned HTTP ${status}`);
					return;
				}
				const expectedType = expectedTypeFor(response.url(), resourceType);
				const contentType = response.headers()["content-type"] || "";
				if (!contentTypeMatches(contentType, expectedType)) {
					issues.push(`${response.url()} returned ${contentType || "no content-type"}, expected ${expectedType}`);
				}
			});

			await page.setViewportSize({ width: 1366, height: 900 });
			const response = await gotoAndSettle(page, route.path);
			expect(response, `${route.path} should return a response`).not.toBeNull();
			expect(response.status(), `${route.path} HTTP status`).toBeLessThan(400);
			expect(issues, `${route.path} network/console issues`).toEqual([]);
		});
	}
});
