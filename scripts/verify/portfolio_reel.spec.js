const { test, expect } = require("@playwright/test");
const {
	gotoAndSettle,
	auditPageLayout,
	expectNoLayoutFailures,
} = require("./layout_helpers");

async function expectSuccessfulResponse(response, path) {
	expect(response, `${path} should return a response`).not.toBeNull();
	expect(response.status(), `${path} HTTP status`).toBeLessThan(400);
}

test.describe("portfolio proof reel", () => {
	test("desktop renders the approved whole-photo reel with optimized assets", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 768 });
		const response = await gotoAndSettle(page, "/portfolio");
		await expectSuccessfulResponse(response, "/portfolio");
		await page.waitForSelector(".lt-photo");
		await page.waitForTimeout(250);

		const facts = await page.evaluate(() => {
			const root = document.querySelector("[data-portfolio]");
			const reel = document.querySelector("[data-reel]");
			const photos = Array.from(document.querySelectorAll(".lt-photo"));
			const first = photos[0];
			const second = photos[1];
			const third = photos[2];
			const firstImage = first ? first.querySelector("img") : null;
			const firstStyle = first ? window.getComputedStyle(first) : null;
			const imageStyle = firstImage ? window.getComputedStyle(firstImage) : null;
			const rect = first ? first.getBoundingClientRect() : null;
			return {
				hasRoot: Boolean(root),
				hasReel: Boolean(reel),
				headingText: document.querySelector(".lt-title")?.textContent || "",
				metaCount: document.querySelectorAll(".lt-meta > div").length,
				photoCount: photos.length,
				firstPosition: firstStyle ? firstStyle.position : null,
				firstWidth: rect ? Math.round(rect.width) : 0,
				firstHeight: rect ? Math.round(rect.height) : 0,
				firstLeftStyle: first ? first.style.left : "",
				firstTop: rect ? Math.round(rect.top) : 9999,
				firstLeft: rect ? Math.round(rect.left) : 9999,
				secondWidth: second ? Math.round(second.getBoundingClientRect().width) : 0,
				thirdTop: third ? Math.round(parseFloat(third.style.top || "0")) : 0,
				firstSide: first ? first.dataset.side : "",
				secondSide: second ? second.dataset.side : "",
				thirdSide: third ? third.dataset.side : "",
				imageObjectFit: imageStyle ? imageStyle.objectFit : null,
				imageSrc: firstImage ? firstImage.currentSrc || firstImage.src : "",
				imageWidthAttr: firstImage ? firstImage.getAttribute("width") : null,
				imageHeightAttr: firstImage ? firstImage.getAttribute("height") : null,
				visibleCaptionCount: Array.from(document.querySelectorAll(".lt-cap"))
					.filter((caption) => {
						const style = window.getComputedStyle(caption);
						return style.visibility !== "hidden" && Number.parseFloat(style.opacity || "0") > 0.5;
					}).length,
			};
		});

		expect(facts.hasRoot).toBe(true);
		expect(facts.hasReel).toBe(true);
		expect(facts.headingText).toContain("Balloon installations");
		expect(facts.headingText).toContain("for the room you remember.");
		expect(facts.metaCount).toBe(3);
		expect(facts.photoCount).toBeGreaterThanOrEqual(15);
		expect(facts.firstPosition).toBe("absolute");
		expect(facts.firstSide).toBe("left");
		expect(facts.secondSide).toBe("right");
		expect(facts.thirdSide).toBe("left");
		expect(facts.firstWidth).toBeGreaterThan(390);
		expect(facts.firstWidth).toBeLessThan(500);
		expect(Number.parseFloat(facts.firstLeftStyle)).toBeGreaterThanOrEqual(1);
		expect(Number.parseFloat(facts.firstLeftStyle)).toBeLessThanOrEqual(14);
		expect(facts.firstTop).toBeLessThan(768);
		expect(facts.firstLeft).toBeLessThan(80);
		expect(facts.secondWidth - facts.firstWidth).toBeGreaterThan(60);
		expect(facts.thirdTop).toBeGreaterThan(360);
		expect(facts.imageObjectFit).toBe("contain");
		expect(facts.imageSrc).toContain("/optimized/");
		expect(facts.imageSrc).toContain(".webp");
		expect(Number(facts.imageWidthAttr)).toBeGreaterThan(0);
		expect(Number(facts.imageHeightAttr)).toBeGreaterThan(0);
		expect(facts.visibleCaptionCount).toBe(0);

		await page.locator(".lt-photo").first().click({ force: true });
		await expect(page.locator(".lt-photo.is-front")).toHaveCount(1);
		await expect(page.locator(".lt-photo.is-front .lt-cap")).toHaveCSS("visibility", "visible");

		const result = await auditPageLayout(page, {
			targetSelectors: [".lt-photo.is-front"],
		});
		expectNoLayoutFailures(expect, result, "portfolio proof reel desktop");
	});

	test("mobile stacks full-width natural-ratio photos without horizontal overflow", async ({ page }) => {
		await page.setViewportSize({ width: 375, height: 812 });
		const response = await gotoAndSettle(page, "/portfolio");
		await expectSuccessfulResponse(response, "/portfolio");
		await page.waitForSelector(".lt-photo");
		await page.waitForTimeout(250);

		const facts = await page.evaluate(() => {
			const first = document.querySelector(".lt-photo");
			const firstImage = first ? first.querySelector("img") : null;
			const photoStyle = first ? window.getComputedStyle(first) : null;
			const imageStyle = firstImage ? window.getComputedStyle(firstImage) : null;
			const docWidth = Math.max(
				document.documentElement.scrollWidth,
				document.body ? document.body.scrollWidth : 0,
			);
			return {
				photoPosition: photoStyle ? photoStyle.position : null,
				photoWidth: first ? Math.round(first.getBoundingClientRect().width) : 0,
				imageObjectFit: imageStyle ? imageStyle.objectFit : null,
				docWidth,
				viewportWidth: document.documentElement.clientWidth,
			};
		});

		expect(facts.photoPosition).toBe("relative");
		expect(facts.photoWidth).toBeGreaterThanOrEqual(facts.viewportWidth - 42);
		expect(facts.photoWidth).toBeLessThanOrEqual(facts.viewportWidth - 38);
		expect(facts.imageObjectFit).toBe("contain");
		expect(facts.docWidth).toBeLessThanOrEqual(facts.viewportWidth + 2);

		const result = await auditPageLayout(page, {
			targetSelectors: [".lt-photo"],
		});
		expectNoLayoutFailures(expect, result, "portfolio proof reel mobile");
	});

	test("category query links still filter the collage source", async ({ page }) => {
		await page.setViewportSize({ width: 1280, height: 900 });
		const response = await gotoAndSettle(page, "/portfolio?category=balloon-arches");
		await expectSuccessfulResponse(response, "/portfolio?category=balloon-arches");
		await page.waitForSelector(".lt-photo");

		const facts = await page.evaluate(() => {
			const photos = Array.from(document.querySelectorAll(".lt-photo"));
			return {
				count: photos.length,
				categories: Array.from(new Set(photos.map((photo) => photo.dataset.category))),
			};
		});

		expect(facts.count).toBeGreaterThan(0);
		expect(facts.count).toBeLessThan(15);
		expect(facts.categories).toEqual(["balloon-arches"]);

		const emptyResponse = await gotoAndSettle(page, "/portfolio?category=balloon-drops");
		await expectSuccessfulResponse(emptyResponse, "/portfolio?category=balloon-drops");
		await expect(page.locator(".lt-portfolio__empty")).toBeVisible();
		await expect(page.locator(".lt-photo")).toHaveCount(0);
	});

	test("desktop scroll preserves reference edge-bleed collage instead of safe rows", async ({ page }) => {
		await page.setViewportSize({ width: 1366, height: 768 });
		const response = await gotoAndSettle(page, "/portfolio");
		await expectSuccessfulResponse(response, "/portfolio");
		await page.waitForSelector(".lt-photo");

		const before = await page.evaluate(() => {
			const first = document.querySelector(".lt-photo");
			return {
				transform: first ? first.style.transform : "",
				opacity: first ? Number.parseFloat(first.style.opacity || "0") : 0,
			};
		});

		await page.mouse.wheel(0, 700);
		await page.waitForTimeout(1200);

		const after = await page.evaluate(() => {
			const photos = Array.from(document.querySelectorAll(".lt-photo"));
			const visible = photos
				.map((photo) => {
					const rect = photo.getBoundingClientRect();
					return {
						left: Math.round(rect.left),
						top: Math.round(rect.top),
						width: Math.round(rect.width),
						height: Math.round(rect.height),
						visible: rect.bottom > 0 && rect.top < window.innerHeight,
						transform: photo.style.transform,
						opacity: Number.parseFloat(photo.style.opacity || "0"),
						side: photo.dataset.side,
					};
				})
				.filter((photo) => photo.visible);
			return {
				firstTransform: photos[0] ? photos[0].style.transform : "",
				firstOpacity: photos[0] ? Number.parseFloat(photos[0].style.opacity || "0") : 0,
				firstLeft: photos[0] ? Math.round(photos[0].getBoundingClientRect().left) : 9999,
				secondLeft: photos[1] ? Math.round(photos[1].getBoundingClientRect().left) : 0,
				thirdLeft: photos[2] ? Math.round(photos[2].getBoundingClientRect().left) : 9999,
				visible,
			};
		});

		expect(after.firstTransform).not.toBe(before.transform);
		expect(after.firstOpacity).toBeGreaterThan(before.opacity);
		expect(after.visible.length).toBeGreaterThanOrEqual(3);
		expect(Math.max(...after.visible.map((photo) => photo.width))).toBeLessThan(760);
		expect(new Set(after.visible.map((photo) => photo.top)).size).toBeGreaterThan(2);
		expect(after.firstLeft).toBeLessThan(40);
		expect(after.secondLeft).toBeGreaterThan(780);
		expect(after.thirdLeft).toBeLessThan(20);
		expectNoLayoutFailures(expect, await auditPageLayout(page, {
			targetSelectors: [".lt-portfolio", ".lt-reel"],
		}), "portfolio staggered scroll state");
	});
});
