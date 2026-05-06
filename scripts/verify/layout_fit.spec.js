const { test, expect } = require("@playwright/test");
const {
	PUBLIC_ROUTES,
	PASSIVE_VIEWPORTS,
	gotoAndSettle,
	auditPageLayout,
	expectNoLayoutFailures,
} = require("./layout_helpers");

test.describe("Locally Twisted layout fit", () => {
	for (const viewport of PASSIVE_VIEWPORTS) {
		for (const route of PUBLIC_ROUTES) {
			test(`${route.name} fits at ${viewport.name}`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, route.path);
				expect(response, `${route.path} should return a response`).not.toBeNull();
				expect(response.status(), `${route.path} HTTP status`).toBeLessThan(400);

				const result = await auditPageLayout(page);
				expectNoLayoutFailures(
					expect,
					result,
					`${route.path} at ${viewport.name} (${viewport.width}px)`,
				);
			});
		}
	}
});
