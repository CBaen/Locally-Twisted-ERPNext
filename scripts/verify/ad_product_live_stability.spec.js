const { test, expect } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "https://locallytwisted.com";
const BIRTHDAY_PATH = "/shop-items/bouquets/birthday-deliveries";
const MISSIONARY_PATH = "/shop-items/bouquets/large-head-missionary";

const birthdayMatrix = [
	{
		size: "Small",
		sizeValue: "Small",
		bouquet: "Small 3 balloon bouquet",
		bouquetValue: "Small 3 balloon bouquet",
		expectedPrice: "$ 90.00",
		expectedItem: "birthday-deliveries-SMA-MIC-12-SMA",
	},
	{
		size: "Small",
		sizeValue: "Small",
		bouquet: "5 balloon bouquet",
		bouquetValue: "5 balloon bouquet",
		expectedPrice: "$ 100.00",
		expectedItem: "birthday-deliveries-SMA-MIC-12-5BA",
	},
	{
		size: "Small",
		sizeValue: "Small",
		bouquet: "7 balloon bouquet",
		bouquetValue: "7 balloon bouquet",
		expectedPrice: "$ 110.00",
		expectedItem: "birthday-deliveries-SMA-MIC-12-7BA",
	},
	{
		size: "Medium",
		sizeValue: "Medium",
		bouquet: "Small 3 balloon bouquet",
		bouquetValue: "Small 3 balloon bouquet",
		expectedPrice: "$ 120.00",
		expectedItem: "birthday-deliveries-MED-MIC-12-SMA",
	},
	{
		size: "Medium",
		sizeValue: "Medium",
		bouquet: "5 balloon bouquet",
		bouquetValue: "5 balloon bouquet",
		expectedPrice: "$ 130.00",
		expectedItem: "birthday-deliveries-MED-MIC-12-5BA",
	},
	{
		size: "Medium",
		sizeValue: "Medium",
		bouquet: "7 balloon bouquet",
		bouquetValue: "7 balloon bouquet",
		expectedPrice: "$ 140.00",
		expectedItem: "birthday-deliveries-MED-MIC-12-7BA",
	},
	{
		size: "Large",
		sizeValue: "Large",
		bouquet: "Small 3 balloon bouquet",
		bouquetValue: "Small 3 balloon bouquet",
		expectedPrice: "$ 155.00",
		expectedItem: "birthday-deliveries-LAR-MIC-12-SMA",
	},
	{
		size: "Large",
		sizeValue: "Large",
		bouquet: "5 balloon bouquet",
		bouquetValue: "5 balloon bouquet",
		expectedPrice: "$ 165.00",
		expectedItem: "birthday-deliveries-LAR-MIC-12-5BA",
	},
	{
		size: "Large",
		sizeValue: "Large",
		bouquet: "7 balloon bouquet",
		bouquetValue: "7 balloon bouquet",
		expectedPrice: "$ 175.00",
		expectedItem: "birthday-deliveries-LAR-MIC-12-7BA",
	},
];

function route(path) {
	return new URL(path, BASE_URL).toString();
}

async function visibleBodyText(page) {
	return page.locator("body").innerText();
}

async function chooseBirthdayConfiguration(page, row) {
	await page.goto(route(BIRTHDAY_PATH), { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".lt-product__configure");

	await page.evaluate(
		async ({ sizeValue, bouquetValue }) => {
			const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
			const dispatch = (element) => {
				element.dispatchEvent(new Event("input", { bubbles: true }));
				element.dispatchEvent(new Event("change", { bubbles: true }));
			};
			const chooseRadio = (attributeName, value) => {
				const selector = `.lt-product__attr[data-attribute-name="${attributeName}"] input[type="radio"][value="${value}"]`;
				const input = document.querySelector(selector);
				if (!input) {
					throw new Error(`Missing ${attributeName} option: ${value}`);
				}
				input.checked = true;
				dispatch(input);
				return input;
			};
			const chooseTheme = () => {
				const select = document.querySelector(
					'.lt-product__attr[data-attribute-name="Delivery themes"] select',
				);
				if (!select) {
					throw new Error("Missing Delivery themes select");
				}
				const option = Array.from(select.options).find(
					(candidate) => !candidate.disabled && candidate.value === "Mickey",
				);
				if (!option) {
					throw new Error("Missing enabled Mickey delivery theme");
				}
				select.value = option.value;
				dispatch(select);
			};
			const fillAge = () => {
				const age = document.querySelector(
					'.js-lt-product-setup-group[data-setup-label="ADD BIRTHDAY AGE"] input[type="number"]',
				);
				if (!age) {
					throw new Error("Missing visible ADD BIRTHDAY AGE number input");
				}
				age.value = "25";
				dispatch(age);
			};

			chooseRadio("Delivery Size", sizeValue);
			await wait(250);
			chooseTheme();
			await wait(250);
			fillAge();
			await wait(250);
			chooseRadio("Add Bouquet", bouquetValue);
			await wait(1250);
		},
		{ sizeValue: row.sizeValue, bouquetValue: row.bouquetValue },
	);
}

test.describe.configure({ mode: "serial" });

test("Large Head Missionary live route and cart API price are 125", async ({ page }) => {
	await page.goto(route(MISSIONARY_PATH), { waitUntil: "domcontentloaded" });

	const text = await visibleBodyText(page);
	expect(text).toContain("$ 125.00");
	expect(text).not.toContain("$ 175.00");

	const cartProof = await page.evaluate(async () => {
		const body = new URLSearchParams();
		body.set(
			"item_codes",
			JSON.stringify([{ item_code: "large-head-missionary-ELD-BLU-BLA", qty: 1 }]),
		);
		const response = await fetch("/api/method/locally_twisted.api.cart.get_cart_items", {
			method: "POST",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
				"X-Frappe-CSRF-Token": window.frappe?.csrf_token || "",
			},
			body: body.toString(),
		});
		return response.json();
	});
	const item = cartProof?.message?.items?.[0];
	expect(item?.item_code).toBe("large-head-missionary-ELD-BLU-BLA");
	expect(item?.price_list_rate).toBe(125);
	expect(item?.line_total).toBe(125);
});

test("Birthday Deliveries exposes birthday age, not the old foil-number selector", async ({ page }) => {
	await page.goto(route(BIRTHDAY_PATH), { waitUntil: "domcontentloaded" });
	await page.waitForSelector(".lt-product__configure");

	const text = await visibleBodyText(page);
	expect(text).toContain("ADD BIRTHDAY AGE");
	expect(text).not.toContain("Add Foil Number");

	const ageInput = page.locator(
		'.js-lt-product-setup-group[data-setup-label="ADD BIRTHDAY AGE"] input',
	);
	await expect(ageInput).toHaveAttribute("type", "number");

	const legacyState = await page.evaluate(() => {
		const legacy = document.querySelector('.lt-product__attr[data-attribute-name="Add Foil Number"]');
		if (!legacy) {
			return { exists: false };
		}
		return {
			exists: true,
			display: window.getComputedStyle(legacy).display,
			ariaHidden: legacy.getAttribute("aria-hidden"),
		};
	});
	expect(legacyState).toEqual({ exists: true, display: "none", ariaHidden: "true" });
});

for (const row of birthdayMatrix) {
	test(`Birthday Deliveries ${row.size} + ${row.bouquet} resolves to ${row.expectedPrice}`, async ({
		page,
	}) => {
		await chooseBirthdayConfiguration(page, row);

		await expect(page.locator("#lt-product-price-text")).toContainText(row.expectedPrice);
		const addButton = page.locator("#lt-add-to-cart-variant");
		await expect(addButton).toBeEnabled();
		await expect(addButton).toHaveAttribute("data-item-code", row.expectedItem);

		const text = await visibleBodyText(page);
		expect(text).toContain("ADD BIRTHDAY AGE");
		expect(text).not.toContain("Add Foil Number");
	});
}
