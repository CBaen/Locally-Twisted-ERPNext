const { test, expect } = require("@playwright/test");
const { BASE_URL, gotoAndSettle } = require("./layout_helpers");

const ABSOLUTE_BASE = new URL(BASE_URL);

function absolutePath(path) {
	return new URL(path, ABSOLUTE_BASE).toString().replace(/\/$/, path === "/" ? "/" : "");
}

async function getJsonLd(page) {
	return page.locator("script[type='application/ld+json']").evaluateAll((nodes) =>
		nodes.map((node) => JSON.parse(node.textContent || "{}")),
	);
}

function flattenStructuredData(items) {
	const flat = [];
	for (const item of items) {
		if (!item) continue;
		flat.push(item);
		if (Array.isArray(item["@graph"])) flat.push(...item["@graph"]);
	}
	return flat;
}

test.describe("Locally Twisted SEO, GEO, and AEO contract", () => {
	test("about page is source owned and exposes canonical social metadata and business JSON-LD", async ({ page }) => {
		const response = await gotoAndSettle(page, "/about");
		expect(response, "/about should return a response").not.toBeNull();
		expect(response.status(), "/about should load").toBe(200);

		await expect(page.locator("h1")).toHaveCount(1);
		await expect(page.locator("h1")).toHaveText("Balloon decor built for Utah events since 1998.");
		await expect(page.locator("link[rel='canonical']")).toHaveAttribute("href", absolutePath("/about"));
		await expect(page.locator("meta[name='description']")).toHaveAttribute("content", /Utah balloon decor/i);
		await expect(page.locator("meta[property='og:image']")).toHaveAttribute("content", /about-generated-lifestyle-desktop\.webp/);
		await expect(page.locator("meta[name='twitter:image']")).toHaveAttribute("content", /about-generated-lifestyle-desktop\.webp/);
		await expect(page.locator("meta[property='og:url']")).toHaveAttribute("content", absolutePath("/about"));
		await expect(page.locator("meta[property='og:site_name']")).toHaveAttribute("content", "Locally Twisted");
		await expect(page.locator("meta[name='twitter:card']")).toHaveAttribute("content", "summary_large_image");

		const jsonLd = flattenStructuredData(await getJsonLd(page));
		expect(jsonLd.some((item) => item["@type"] === "LocalBusiness" || item["@type"] === "Organization")).toBe(true);
		expect(jsonLd.some((item) => item.aggregateRating || item.openingHours || item.openingHoursSpecification)).toBe(false);
	});

	for (const [path, canonicalPath] of [
		["/home", "/"],
		["/about-us", "/about"],
		["/balloon_twisting_and_face_painting", "/balloon-twisting-and-face-painting"],
		["/refund_policy", "/refund-policy"],
		["/terms_of_service", "/terms-of-service"],
	]) {
		test(`${path} declares the canonical public route`, async ({ page }) => {
			const response = await gotoAndSettle(page, path);
			expect(response, `${path} should return a response`).not.toBeNull();
			expect(response.status(), `${path} should not error`).toBeLessThan(400);
			await expect(page.locator("link[rel='canonical']")).toHaveAttribute("href", absolutePath(canonicalPath));
		});
	}

	test("sitemap prefers canonical public routes and follows the current ecommerce indexing gate", async ({ request }) => {
		const shopProbe = await request.get(new URL("/shop", BASE_URL).toString(), {
			failOnStatusCode: false,
			maxRedirects: 0,
		});
		const ecommercePaused =
			shopProbe.status() >= 300 &&
			shopProbe.status() < 400 &&
			(shopProbe.headers().location || "").includes("/ready-to-order-paused");

		const response = await request.get(new URL("/sitemap.xml", BASE_URL).toString());
		expect(response.status()).toBe(200);
		const xml = await response.text();

		for (const path of ["/", "/about", "/balloon-twisting-and-face-painting", "/faq"]) {
			expect(xml, `sitemap should include ${path}`).toContain(absolutePath(path));
		}
		for (const path of ["/home", "/about-us", "/event-balloons", "/event_balloons", "/balloon_twisting_and_face_painting", "/refund_policy", "/terms_of_service"]) {
			expect(xml, `sitemap should exclude duplicate ${path}`).not.toContain(absolutePath(path));
		}
		for (const path of ["/shop", "/all-products", "/products", "/shop-items", "/shop-items/seasonal-specialty"]) {
			if (ecommercePaused) {
				expect(xml, `paused ecommerce URL should be out of sitemap: ${path}`).not.toContain(absolutePath(path));
			} else {
				if (path === "/products") continue;
				expect(xml, `open ecommerce URL should remain in sitemap: ${path}`).toContain(absolutePath(path));
			}
		}

		expect(xml, "sitemap should not advertise the Frappe Cloud vanity host").not.toContain("locallytwisted.v.frappe.cloud");
		for (const match of xml.matchAll(/<loc>(.*?)<\/loc>/g)) {
			const loc = new URL(match[1]);
			expect(loc.hostname, `${match[1]} should use the tested public host`).toBe(ABSOLUTE_BASE.hostname);
		}
	});

	test("robots.txt allows public crawling and advertises the current-host sitemap", async ({ request }) => {
		const response = await request.get(new URL("/robots.txt", BASE_URL).toString());
		expect(response.status()).toBe(200);
		const text = await response.text();

		expect(text).toContain("User-agent: *");
		expect(text).toContain("Allow: /");
		expect(text).toContain(`Sitemap: ${absolutePath("/sitemap.xml")}`);
		expect(text).not.toContain("Disallow: /");
		expect(text).not.toContain("locallytwisted.v.frappe.cloud");
	});

	test("paused ecommerce doorway is explicitly noindex", async ({ page }) => {
		const response = await gotoAndSettle(page, "/ready-to-order-paused");
		expect(response, "/ready-to-order-paused should return a response").not.toBeNull();
		expect(response.status(), "/ready-to-order-paused should load").toBeLessThan(400);
		await expect(page.locator("meta[name='robots']")).toHaveAttribute("content", /noindex/);
	});

	test("removed Event Balloons hub routes return 404 without redirect", async ({ request }) => {
		for (const path of ["/event-balloons", "/event_balloons"]) {
			const response = await request.get(new URL(path, BASE_URL).toString(), {
				failOnStatusCode: false,
				maxRedirects: 0,
			});
			expect(response.status(), `${path} should be gone`).toBe(404);
			expect(response.headers().location, `${path} should not redirect`).toBeUndefined();
		}
	});

	test("home and service pages expose stable structured data without ratings or hours", async ({ page }) => {
		for (const path of ["/", "/corporate-events", "/balloon-twisting-and-face-painting"]) {
			const response = await gotoAndSettle(page, path);
			expect(response, `${path} should return a response`).not.toBeNull();
			expect(response.status(), `${path} should load`).toBeLessThan(400);
			const jsonLd = flattenStructuredData(await getJsonLd(page));
			const hasBusiness = jsonLd.some((item) => item["@type"] === "LocalBusiness" || item["@type"] === "Organization");
			const hasService = jsonLd.some((item) => item["@type"] === "Service");
			if (path === "/") expect(hasBusiness, "home should expose business graph").toBe(true);
			if (path !== "/") expect(hasService, `${path} should expose Service structured data`).toBe(true);
			expect(jsonLd.some((item) => item.aggregateRating || item.openingHours || item.openingHoursSpecification)).toBe(false);
		}
	});

	test("FAQ visible AEO answers match FAQPage structured data", async ({ page }) => {
		const response = await gotoAndSettle(page, "/faq");
		expect(response, "/faq should return a response").not.toBeNull();
		expect(response.status(), "/faq should load").toBeLessThan(400);

		const faqQuestions = [
			"How are face painting and balloon twisting priced?",
			"How is event balloon decor priced?",
			"What payment is required for personal balloon decor?",
			"How do pickup and delivery usually work for ready-to-order items?",
			"Do corporate clients pay deposits?",
		];

		for (const text of faqQuestions) {
			await expect(page.getByText(text)).toBeVisible();
		}

		const jsonLd = flattenStructuredData(await getJsonLd(page));
		const faq = jsonLd.find((item) => item["@type"] === "FAQPage");
		expect(faq, "FAQPage JSON-LD should exist").toBeTruthy();
		const questionNames = (faq.mainEntity || []).map((item) => item.name);
		for (const text of faqQuestions) {
			expect(questionNames).toContain(text);
		}
	});

	test("BTFP service photos use descriptive alt text for content images", async ({ page }) => {
		const response = await gotoAndSettle(page, "/balloon-twisting-and-face-painting");
		expect(response, "BTFP page should return a response").not.toBeNull();
		expect(response.status(), "BTFP page should load").toBeLessThan(400);

		const result = await page.locator(".lt-btfp__carousel-img").evaluateAll((images) => ({
			total: images.length,
			empty: images.filter((img) => !(img.getAttribute("alt") || "").trim()).length,
		}));
		expect(result.total, "BTFP carousel content images should exist").toBeGreaterThan(0);
		expect(result.empty, "BTFP content images should not use empty decorative alt text").toBe(0);
	});
});
