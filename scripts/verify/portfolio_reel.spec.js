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
			const fourth = photos[3];
			const firstImage = first ? first.querySelector("img") : null;
			const firstStyle = first ? window.getComputedStyle(first) : null;
			const imageStyle = firstImage ? window.getComputedStyle(firstImage) : null;
			const frame = first ? first.querySelector(".lt-frame") : null;
			const frameStyle = frame ? window.getComputedStyle(frame) : null;
			const rect = first ? first.getBoundingClientRect() : null;
			const heroRect = document.querySelector(".lt-portfolio__hero")?.getBoundingClientRect();
			const reelRect = reel ? reel.getBoundingClientRect() : null;
			const bodyFontFamily = window.getComputedStyle(document.body).fontFamily;
			const rootStyle = root ? window.getComputedStyle(root) : null;
			const primaryButton = document.querySelector(".lt-portfolio__button:not(.lt-portfolio__button--secondary)");
			const primaryButtonStyle = primaryButton ? window.getComputedStyle(primaryButton) : null;
			return {
				hasRoot: Boolean(root),
				hasReel: Boolean(reel),
				headingText: document.querySelector(".lt-portfolio__title")?.textContent || "",
				heroText: document.querySelector(".lt-portfolio__hero")?.innerText.replace(/\s+/g, " ").trim() || "",
				heroHeight: heroRect ? Math.round(heroRect.height) : 0,
				heroBottom: heroRect ? Math.round(heroRect.bottom) : 0,
				reelTop: reelRect ? Math.round(reelRect.top) : 0,
				internalNavCount: document.querySelectorAll(".lt-head, .lt-nav").length,
				fontLinkCount: document.querySelectorAll('link[href*="fonts.googleapis"]').length,
				cursorDotCount: document.querySelectorAll(".lt-cursor-dot, .lt-cursor-ring").length,
				rootCursor: rootStyle ? rootStyle.cursor : "",
				rootFontFamily: rootStyle ? rootStyle.fontFamily : "",
				bodyFontFamily,
				backgroundColor: window.getComputedStyle(root).backgroundColor,
				frameBackgroundColor: frameStyle ? frameStyle.backgroundColor : "",
				imageBackgroundColor: imageStyle ? imageStyle.backgroundColor : "",
				primaryButtonText: primaryButton ? primaryButton.innerText.trim() : "",
				primaryButtonColor: primaryButtonStyle ? primaryButtonStyle.color : "",
				primaryButtonTextFill: primaryButtonStyle ? primaryButtonStyle.webkitTextFillColor : "",
				primaryButtonBackground: primaryButtonStyle ? primaryButtonStyle.backgroundColor : "",
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
				fourthSide: fourth ? fourth.dataset.side : "",
				fourthWidth: fourth ? Math.round(fourth.getBoundingClientRect().width) : 0,
				fourthLeft: fourth ? Math.round(fourth.getBoundingClientRect().left) : 0,
				fourthTop: fourth ? Math.round(Number.parseFloat(fourth.style.top || "0")) : 0,
				imageObjectFit: imageStyle ? imageStyle.objectFit : null,
				imageSrc: firstImage ? firstImage.currentSrc || firstImage.src : "",
				imageWidthAttr: firstImage ? firstImage.getAttribute("width") : null,
				imageHeightAttr: firstImage ? firstImage.getAttribute("height") : null,
				visibleCaptionCount: document.querySelectorAll(".lt-cap").length,
			};
		});

		expect(facts.hasRoot).toBe(true);
		expect(facts.hasReel).toBe(true);
		expect(facts.headingText).toContain("Real balloon installs for Utah events.");
		expect(facts.heroText).toContain("Corporate entrances, school stages, civic celebrations, and private moments");
		expect(facts.heroText).toMatch(/start an event inquiry/i);
		expect(facts.heroHeight).toBe(280);
		expect(facts.internalNavCount, "the portfolio should use the shared site chrome, not a copied internal page shell").toBe(0);
		expect(facts.fontLinkCount, "portfolio should rely on the sitewide LT brand fonts").toBe(0);
		expect(facts.cursorDotCount, "portfolio should not mount prototype cursor artifacts").toBe(0);
		expect(facts.rootCursor).not.toBe("none");
		expect(facts.rootFontFamily).toContain("Lato");
		expect(facts.bodyFontFamily).toContain("Lato");
		expect(facts.backgroundColor).toBe("rgb(250, 247, 242)");
		expect(facts.frameBackgroundColor).toBe("rgb(255, 255, 255)");
		expect(facts.imageBackgroundColor).toBe("rgb(250, 247, 242)");
		expect(facts.primaryButtonText).toMatch(/start an event inquiry/i);
		expect(facts.primaryButtonColor, "primary portfolio CTA text should contrast against its white background").toBe("rgb(14, 34, 64)");
		expect(facts.primaryButtonTextFill, "primary portfolio CTA should not inherit white text-fill from the dark hero").toBe("rgb(14, 34, 64)");
		expect(facts.primaryButtonBackground).toBe("rgb(255, 255, 255)");
		expect(facts.photoCount).toBeGreaterThanOrEqual(15);
		expect(facts.centerCount).toBeGreaterThanOrEqual(2);
		expect(facts.firstPosition).toBe("absolute");
		expect(facts.firstSide).toBe("left");
		expect(facts.secondSide).toBe("right");
		expect(facts.thirdSide).toBe("left");
		expect(facts.fourthSide).toBe("center");
		expect(facts.firstWidth).toBeGreaterThan(420);
		expect(facts.firstWidth).toBeLessThan(455);
		expect(Number.parseFloat(facts.firstLeftStyle)).toBeGreaterThanOrEqual(1);
		expect(Number.parseFloat(facts.firstLeftStyle)).toBeLessThanOrEqual(3);
		expect(facts.firstHeight / facts.firstWidth).toBeCloseTo(1.25, 1);
		expect(facts.firstOpacity).toBeLessThan(0.1);
		expect(facts.firstLeft).toBeLessThan(-250);
		expect(facts.reelTop, "the collage should begin immediately after the compact branded portfolio hero").toBeGreaterThanOrEqual(facts.heroBottom - 1);
		expect(facts.firstTop).toBeGreaterThan(facts.reelTop);
		expect(facts.firstTop).toBeLessThan(facts.reelTop + 160);
		expect(facts.secondWidth - facts.firstWidth).toBeGreaterThan(70);
		expect(facts.thirdWidth).toBeGreaterThan(395);
		expect(facts.thirdWidth).toBeLessThan(425);
		expect(facts.thirdTop).toBeGreaterThan(350);
		expect(facts.fourthWidth).toBeGreaterThan(630);
		expect(facts.fourthWidth).toBeLessThan(670);
		expect(facts.fourthLeft).toBeGreaterThan(330);
		expect(facts.fourthLeft).toBeLessThan(390);
		expect(facts.fourthTop).toBeGreaterThan(880);
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
		expect(before.opacity).toBeLessThan(0.1);
		expect(after.firstOpacity).toBe(1);
		expect(after.visible.length).toBeGreaterThanOrEqual(3);
		expect(Math.max(...after.visible.map((photo) => photo.width))).toBeGreaterThan(500);
		expect(after.visible.some((photo) => photo.side === "center")).toBe(true);
		expect(after.visible.some((photo) => photo.side === "left")).toBe(true);
		expect(after.visible.some((photo) => photo.side === "right")).toBe(true);
		expect(new Set(after.visible.map((photo) => photo.top)).size).toBeGreaterThanOrEqual(2);
		expectNoLayoutFailures(expect, await auditPageLayout(page, {
			targetSelectors: [".lt-portfolio", ".lt-reel"],
		}), "portfolio staggered scroll state");
	});
});
