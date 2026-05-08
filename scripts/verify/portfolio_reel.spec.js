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
			const rect = first ? first.getBoundingClientRect() : null;
			const imageRect = firstImage ? firstImage.getBoundingClientRect() : null;
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
				imageBackgroundColor: imageStyle ? imageStyle.backgroundColor : "",
				photoBackgroundColor: firstStyle ? firstStyle.backgroundColor : "",
				photoBoxShadow: firstStyle ? firstStyle.boxShadow : "",
				frameCount: document.querySelectorAll(".lt-frame").length,
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
				imageParentClass: firstImage?.parentElement?.className || "",
				imageFillsPhoto:
					rect && imageRect
						? Math.abs(rect.left - imageRect.left) <= 1 &&
							Math.abs(rect.top - imageRect.top) <= 1 &&
							Math.abs(rect.width - imageRect.width) <= 1 &&
							Math.abs(rect.height - imageRect.height) <= 1
						: false,
				imageSrc: firstImage ? firstImage.currentSrc || firstImage.src : "",
				imageWidthAttr: firstImage ? firstImage.getAttribute("width") : null,
				imageHeightAttr: firstImage ? firstImage.getAttribute("height") : null,
				visibleCaptionCount: document.querySelectorAll(".lt-cap, figcaption").length,
				portfolioFooterCount: document.querySelectorAll(".lt-foot").length,
				forbiddenPortfolioFooterText: root
					? ["Inquire", "Studio", "Index", "Selected work", "15 installs", "(801) 285-0860", "Utah events and venues"].filter((text) =>
							root.innerText.includes(text),
						)
					: [],
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
		expect(facts.frameCount, "portfolio photos should not sit inside visible frame/container wrappers").toBe(0);
		expect(facts.photoBackgroundColor, "portfolio photos should not expose white/cream frame stripes").toBe("rgba(0, 0, 0, 0)");
		expect(facts.photoBoxShadow, "portfolio photos should read as the image itself, not a framed card").toBe("none");
		expect(facts.imageBackgroundColor, "image elements should not paint a stripe behind transparent space").toBe("rgba(0, 0, 0, 0)");
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
		expect(facts.firstWidth).toBeGreaterThan(640);
		expect(facts.firstWidth).toBeLessThan(670);
		expect(Number.parseFloat(facts.firstLeftStyle)).toBeGreaterThanOrEqual(1);
		expect(Number.parseFloat(facts.firstLeftStyle)).toBeLessThanOrEqual(3);
		expect(facts.firstHeight / facts.firstWidth).toBeCloseTo(4 / 3, 1);
		expect(facts.firstOpacity).toBeLessThan(0.1);
		expect(facts.firstLeft).toBeLessThan(-250);
		expect(facts.reelTop, "the collage should begin immediately after the compact branded portfolio hero").toBeGreaterThanOrEqual(facts.heroBottom - 1);
		expect(facts.firstTop).toBeGreaterThan(facts.reelTop);
		expect(facts.firstTop).toBeLessThan(facts.reelTop + 160);
		expect(facts.secondWidth - facts.firstWidth).toBeGreaterThan(110);
		expect(facts.thirdWidth).toBeGreaterThan(600);
		expect(facts.thirdWidth).toBeLessThan(630);
		expect(facts.thirdTop, "larger photos should keep the older looser reel spacing instead of using higher visual density").toBeGreaterThan(540);
		expect(facts.thirdTop).toBeLessThan(570);
		expect(facts.fourthWidth).toBeGreaterThan(950);
		expect(facts.fourthWidth).toBeLessThan(995);
		expect(facts.fourthLeft).toBeGreaterThan(170);
		expect(facts.fourthLeft).toBeLessThan(230);
		expect(facts.fourthTop, "center statements should keep breathing room after photo scale is increased").toBeGreaterThan(1160);
		expect(facts.fourthTop).toBeLessThan(1210);
		expect(facts.imageParentClass).toContain("lt-photo");
		expect(facts.imageFillsPhoto, "image rect should be the photo rect, with no letterbox frame around it").toBe(true);
		expect(facts.imageSrc).toContain("/optimized/");
		expect(facts.imageSrc).toContain(".webp");
		expect(Number(facts.imageWidthAttr)).toBeGreaterThan(0);
		expect(Number(facts.imageHeightAttr)).toBeGreaterThan(0);
		expect(facts.visibleCaptionCount, "GL rejected captions on portfolio photos").toBe(0);
		expect(facts.portfolioFooterCount, "GL rejected the extra portfolio footer/contact/index section").toBe(0);
		expect(facts.forbiddenPortfolioFooterText, "portfolio should not render the removed footer section labels").toEqual([]);

		await page.locator(".lt-photo").first().click({ force: true });
		await expect(page.locator(".lt-photo.is-front")).toHaveCount(1);

		const result = await auditPageLayout(page, {
			targetSelectors: [".lt-photo.is-front"],
		});
		expectNoLayoutFailures(expect, result, "portfolio proof reel desktop");
	});

	test("mobile slides full-width natural-ratio photos into view without horizontal overflow", async ({ page }) => {
		await page.setViewportSize({ width: 375, height: 812 });
		const response = await gotoAndSettle(page, "/portfolio");
		await expectSuccessfulResponse(response, "/portfolio");
		await page.waitForSelector(".lt-photo");
		await page.waitForTimeout(350);

		const facts = await page.evaluate(() => {
			const first = document.querySelector(".lt-photo");
			const second = document.querySelectorAll(".lt-photo")[1];
			const firstImage = first ? first.querySelector("img") : null;
			const photoStyle = first ? window.getComputedStyle(first) : null;
			const secondStyle = second ? window.getComputedStyle(second) : null;
			const imageStyle = firstImage ? window.getComputedStyle(firstImage) : null;
			const imageRect = firstImage ? firstImage.getBoundingClientRect() : null;
			const firstRect = first ? first.getBoundingClientRect() : null;
			const docWidth = Math.max(
				document.documentElement.scrollWidth,
				document.body ? document.body.scrollWidth : 0,
			);
			return {
				photoPosition: photoStyle ? photoStyle.position : null,
				photoWidth: firstRect ? Math.round(firstRect.width) : 0,
				firstVisible: first ? first.classList.contains("is-visible") : false,
				firstTransition: photoStyle ? photoStyle.transitionProperty : "",
				secondVisible: second ? second.classList.contains("is-visible") : false,
				secondOpacity: secondStyle ? Number.parseFloat(secondStyle.opacity || "0") : 1,
				secondTransform: secondStyle ? secondStyle.transform : "",
				imageObjectFit: imageStyle ? imageStyle.objectFit : null,
				frameCount: document.querySelectorAll(".lt-frame").length,
				captionCount: document.querySelectorAll(".lt-cap, figcaption").length,
				imageFillsPhoto:
					firstRect && imageRect
						? Math.abs(firstRect.left - imageRect.left) <= 1 &&
							Math.abs(firstRect.top - imageRect.top) <= 1 &&
							Math.abs(firstRect.width - imageRect.width) <= 1 &&
							Math.abs(firstRect.height - imageRect.height) <= 1
						: false,
				docWidth,
				viewportWidth: document.documentElement.clientWidth,
			};
		});

		expect(facts.photoPosition).toBe("relative");
		expect(facts.photoWidth).toBeGreaterThanOrEqual(facts.viewportWidth - 1);
		expect(facts.photoWidth).toBeLessThanOrEqual(facts.viewportWidth + 1);
		expect(facts.firstVisible, "the first mobile portfolio photo should animate into visible state").toBe(true);
		expect(facts.firstTransition).toContain("transform");
		expect(facts.secondVisible, "later mobile portfolio photos should wait for scroll before becoming visible").toBe(false);
		expect(facts.secondOpacity).toBeLessThan(0.35);
		expect(facts.secondTransform).not.toBe("none");
		expect(facts.frameCount, "mobile portfolio photos should not render frame wrappers").toBe(0);
		expect(facts.captionCount, "mobile portfolio photos should not render captions").toBe(0);
		expect(facts.imageFillsPhoto, "mobile image rect should equal the photo rect").toBe(true);
		expect(facts.docWidth).toBeLessThanOrEqual(facts.viewportWidth + 2);

		await page.locator(".lt-photo").nth(1).scrollIntoViewIfNeeded();
		await page.waitForTimeout(650);
		const secondAfterScroll = await page.evaluate(() => {
			const second = document.querySelectorAll(".lt-photo")[1];
			const style = second ? window.getComputedStyle(second) : null;
			return {
				visible: second ? second.classList.contains("is-visible") : false,
				opacity: style ? Number.parseFloat(style.opacity || "0") : 0,
				transform: style ? style.transform : "",
			};
		});
		expect(secondAfterScroll.visible).toBe(true);
		expect(secondAfterScroll.opacity).toBeGreaterThan(0.8);

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

		await page.evaluate(() => window.scrollTo(0, 2200));
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
		expect(Math.max(...after.visible.map((photo) => photo.width))).toBeGreaterThan(800);
		expect(after.visible.some((photo) => photo.side === "center")).toBe(true);
		expect(after.visible.some((photo) => photo.side === "left")).toBe(true);
		expect(after.visible.some((photo) => photo.side === "right")).toBe(true);
		expect(new Set(after.visible.map((photo) => photo.top)).size).toBeGreaterThanOrEqual(2);
		expectNoLayoutFailures(expect, await auditPageLayout(page, {
			targetSelectors: [".lt-portfolio", ".lt-reel"],
		}), "portfolio staggered scroll state");
	});
});
