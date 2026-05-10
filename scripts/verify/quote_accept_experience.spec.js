const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { test, expect } = require("@playwright/test");
const { auditPageLayout, expectNoLayoutFailures, gotoAndSettle } = require("./layout_helpers");

const TEMPLATE_PATH = path.resolve(
	__dirname,
	"../../apps/locally_twisted/locally_twisted/www/quote_accept.html",
);
const CONTAINER = "locally-twisted-erpnext-v15-backend-1";
const SITE = "frontend";

function benchExecute(method, kwargs = undefined) {
	const args = ["exec", CONTAINER, "bench", "--site", SITE, "execute", method];
	if (kwargs) {
		args.push("--kwargs", JSON.stringify(kwargs));
	}
	const output = execFileSync("docker", args, {
		encoding: "utf8",
		stdio: ["ignore", "pipe", "pipe"],
	}).trim();
	return output ? JSON.parse(output) : null;
}

test.describe("quote acceptance customer experience", () => {
	let fixtureMarker = "";

	test.afterEach(() => {
		if (!fixtureMarker) return;
		try {
			benchExecute("locally_twisted.verify.quote_accept_experience_fixture.cleanup", {
				marker: fixtureMarker,
			});
		} finally {
			fixtureMarker = "";
		}
	});

	test("missing approval code fails loudly with a safe contact fallback", async ({ page }) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await gotoAndSettle(page, "/quote-accept");

		await expect(page.locator("h1")).toContainText("Review your quote");
		await expect(page.locator(".lt-quote-accept__error")).toContainText("Tiny snag");
		await expect(page.locator("body")).toContainText("Nothing was approved or ordered");
		await expect(page.getByRole("link", { name: /contact locally twisted/i })).toHaveAttribute("href", "/contact");
		await expect(page.locator("#lt-quote-accept-form")).toHaveCount(0);

		const layout = await auditPageLayout(page, {
			containerSelectors: [".lt-quote-accept__inner", ".lt-quote-accept__error"],
			targetSelectors: [".lt-quote-accept__button"],
		});
		expectNoLayoutFailures(expect, layout, "quote accept missing-token page");
	});

	test("approval success state is a distinct no-payment customer panel", () => {
		const source = fs.readFileSync(TEMPLATE_PATH, "utf8");

		expect(source).toContain("lt-quote-accept__success");
		expect(source).toContain("data-lt-quote-accepted");
		expect(source).toContain("No card was charged");
		expect(source).toContain("Nothing was invoiced");
		expect(source).toContain("/contact");
	});

	test("real approval token previews quote and submits to a no-payment success state", async ({ page }) => {
		const fixture = benchExecute("locally_twisted.verify.quote_accept_experience_fixture.create", {
			base_url: "http://localhost:8081",
		});
		fixtureMarker = fixture.marker;

		await page.setViewportSize({ width: 390, height: 844 });
		await gotoAndSettle(page, fixture.acceptance_path);

		await expect(page.locator("h1")).toContainText("Review your quote");
		await expect(page.locator(".lt-quote-accept__summary")).toContainText(fixture.quotation);
		await expect(page.locator(".lt-quote-accept__summary")).toContainText("Requested product page quote");
		await expect(page.locator(".lt-quote-accept__summary")).toContainText("$650.00 USD");

		await page.locator('input[name="accepted_by"]').fill("Cameron Browser Customer");
		await page.locator('input[name="accepted_email"]').fill("cameron-browser@example.invalid");
		await page.locator('textarea[name="acceptance_reference"]').fill("browser approval proof");
		await page.getByRole("button", { name: /approve quote/i }).click();

		await expect(page.locator("[data-lt-quote-accepted]")).toBeVisible();
		await expect(page.locator("[data-lt-quote-accepted]")).toContainText("No card was charged");
		await expect(page.locator("[data-lt-quote-accepted]")).toContainText("Nothing was invoiced");
		await expect(page.locator("#lt-quote-accept-form")).toBeHidden();

		const cleanupPreview = benchExecute("locally_twisted.verify.quote_accept_experience_fixture.preview_cleanup_state", {
			marker: fixtureMarker,
		});
		expect(cleanupPreview.sales_order_count).toBe(1);
		expect(cleanupPreview.invoice_count).toBe(0);
		expect(cleanupPreview.payment_request_count).toBe(0);
	});
});
