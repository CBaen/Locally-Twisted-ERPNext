const { test, expect } = require("@playwright/test");
const {
	CONTAINER_CONTRACT_ROUTES,
	CONTAINER_CONTRACT_VIEWPORTS,
	gotoAndSettle,
	auditContainerContract,
	expectNoLayoutFailures,
} = require("./layout_helpers");

test.describe("Locally Twisted public container contract", () => {
	for (const viewport of CONTAINER_CONTRACT_VIEWPORTS) {
		for (const route of CONTAINER_CONTRACT_ROUTES) {
			test(`${route.name} declares and honors containers at ${viewport.name}`, async ({ page }) => {
				await page.setViewportSize({ width: viewport.width, height: viewport.height });
				const response = await gotoAndSettle(page, route.path);
				expect(response, `${route.path} should return a response`).not.toBeNull();
				expect(response.status(), `${route.path} HTTP status`).toBeLessThan(400);

				const result = await auditContainerContract(page, route);
				expectNoLayoutFailures(
					expect,
					result,
					`${route.path} container contract at ${viewport.name} (${viewport.width}px)`,
				);
			});
		}
	}
});
