const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const DESK_USER = process.env.LT_DESK_TEST_USER;
const DESK_PASSWORD = process.env.LT_DESK_TEST_PASSWORD;
const PLATFORM_WORDS = /\b(?:ERPNext|Frappe)\b/i;

test.describe("Owner Desk route recovery", () => {
	test.skip(!DESK_USER || !DESK_PASSWORD, "Set LT_DESK_TEST_USER and LT_DESK_TEST_PASSWORD.");

	test("direct Desk routes land on the owner workspace", async ({ page }) => {
		const getPageFailures = [];

		page.on("response", (response) => {
			if (
				response.url().includes("frappe.desk.desk_page.getpage") &&
				response.status() >= 400
			) {
				getPageFailures.push(`${response.status()} ${response.url()}`);
			}
		});

		await page.goto(new URL("/login", BASE_URL).toString(), { waitUntil: "domcontentloaded" });

		const login = await page.evaluate(
			async ({ user, password }) => {
				const response = await fetch("/api/method/login", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"X-Requested-With": "XMLHttpRequest",
					},
					body: JSON.stringify({ usr: user, pwd: password }),
				});

				return {
					status: response.status,
					body: await response.text(),
				};
			},
			{ user: DESK_USER, password: DESK_PASSWORD },
		);

		expect(login.status, login.body).toBe(200);

		for (const route of ["/app/home", "/app/owner-home", "/app/Workspaces"]) {
			await page.goto(new URL(route, BASE_URL).toString(), { waitUntil: "domcontentloaded" });
			await page.waitForLoadState("networkidle", { timeout: 10_000 }).catch(() => {});

			const body = page.locator("body");
			await expect(body).toContainText("Owner Home");
			await expect(body).toContainText("Today at Locally Twisted");
			await expect(body).toContainText("What Jeff does next");
			await expect(body).toContainText("New Inquiries");
			await expect(body).toContainText("Overdue Follow-ups");
			await expect(body).toContainText("Add Product");
			const visibleText = await body.innerText();
			expect(visibleText, `${route} owner-visible text should stay white-labeled`).not.toMatch(PLATFORM_WORDS);
			await expect(body).not.toContainText("Page not found");
			expect(page.url()).toContain("/app/Workspaces");
		}

		expect(getPageFailures).toEqual([]);
	});
});
