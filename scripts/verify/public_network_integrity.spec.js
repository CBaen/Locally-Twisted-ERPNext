const { test, expect } = require("@playwright/test");
const { BASE_URL, PUBLIC_ROUTES, gotoAndSettle } = require("./layout_helpers");

const DESK_USER = process.env.LT_DESK_TEST_USER || "Administrator";
const DESK_PASSWORD = process.env.LT_DESK_TEST_PASSWORD || "admin";

const EXTRA_ROUTES = [
	{ name: "shop-items-root", path: "/shop-items" },
	{ name: "shop-items-arches", path: "/shop-items/arches" },
	{ name: "shop-items-bouquets", path: "/shop-items/bouquets" },
	{ name: "shop-items-get-well-bouquets", path: "/shop-items/get-well-bouquets" },
	{ name: "shop-items-garlands", path: "/shop-items/garlands" },
	{ name: "shop-items-columns", path: "/shop-items/columns" },
	{ name: "shop-items-drops", path: "/shop-items/drops" },
	{ name: "shop-items-grab-go", path: "/shop-items/grab-go" },
	{ name: "shop-items-table-decor", path: "/shop-items/table-decor" },
	{ name: "shop-items-stands-easels", path: "/shop-items/stands-easels" },
	{ name: "shop-items-deliveries", path: "/shop-items/deliveries" },
	{ name: "shop-items-seasonal", path: "/shop-items/seasonal-specialty" },
	{ name: "all-products", path: "/all-products" },
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
	if (expectedType === "font") {
		return normalized.startsWith("font/")
			|| normalized.includes("application/font")
			|| normalized.includes("application/octet-stream");
	}
	return true;
}

function collectPublicNetworkIssues(page) {
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
		const pageUrl = page.url();
		const url = new URL(request.url());
		if (pageUrl !== "about:blank" && url.origin === new URL(pageUrl).origin) {
			issues.push(`request failed: ${request.url()} ${request.failure()?.errorText || ""}`.trim());
		}
	});
	page.on("response", (response) => {
		const pageUrl = page.url();
		if (pageUrl === "about:blank") return;
		const url = new URL(response.url());
		const base = new URL(pageUrl);
		if (url.origin !== base.origin) return;
		const status = response.status();
		const resourceType = response.request().resourceType();
		const method = response.request().method();
		if (method !== "GET" && status >= 400) {
			issues.push(`${method} ${response.url()} returned HTTP ${status}`);
			return;
		}
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
	return issues;
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

test.describe("public network integrity", () => {
	for (const route of ROUTES) {
		test(`${route.name} has no broken same-origin assets or console errors`, async ({ page }) => {
			const issues = collectPublicNetworkIssues(page);

			await page.setViewportSize({ width: 1366, height: 900 });
			const response = await gotoAndSettle(page, route.path);
			expect(response, `${route.path} should return a response`).not.toBeNull();
			expect(response.status(), `${route.path} HTTP status`).toBeLessThan(400);
			expect(issues, `${route.path} network/console issues`).toEqual([]);
		});
	}

	test("logged-in Desk session keeps Webshop startup POSTs CSRF-clean", async ({ page }) => {
		const issues = collectPublicNetworkIssues(page);

		await loginThroughApi(page);
		await page.goto(new URL("/app", BASE_URL).toString(), { waitUntil: "networkidle" });
		await expect.poll(
			() => page.evaluate(() => window.frappe?.csrf_token || null),
			{ message: "Desk should generate a session CSRF token" },
		).not.toBeNull();
		issues.length = 0;

		const response = await gotoAndSettle(page, "/shop-items/arches");
		expect(response, "/shop-items/arches should return a response").not.toBeNull();
		expect(response.status(), "/shop-items/arches HTTP status").toBeLessThan(400);
		await expect.poll(
			() => page.evaluate(() => window.frappe?.csrf_token || null),
			{ message: "website page should expose the session CSRF token" },
		).not.toBeNull();
		expect(issues, "logged-in Webshop network/console issues").toEqual([]);
	});

	test("regression harness catches stale stylesheet and POST failure classes", async ({ page }) => {
		const issues = collectPublicNetworkIssues(page);
		const syntheticPageUrl = new URL("/__lt-public-network-regression", BASE_URL).toString();
		const staleCssUrl = new URL("/assets/webshop/dist/css/webshop-web.bundle.STALE123.css", BASE_URL).toString();
		const rootUrl = new URL("/", BASE_URL).toString();

		await page.route(syntheticPageUrl, async (route) => {
			await route.fulfill({
				status: 200,
				contentType: "text/html",
				body: [
					"<!doctype html><html><head>",
					`<link rel="stylesheet" href="${staleCssUrl}">`,
					"</head><body>",
					"<script>",
					"fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: 'cmd=webshop.webshop.api.get_product_filter_data' })",
					".finally(() => { window.__ltRegressionPostDone = true; });",
					"</script>",
					"</body></html>",
				].join(""),
			});
		});
		await page.route(staleCssUrl, async (route) => {
			await route.fulfill({
				status: 404,
				contentType: "text/html",
				body: "<html><body>stale stylesheet hash</body></html>",
			});
		});
		await page.route(rootUrl, async (route) => {
			if (route.request().method() !== "POST") {
				await route.continue();
				return;
			}
			await route.fulfill({
				status: 400,
				contentType: "application/json",
				body: JSON.stringify({ exc_type: "CSRFTokenError" }),
			});
		});

		const response = await page.goto(syntheticPageUrl, { waitUntil: "domcontentloaded" });
		expect(response, "synthetic regression page should return a response").not.toBeNull();
		expect(response.status(), "synthetic regression page HTTP status").toBe(200);
		await page.waitForFunction(() => window.__ltRegressionPostDone === true);
		await page.waitForTimeout(250);

		expect(issues.some((issue) => issue.includes(staleCssUrl) && issue.includes("HTTP 404"))).toBe(true);
		expect(issues.some((issue) => issue.includes(`POST ${rootUrl}`) && issue.includes("HTTP 400"))).toBe(true);
	});
});
