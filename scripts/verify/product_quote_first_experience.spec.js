const { expect, test } = require("@playwright/test");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const DESK_USER = process.env.LT_DESK_TEST_USER || "Administrator";
const DESK_PASSWORD = process.env.LT_DESK_TEST_PASSWORD || "admin";
const VIEWPORTS = [
	{ name: "desktop", width: 1366, height: 900 },
	{ name: "mobile", width: 390, height: 844 },
];

async function loginAsOperator(page) {
	const response = await page.goto(new URL("/login", BASE_URL).toString(), { waitUntil: "domcontentloaded" });
	expect(response, "/login should respond").not.toBeNull();

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
			return { status: response.status, body: await response.text() };
		},
		{ user: DESK_USER, password: DESK_PASSWORD },
	);
	expect(login.status, login.body).toBe(200);
}

async function chooseFirstVisibleOption(page) {
	const firstSelect = page.locator(".lt-product__quote-attr select.js-lt-quote-option").first();
	if (await firstSelect.count()) {
		const values = await firstSelect.locator("option").evaluateAll((options) =>
			options.map((option) => option.value).filter(Boolean),
		);
		if (values.length) {
			await firstSelect.selectOption(values[0]);
			return;
		}
	}

	const firstChoice = page.locator(".lt-product__quote-attr input.js-lt-quote-option").first();
	if (await firstChoice.count()) {
		await firstChoice.check({ force: true });
	}
}

async function chooseReadyToOrderOption(page) {
	const firstSelect = page.locator(".lt-product__attr select.js-lt-attr-input").first();
	if (await firstSelect.count()) {
		const values = await firstSelect.locator("option").evaluateAll((options) =>
			options.map((option) => option.value).filter(Boolean),
		);
		if (values.length) {
			await firstSelect.selectOption(values[0]);
			return;
		}
	}

	const firstChoice = page.locator(".lt-product__attr input.js-lt-attr-input").first();
	await expect(firstChoice).toBeVisible();
	await firstChoice.check({ force: true });
}

async function chooseFirstColorRecipeOption(page) {
	const firstColor = page.locator('.lt-product__attr[data-payload-target="color_recipes"] input.js-lt-color-radio').first();
	await expect(firstColor).toBeVisible();
	await firstColor.check({ force: true });
}

async function primeBrowser(page) {
	await page.addInitScript(() => {
		window.localStorage.setItem("lt_cookie_consent", "declined");
		window.localStorage.removeItem("lt_cart");
		document.cookie = "lt_cookie_consent=declined; path=/; SameSite=Lax";
	});
	await loginAsOperator(page);
}

async function expectNoHorizontalOverflow(page) {
	const metrics = await page.evaluate(() => ({
		scrollWidth: document.documentElement.scrollWidth,
		clientWidth: document.documentElement.clientWidth,
	}));
	expect(metrics.scrollWidth, "product page should not create horizontal overflow").toBeLessThanOrEqual(
		metrics.clientWidth + 2,
	);
}

async function expectArchitectureContract(page, expectedLane) {
	const node = page.locator(".js-lt-product-page-architecture").first();
	await expect(node).toBeAttached();
	const contract = JSON.parse(await node.textContent());
	expect(contract.schema_version).toBe("lt-product-page-architecture-contract-v1");
	expect(contract.commerce_lane).toBe(expectedLane);
	expect(contract.product_specific_rules_allowed).toBe(false);
	expect(contract.payload_contract.client_payload_keys).toEqual(
		expect.arrayContaining(["selected_options", "color_recipes", "add_ons", "customizations"]),
	);
	expect(contract.payload_contract.server_derived_keys).toEqual(
		expect.arrayContaining(["resolved_item_code", "price_provenance", "readable_summary", "canonical_cart_line_key"]),
	);
	return contract;
}

for (const viewport of VIEWPORTS) {
	test(`quote-first product page carries selected details into the contact form on ${viewport.name}`, async ({ page }) => {
		await page.setViewportSize({ width: viewport.width, height: viewport.height });
		await primeBrowser(page);
		await page.goto(new URL("/shop-items/arches/classic-arch", BASE_URL).toString(), {
			waitUntil: "domcontentloaded",
		});

		await expect(page.locator(".lt-product__cart--quote-first")).toBeVisible();
		await expect(page.locator(".lt-product__configure")).toHaveCount(0);
		const architecture = await expectArchitectureContract(page, "quote_first");
		expect(architecture.controls.some((control) => control.payload_target === "color_recipes")).toBe(true);
		await expectNoHorizontalOverflow(page);
		await chooseFirstVisibleOption(page);
		await page.locator('[data-customization-key="color_notes"]').fill("Reflex Gold and Navy");
		await page.locator('[data-customization-key="design_notes"]').fill("Frame the stage entrance.");
		await page.locator(".js-lt-product-quote-request").click();

		await page.waitForURL(/\/contact/);
		const hiddenPayload = page.locator("#lt_product_quote_payload");
		await expect(hiddenPayload).toHaveValue(/Reflex Gold and Navy/);

		const payload = JSON.parse(await hiddenPayload.inputValue());
		expect(payload.source).toBe("product-page-quote");
		expect(payload.website_item_code).toBe("classic-arch");
		expect(payload.commerce_lane).toBe("quote_first");
		expect(payload.summary).toContain("Requested product page quote");
		expect(payload.summary).toContain("Reflex Gold and Navy");
		expect(payload.summary).toContain("Frame the stage entrance.");
		expect(payload.customizations).toEqual(
			expect.arrayContaining([
				expect.objectContaining({ key: "color_notes", value: "Reflex Gold and Navy" }),
				expect.objectContaining({ key: "design_notes", value: "Frame the stage entrance." }),
			]),
		);
	});

	test(`ready-to-order product page keeps checkout controls and add-ons on ${viewport.name}`, async ({ page }) => {
		await page.setViewportSize({ width: viewport.width, height: viewport.height });
		await primeBrowser(page);
		await page.goto(new URL("/shop-items/bouquets/unicorn-bouquet", BASE_URL).toString(), {
			waitUntil: "domcontentloaded",
		});

		await expect(page.locator(".lt-product__configure")).toBeVisible();
		await expect(page.locator(".lt-product__cart--quote-first")).toHaveCount(0);
		await expect(page.locator(".lt-product__addons")).toBeVisible();
		const architecture = await expectArchitectureContract(page, "checkout");
		expect(architecture.controls.some((control) => control.payload_target === "selected_options")).toBe(true);
		expect(architecture.controls.some((control) => control.payload_target === "add_ons")).toBe(true);
		await expectNoHorizontalOverflow(page);
		await chooseReadyToOrderOption(page);
		await expect(page.locator("#lt-add-to-cart-variant")).toBeEnabled();
	});

	test(`source-backed checkout color axes stay color recipes on ${viewport.name}`, async ({ page }) => {
		await page.setViewportSize({ width: viewport.width, height: viewport.height });
		await primeBrowser(page);
		await page.goto(new URL("/shop-items/columns/7-butterfly-column", BASE_URL).toString(), {
			waitUntil: "domcontentloaded",
		});

		await expect(page.locator(".lt-product__configure")).toBeVisible();
		const architecture = await expectArchitectureContract(page, "checkout");
		const colorControl = architecture.controls.find((control) => control.axis_name === "latex colors");
		expect(colorControl).toEqual(
			expect.objectContaining({
				role: "customization",
				payload_target: "color_recipes",
				selector_type: "multi_color_recipe_builder",
				source: "combined",
			}),
		);
		await expect(page.locator('.lt-product__attr[data-payload-target="color_recipes"]')).toBeVisible();
		await expectNoHorizontalOverflow(page);
		await chooseFirstColorRecipeOption(page);
		await expect(page.locator("#lt-add-to-cart-variant")).toBeEnabled();
		await page.locator("#lt-add-to-cart-variant").click();

		const cart = await page.evaluate(() => JSON.parse(window.localStorage.getItem("lt_cart") || "{}"));
		expect(cart.items).toHaveLength(1);
		const configuration = cart.items[0].configuration;
		expect(configuration.selected_options).toEqual({});
		expect(configuration.color_recipes).toEqual([
			expect.objectContaining({
				axis: "latex colors",
				values: expect.arrayContaining(["Reflex Champage"]),
			}),
		]);
	});
}
