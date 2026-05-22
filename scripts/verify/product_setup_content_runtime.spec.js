const { test, expect } = require("@playwright/test");
const path = require("path");

test("Product Setup copy rules swap title and product copy by selection", async ({ page }) => {
	const runtimePath = path.resolve(
		"apps/locally_twisted/locally_twisted/public/js/lt-product-setup-runtime.js"
	);
	await page.setContent(`
		<h1 class="lt-product__title js-lt-product-title" data-lt-default-text="Default Proof Title">Default Proof Title</h1>
		<div class="lt-product__brand-description js-lt-product-story" data-lt-copy-wrapper><p>Default story.</p></div>
		<section class="lt-product__details-section" data-lt-copy-wrapper>
			<div class="lt-product__details-body js-lt-product-details"><p>Default details.</p></div>
		</section>
		<form class="lt-product__configure">
			<div class="lt-product__attr" data-attribute-name="Proof Size">
				<label><input class="js-lt-attr-input" type="radio" name="proof-size" value="Small"> Small</label>
				<label><input class="js-lt-attr-input" type="radio" name="proof-size" value="Large"> Large</label>
			</div>
			<div class="lt-product__setup-groups js-lt-product-setup-groups"></div>
		</form>
		<script type="application/json" class="js-lt-product-setup-schema">
			{
				"source": "lt_product_setup",
				"selection_groups": [],
				"media_rules": [],
				"content_rules": [
					{
						"rule_type": "Selection group",
						"selection_group": "Proof Size",
						"selection_value": "Large",
						"display_title": "Large Proof Title",
						"product_story": "<p>Large story.</p>",
						"product_details": "<p>Large details.</p>",
						"approved_for_customer": true
					}
				]
			}
		</script>
	`);
	await page.addScriptTag({ path: runtimePath });

	await page.locator("input[value='Large']").check();
	await page.evaluate(() => {
		window.LT_PRODUCT_SETUP.applySelectedContent(document.querySelector(".lt-product__configure"), "");
	});
	await expect(page.locator(".js-lt-product-title")).toHaveText("Large Proof Title");
	await expect(page.locator(".js-lt-product-story")).toContainText("Large story.");
	await expect(page.locator(".js-lt-product-details")).toContainText("Large details.");

	await page.locator("input[value='Small']").check();
	await page.evaluate(() => {
		window.LT_PRODUCT_SETUP.applySelectedContent(document.querySelector(".lt-product__configure"), "");
	});
	await expect(page.locator(".js-lt-product-title")).toHaveText("Default Proof Title");
	await expect(page.locator(".js-lt-product-story")).toContainText("Default story.");
	await expect(page.locator(".js-lt-product-details")).toContainText("Default details.");
});
