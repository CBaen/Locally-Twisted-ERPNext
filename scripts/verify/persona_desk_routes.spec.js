const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const DESK_PASSWORD = process.env.LT_DESK_TEST_PASSWORD;

const PERSONAS = [
	{
		name: "manager",
		user: process.env.LT_MANAGER_TEST_USER || "lt-manager-temp@example.com",
		title: "Manager Home",
		expected: [
			"Manager Home",
			"Today's work",
			"Events Inquiry Inbox",
			"Inquiry Board",
			"Booking Calendar",
			"Task Board",
			"Customers",
			"People to Contact",
			"Add New Inquiry",
			"Add Customer",
		],
		forbidden: ["Products", "Product Prices", "Add Product"],
	},
	{
		name: "employee",
		user: process.env.LT_EMPLOYEE_TEST_USER || "lt-employee-temp@example.com",
		title: "My Jobs",
		expected: ["My Jobs", "Work to do", "My Tasks", "Task Board", "Event Jobs"],
		forbidden: [
			"Events Inquiry Inbox",
			"Inquiry Board",
			"Booking Calendar",
			"Customers",
			"People to Contact",
			"Add New Inquiry",
			"Add Customer",
			"Products",
		],
	},
	{
		name: "accountant",
		user: process.env.LT_ACCOUNTANT_TEST_USER || "lt-accountant-temp@example.com",
		title: "Accounting Home",
		expected: [
			"Accounting Home",
			"Money to collect",
			"Sales Invoices",
			"Payment Requests",
			"Payments",
			"Customers",
			"Review before sending",
			"Reminder Review Report",
			"Accounting reference",
			"Journal Entries",
			"Chart of Accounts",
		],
		forbidden: [
			"Suppliers",
			"Purchase Invoices",
			"Bank Transactions",
			"Bank Accounts",
			"Bank Reconciliation",
			"Payment Terms",
			"Statement Reminders",
			"Employees",
		],
	},
];

test.describe("Persona Desk routes", () => {
	test.skip(!DESK_PASSWORD, "Set LT_DESK_TEST_PASSWORD.");

	for (const persona of PERSONAS) {
		test(`${persona.name} lands on personalized workspace`, async ({ page }) => {
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
				{ user: persona.user, password: DESK_PASSWORD },
			);

			expect(login.status, login.body).toBe(200);

			await page.goto(new URL("/app/Workspaces", BASE_URL).toString(), {
				waitUntil: "domcontentloaded",
			});
			await page.waitForLoadState("networkidle", { timeout: 10_000 }).catch(() => {});

			const body = page.locator("body");
			await expect(page).toHaveTitle(persona.title);
			for (const text of persona.expected) {
				await expect(body, `${persona.name} should see ${text}`).toContainText(text);
			}
			for (const text of persona.forbidden) {
				await expect(body, `${persona.name} should not see ${text}`).not.toContainText(text);
			}
		});
	}
});
