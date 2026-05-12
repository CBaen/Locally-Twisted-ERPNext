#!/usr/bin/env node
/*
 * Focused post-import checkout proof for the corrected V1 catalog subset.
 *
 * This is intentionally a direct Node + Playwright script because the repo
 * @playwright/test runner has hung in this environment before page assertions.
 *
 * Run after the corrected purge/re-import is complete:
 *   "C:\Program Files\nodejs\node.exe" scripts/verify/post_import_checkout_proof.js
 */
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const BASE_URL = process.env.LT_BASE_URL || "http://localhost:8081";
const CHROME_PATH =
	process.env.PLAYWRIGHT_CHROME_PATH ||
	"C:/Program Files/Google/Chrome/Application/chrome.exe";
const OUT_DIR = path.join(process.cwd(), "output", "playwright");
const REPORT_PATH = path.join(OUT_DIR, "post-import-checkout-proof.json");

const PRODUCTS = [
	{
		label: "Easter Balloon Cups",
		route: "/shop-items/seasonal-specialty/easter-balloon-cups",
		expectedTemplate: "easter-balloon-cups",
	},
	{
		label: "7' Butterfly Column",
		route: "/shop-items/columns/7-butterfly-column",
		expectedTemplate: "7-butterfly-column",
	},
	{
		label: "Graduation Grab n Go",
		route: "/shop-items/grab-go/graduation-grab-n-go",
		expectedTemplate: "graduation-grab-n-go",
	},
	{
		label: "6' Graduation stands",
		route: "/shop-items/stands-easels/6-graduation-stands",
		expectedTemplate: "6-graduation-stands",
	},
	{
		label: "Unicorn Bouquet",
		route: "/shop-items/bouquets/unicorn-bouquet",
		expectedTemplate: "unicorn-bouquet",
	},
];

function fail(message) {
	const error = new Error(message);
	error.proofFailure = true;
	throw error;
}

function hasMoney(text) {
	return /\$\s*\d|\d+\.\d{2}/.test(text || "");
}

async function visibleText(locator) {
	if ((await locator.count()) === 0) return "";
	return (await locator.first().innerText().catch(() => "")).trim();
}

async function gotoOk(page, route) {
	const response = await page.goto(BASE_URL + route, {
		waitUntil: "domcontentloaded",
		timeout: 20000,
	});
	if (!response) fail(`${route} did not return a browser response`);
	if (response.status() >= 400) fail(`${route} returned HTTP ${response.status()}`);
	await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
	return response.status();
}

async function waitForCartRendered(page) {
	await page.waitForSelector(
		"#lt-cart-populated:not([hidden]), #lt-cart-empty:not([hidden]), #lt-cart-error:not([hidden])",
		{ timeout: 20000 },
	);
	if ((await page.locator("#lt-cart-error:not([hidden])").count()) > 0) {
		const errorText = await visibleText(page.locator("#lt-cart-error"));
		fail(`/cart rendered error state: ${errorText}`);
	}
	if ((await page.locator("#lt-cart-empty:not([hidden])").count()) > 0) {
		fail("/cart rendered empty state after products were added");
	}
}

async function waitForCheckoutSummaryRendered(page) {
	if ((await page.locator("#lt-checkout-summary-loading").count()) === 0) return;
	await page.waitForSelector(
		"#lt-checkout-summary-subtotal-row:not([hidden]), #lt-checkout-summary-empty:not([hidden]), #lt-checkout-summary-error:not([hidden])",
		{ timeout: 20000 },
	);
	if ((await page.locator("#lt-checkout-summary-error:not([hidden])").count()) > 0) {
		const errorText = await visibleText(page.locator("#lt-checkout-summary-error"));
		fail(`/checkout rendered cart summary error state: ${errorText}`);
	}
	if ((await page.locator("#lt-checkout-summary-empty:not([hidden])").count()) > 0) {
		fail("/checkout rendered empty cart summary after products were added");
	}
}

async function firstVisibleEnabled(locator) {
	const count = await locator.count();
	for (let i = 0; i < count; i += 1) {
		const candidate = locator.nth(i);
		if ((await candidate.isVisible().catch(() => false)) && (await candidate.isEnabled().catch(() => false))) {
			return candidate;
		}
	}
	return null;
}

function hasSelectionProof(selectionProof) {
	return (
		Object.keys(selectionProof.selectedOptions || {}).length > 0 ||
		(selectionProof.colorDrawers || []).length > 0
	);
}

async function chooseFirstOptionForEachAttribute(page) {
	const attrs = page.locator(".lt-product__configure .lt-product__attr");
	const count = await attrs.count();
	const selectionProof = {
		selectedOptions: {},
		colorDrawers: [],
	};
	for (let i = 0; i < count; i += 1) {
		const attr = attrs.nth(i);
		const name = await attr.getAttribute("data-attribute-name");
		if (!name) continue;

		const displayType = (await attr.getAttribute("data-display-type")) || "";
		if (displayType === "color-drawer") {
			const input = await firstVisibleEnabled(attr.locator(".js-lt-color-radio"));
			if (!input) fail(`No visible enabled color option for ${name}`);
			const value = (await input.getAttribute("value")) || "";
			if (!value) fail(`Color option for ${name} has empty value`);
			const hidden = attr.locator(".js-lt-color-hidden").first();
			if ((await hidden.count()) === 0) fail(`Color drawer for ${name} is missing hidden sync select`);
			await input.check({ force: true });
			await page.waitForFunction(
				({ attrName, expectedValue }) => {
					const attrEl = Array.from(document.querySelectorAll(".lt-product__attr")).find(
						(node) => node.getAttribute("data-attribute-name") === attrName,
					);
					if (!attrEl) return false;
					const checked = attrEl.querySelector(".js-lt-color-radio:checked");
					const hiddenSelect = attrEl.querySelector(".js-lt-color-hidden");
					return checked && checked.value === expectedValue && hiddenSelect && hiddenSelect.value === expectedValue;
				},
				{ attrName: name, expectedValue: value },
				{ timeout: 10000 },
			);
			selectionProof.colorDrawers.push({
				axis: name,
				value,
				hiddenValue: await hidden.inputValue(),
			});
			continue;
		}

		const select = await firstVisibleEnabled(attr.locator("select.js-lt-attr-input:not(.js-lt-color-hidden)"));
		if (select) {
			const value = await select.evaluate((node) => {
				const option = Array.from(node.options).find((candidate) => candidate.value && !candidate.disabled && !candidate.hidden);
				return option ? option.value : "";
			});
			if (!value) fail(`No selectable option for ${name}`);
			await select.selectOption(value);
			selectionProof.selectedOptions[name] = value;
			continue;
		}

		const input = await firstVisibleEnabled(
			attr.locator("input[type='radio']:not(:disabled), input[type='checkbox']:not(:disabled)"),
		);
		if (!input) fail(`No visible enabled option input for ${name}`);
		const value = await input.getAttribute("value");
		await input.check({ force: true });
		selectionProof.selectedOptions[name] = value || "";
	}
	return selectionProof;
}

function assertColorDrawerConfiguration(product, line, colorDrawers) {
	if (!colorDrawers || colorDrawers.length === 0) return;
	if (!line.configuration) fail(`${product.route} cart line missing structured configuration for color drawer`);
	const recipes = Array.isArray(line.configuration.color_recipes) ? line.configuration.color_recipes : [];
	const selectedOptions = line.configuration.selected_options || {};
	for (const expected of colorDrawers) {
		if (Object.prototype.hasOwnProperty.call(selectedOptions, expected.axis)) {
			fail(`${product.route} preserved color drawer axis ${expected.axis} in selected_options`);
		}
		const matchingRecipe = recipes.find((recipe) => {
			const values = Array.isArray(recipe.values) ? recipe.values : [];
			return (
				(recipe.axis === expected.axis || recipe.label === expected.axis) &&
				values.includes(expected.value)
			);
		});
		if (!matchingRecipe) {
			fail(`${product.route} cart line missing color_recipes ${expected.axis}=${expected.value}`);
		}
	}
}

async function assertCheckoutPreviewAcceptsCart(page) {
	const result = await page.evaluate(async () => {
		const cart = window.LT_CART && window.LT_CART.getCart && window.LT_CART.getCart();
		const items = cart && Array.isArray(cart.items) ? cart.items : [];
		const fd = new FormData();
		fd.append("items_json", JSON.stringify(items));
		fd.append("fulfillment_method", "pickup");
		fd.append("pickup_location", "West Jordan");
		const response = await fetch("/api/method/locally_twisted.www.checkout.preview_checkout_totals", {
			method: "POST",
			headers: { "X-Requested-With": "XMLHttpRequest" },
			body: fd,
			credentials: "same-origin",
		});
		let json = null;
		try {
			json = await response.json();
		} catch (err) {
			json = { parse_error: String(err) };
		}
		return {
			httpOk: response.ok,
			status: response.status,
			json,
		};
	});
	if (!result.httpOk) {
		fail(`preview_checkout_totals returned HTTP ${result.status}: ${JSON.stringify(result.json)}`);
	}
	const message = result.json && result.json.message;
	if (!message || message.ok !== true) {
		fail(`preview_checkout_totals did not accept pickup cart: ${JSON.stringify(result.json)}`);
	}
	return message;
}

async function addProductToCart(page, product) {
	await gotoOk(page, product.route);

	const title = await visibleText(page.locator(".lt-product__title"));
	if (!title) fail(`${product.route} missing product title`);

	const image = page.locator(".product-image img.website-image, img.website-image").first();
	if ((await image.count()) === 0) fail(`${product.route} missing product image`);
	const imageBefore = await image.getAttribute("src");
	if (!imageBefore) fail(`${product.route} product image has empty src`);

	const quoteGate = await page.locator(".lt-product__cart--quote-first, .js-lt-product-quote-request").count();
	if (quoteGate > 0) {
		fail(`${product.route} rendered quote-first gate instead of direct checkout controls`);
	}

	const configure = page.locator(".lt-product__configure");
	let selections = {};
	let addButton = page.locator("#lt-add-to-cart-variant");
	let priceBefore = await visibleText(page.locator(".lt-product__price"));
	let itemCode = "";
	let priceAfter = "";
	let imageAfter = imageBefore;
	let selectionProof = { selectedOptions: {}, colorDrawers: [] };

	if ((await configure.count()) > 0) {
		selectionProof = await chooseFirstOptionForEachAttribute(page);
		selections = selectionProof.selectedOptions;
		await page.waitForFunction(
			() => {
				const btn = document.querySelector("#lt-add-to-cart-variant");
				return btn && !btn.disabled && btn.getAttribute("data-item-code");
			},
			null,
			{ timeout: 20000 },
		);
		itemCode = await addButton.getAttribute("data-item-code");
		priceAfter = await visibleText(page.locator("#lt-product-price-text, .lt-product__price"));
		imageAfter = (await image.getAttribute("src")) || "";
	} else {
		addButton = page.locator(".btn-add-to-cart[data-item-code], [data-item-code].btn-add-to-cart").first();
		if ((await addButton.count()) === 0) fail(`${product.route} missing add-to-cart button`);
		itemCode = await addButton.getAttribute("data-item-code");
		priceAfter = priceBefore;
	}

	if (!itemCode) fail(`${product.route} add-to-cart button did not resolve an item code`);
	if (!itemCode.startsWith(product.expectedTemplate)) {
		fail(`${product.route} resolved ${itemCode}, expected ${product.expectedTemplate} template/variant`);
	}
	if (!hasMoney(priceAfter)) fail(`${product.route} did not expose a usable price after selection`);

	await addButton.click();
	await page.waitForFunction(
		(code) => {
			const cart = window.LT_CART && window.LT_CART.getCart && window.LT_CART.getCart();
			return cart && Array.isArray(cart.items) && cart.items.some((line) => line.item_code === code);
		},
		itemCode,
		{ timeout: 10000 },
	);
	const cart = await page.evaluate(() => window.LT_CART.getCart());
	const line = cart.items.find((entry) => entry.item_code === itemCode);
	if (!line) fail(`${product.route} did not preserve ${itemCode} in LT_CART`);
	if (!line.line_key || !line.line_key.startsWith(itemCode + "::")) {
		fail(`${product.route} cart line key does not preserve item code`);
	}
	if (hasSelectionProof(selectionProof)) {
		if (!line.configuration) fail(`${product.route} cart line missing structured configuration`);
		if (line.configuration.schema_version !== "lt-product-config-v1") {
			fail(`${product.route} cart line has wrong configuration schema`);
		}
		if (line.configuration.website_item_code !== product.expectedTemplate) {
			fail(`${product.route} cart line lost website item/template code`);
		}
	}
	assertColorDrawerConfiguration(product, line, selectionProof.colorDrawers);

	return {
		label: product.label,
		route: product.route,
		title,
		itemCode,
		selections,
		colorDrawers: selectionProof.colorDrawers,
		priceBefore,
		priceAfter,
		imageBefore,
		imageAfter,
		cartLine: line,
	};
}

async function assertCartAndCheckout(page, productResults) {
	await gotoOk(page, "/cart");
	if (page.url().includes("/ready-to-order-paused")) fail("/cart redirected to ecommerce pause page");
	await waitForCartRendered(page);
	const cartBody = await page.locator("body").innerText();
	for (const result of productResults) {
		if (!cartBody.includes(result.title) && !cartBody.includes(result.itemCode)) {
			fail(`/cart did not render ${result.label} (${result.itemCode})`);
		}
	}
	if ((await page.locator("#lt-cart-checkout-btn").count()) === 0) {
		fail("/cart missing checkout button");
	}
	const checkoutPreview = await assertCheckoutPreviewAcceptsCart(page);

	await gotoOk(page, "/checkout");
	if (page.url().includes("/ready-to-order-paused")) fail("/checkout redirected to ecommerce pause page");
	if ((await page.locator("#lt-checkout-form").count()) === 0) {
		fail("/checkout missing checkout form");
	}
	await waitForCheckoutSummaryRendered(page);
	const checkoutBody = await page.locator("body").innerText();
	for (const result of productResults) {
		if (!checkoutBody.includes(result.title) && !checkoutBody.includes(result.itemCode)) {
			fail(`/checkout did not preserve ${result.label} (${result.itemCode})`);
		}
	}
	return { checkoutPreview };
}

async function main() {
	fs.mkdirSync(OUT_DIR, { recursive: true });
	const browser = await chromium.launch({
		headless: true,
		executablePath: CHROME_PATH,
		timeout: 15000,
	});
	const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
	const proof = {
		baseUrl: BASE_URL,
		chromePath: CHROME_PATH,
		products: [],
		ok: false,
	};
	try {
		await gotoOk(page, "/");
		await page.evaluate(() => window.LT_CART && window.LT_CART.clear && window.LT_CART.clear());
		for (const product of PRODUCTS) {
			proof.products.push(await addProductToCart(page, product));
		}
		const checkoutProof = await assertCartAndCheckout(page, proof.products);
		proof.checkoutPreview = checkoutProof.checkoutPreview;
		proof.ok = true;
	} finally {
		fs.writeFileSync(REPORT_PATH, JSON.stringify(proof, null, 2) + "\n", "utf8");
		await browser.close();
	}
	console.log(`[POST IMPORT CHECKOUT PROOF] PASS report=${REPORT_PATH}`);
}

main().catch((error) => {
	const message = error && error.stack ? error.stack : String(error);
	console.error(`[POST IMPORT CHECKOUT PROOF] FAIL ${message}`);
	process.exit(1);
});
