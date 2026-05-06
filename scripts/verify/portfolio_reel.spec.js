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
			const frame = first ? first.querySelector(".lt-frame") : null;
			const frameStyle = frame ? window.getComputedStyle(frame) : null;
			const rect = first ? first.getBoundingClientRect() : null;
			const heroRect = document.querySelector(".lt-portfolio-hero")?.getBoundingClientRect();
			const headerRect = document.querySelector(".navbar, header, .web-header")?.getBoundingClientRect();
			const bodyFontFamily = window.getComputedStyle(document.body).fontFamily;
			const rootStyle = root ? window.getComputedStyle(root) : null;
			return {
				hasRoot: Boolean(root),
				hasReel: Boolean(reel),
				headingText: document.querySelector(".lt-title")?.textContent || "",
				heroCopy: document.querySelector(".lt-hero-copy")?.textContent || "",
				heroHeight: heroRect ? Math.round(heroRect.height) : 0,
				headerHeight: headerRect ? Math.round(headerRect.height) : 0,
				fontLinkCount: document.querySelectorAll('link[href*="fonts.googleapis"]').length,
				cursorDotCount: document.querySelectorAll(".lt-cursor-dot, .lt-cursor-ring").length,
				rootCursor: rootStyle ? rootStyle.cursor : "",
				rootFontFamily: rootStyle ? rootStyle.fontFamily : "",
				bodyFontFamily,
				backgroundColor: window.getComputedStyle(root).backgroundColor,
				frameBackgroundColor: frameStyle ? frameStyle.backgroundColor : "",
				imageBackgroundColor: imageStyle ? imageStyle.backgroundColor : "",
				photoCount: photos.length,
				centerCount: photos.filter((photo) => photo.dataset.side === "center").length,
				firstPosition: firstStyle ? firstStyle.position : null,
				firstWidth: rect ? Math.round(rect.width) : 0,
				firstHeight: rect ? Math.round(rect.height) : 0,
				firstOpacity: firstStyle ? Number.parseFloat(firstStyle.opacity || "0") : 0,
				firstLeftStyle: first ? first.style.left : "",
				firstTop: rect ? Math.round(rect.top) : 9999,
				firstLeft: rect ? Math.round(rect.left) : 9999,
				secondWidth: second ? Math.round(second.getBoundingClientRect().width) : 0,
				thirdTop: third ? Math.round(parseFloat(third.style.top || "0")) : 0,
				firstSide: first ? first.dataset.side : "",
				secondSide: second ? second.dataset.side : "",
				thirdSide: third ? third.dataset.side : "",
				thirdWidth: third ? Math.round(third.getBoundingClientRect().width) : 0,
				thirdLeft: third ? Math.round(third.getBoundingClientRect().left) : 0,
				imageObjectFit: imageStyle ? imageStyle.objectFit : null,
				imageSrc: firstImage ? firstImage.currentSrc || firstImage.src : "",
				imageWidthAttr: firstImage ? firstImage.getAttribute("width") : null,
				imageHeightAttr: firstImage ? firstImage.getAttribute("height") : null,
				visibleCaptionCount: document.querySelectorAll(".lt-cap").length,
			};
		});

		expect(facts.hasRoot).toBe(true);
		expect(facts.hasReel).toBe(true);
		expect(facts.headingText.trim()).toBe("What We Do");
		expect(facts.heroCopy).toContain("Utah");
		expect(facts.heroCopy).toContain("balloon decor");
		expect(facts.heroHeight).toBeGreaterThan(225);
		expect(facts.heroHeight).toBeLessThanOrEqual(Math.max(330, facts.headerHeight * 3));
		expect(facts.fontLinkCount).toBe(0);
		expect(facts.cursorDotCount).toBe(0);
		expect(facts.rootCursor).not.toBe("none");
		expect(facts.rootFontFamily).toBe(facts.bodyFontFamily);
		expect(facts.backgroundColor).not.toBe("rgb(248, 244, 237)");
		expect(facts.frameBackgroundColor).toBe(facts.backgroundColor);
		expect(facts.imageBackgroundColor).toBe(facts.backgroundColor);
		expect(facts.photoCount).toBeGreaterThanOrEqual(15);
		expect(facts.centerCount).toBeGreaterThanOrEqual(4);
		expect(facts.firstPosition).toBe("absolute");
		expect(facts.firstSide).toBe("left");
		expect(facts.secondSide).toBe("right");
		expect(facts.thirdSide).toBe("center");
		expect(facts.firstWidth).toBeGreaterThan(830);
		expect(facts.firstWidth).toBeLessThan(900);
		expect(Number.parseFloat(facts.firstLeftStyle)).toBeGreaterThanOrEqual(-4);
		expect(Number.parseFloat(facts.firstLeftStyle)).toBeLessThanOrEqual(8);
		expect(facts.firstHeight / facts.firstWidth).toBeCloseTo(1.25, 1);
		expect(facts.firstOpacity).toBeGreaterThan(0.85);
		expect(facts.firstLeft).toBeGreaterThan(-80);
		expect(facts.firstLeft).toBeLessThan(60);
		expect(facts.firstTop).toBeLessThan(540);
		expect(facts.secondWidth - facts.firstWidth).toBeGreaterThan(140);
		expect(facts.thirdWidth).toBeGreaterThan(1200);
		expect(facts.thirdWidth).toBeLessThan(1300);
		expect(facts.thirdLeft).toBeGreaterThan(20);
		expect(facts.thirdLeft).toBeLessThan(90);
		expect(facts.thirdTop).toBeLessThan(90);
		expect(facts.imageObjectFit).toBe("contain");
		expect(facts.imageSrc).toContain("/optimized/");
		expect(facts.imageSrc).toContain(".webp");
		expect(Number(facts.imageWidthAttr)).toBeGreaterThan(0);
		expect(Number(facts.imageHeightAttr)).toBeGreaterThan(0);
		expect(facts.visibleCaptionCount).toBe(facts.photoCount);

		await page.locator(".lt-photo").first().click({ force: true });
		await expect(page.locator(".lt-photo.is-front")).toHaveCount(1);

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

	test("desktop scroll keeps the larger edge and center collage rhythm", async ({ page }) => {
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

		await page.evaluate(() => window.scrollTo(0, 1500));
		await page.waitForTimeout(1400);

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
				firstTop: photos[0] ? Math.round(photos[0].getBoundingClientRect().top) : 9999,
				secondLeft: photos[1] ? Math.round(photos[1].getBoundingClientRect().left) : 0,
				secondTop: photos[1] ? Math.round(photos[1].getBoundingClientRect().top) : 9999,
				thirdLeft: photos[2] ? Math.round(photos[2].getBoundingClientRect().left) : 9999,
				visible,
			};
		});

		expect(after.firstTransform).not.toBe(before.transform);
		expect(before.opacity).toBe(1);
		expect(after.firstOpacity).toBe(1);
		expect(after.visible.length).toBeGreaterThanOrEqual(3);
		expect(Math.max(...after.visible.map((photo) => photo.width))).toBeGreaterThan(850);
		expect(after.visible.some((photo) => photo.side === "center")).toBe(true);
		expect(after.visible.some((photo) => photo.side === "left")).toBe(true);
		expect(after.visible.some((photo) => photo.side === "right")).toBe(true);
		expect(new Set(after.visible.map((photo) => photo.top)).size).toBeGreaterThanOrEqual(2);
		expectNoLayoutFailures(expect, await auditPageLayout(page, {
			targetSelectors: [".lt-portfolio", ".lt-reel"],
		}), "portfolio staggered scroll state");
	});
});
