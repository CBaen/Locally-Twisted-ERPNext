const { chromium } = require("@playwright/test");
const { BASE_URL, PUBLIC_ROUTES, gotoAndSettle } = require("./layout_helpers");

const VIEWPORTS = [
	{ name: "desktop", width: 1366, height: 900, tabLimit: 28 },
	{ name: "mobile", width: 390, height: 844, tabLimit: 28 },
	{ name: "zoom-pressure", width: 640, height: 900, tabLimit: 20 },
];

function status(response) {
	return response ? response.status() : 0;
}

async function focusedElementState(page) {
	return page.evaluate(() => {
		function proxyFor(element) {
			if (!element || !["INPUT", "SELECT", "TEXTAREA"].includes(element.tagName)) return null;
			const directLabel = element.closest("label");
			if (directLabel) return directLabel;
			if (!element.id) return null;
			return document.querySelector(`label[for="${CSS.escape(element.id)}"]`);
		}

		function box(element) {
			const rect = element.getBoundingClientRect();
			const style = window.getComputedStyle(element);
			return {
				rect,
				style,
				visible:
					style.display !== "none" &&
					style.visibility !== "hidden" &&
					Number(style.opacity) !== 0 &&
					rect.width > 0 &&
					rect.height > 0,
				inViewport:
					rect.bottom >= -2 &&
					rect.top <= window.innerHeight + 2 &&
					rect.right >= -2 &&
					rect.left <= window.innerWidth + 2,
				outlineWidth: Number.parseFloat(style.outlineWidth || "0"),
				boxShadow: style.boxShadow || "",
			};
		}

		const el = document.activeElement;
		if (!el || el === document.body) return { tag: "body" };

		const target = box(el);
		const proxy = proxyFor(el);
		const proxyBox = proxy ? box(proxy) : null;
		const usesVisibleProxy =
			proxyBox &&
			proxyBox.visible &&
			proxyBox.inViewport &&
			(proxyBox.outlineWidth >= 2 || (proxyBox.boxShadow && proxyBox.boxShadow !== "none"));

		return {
			tag: el.tagName,
			id: el.id || "",
			text: (el.innerText || el.getAttribute("aria-label") || el.getAttribute("title") || el.value || "")
				.trim()
				.slice(0, 80),
			visible: target.visible || Boolean(usesVisibleProxy),
			inViewport: target.inViewport || Boolean(usesVisibleProxy),
			outlineWidth: target.outlineWidth,
			boxShadow: target.boxShadow,
			proxyFocusVisible: Boolean(usesVisibleProxy),
		};
	});
}

async function layoutState(page) {
	return page.evaluate(() => ({
		scrollWidth: document.documentElement.scrollWidth,
		clientWidth: document.documentElement.clientWidth,
		mainCount: document.querySelectorAll("main").length,
		h1Count: document.querySelectorAll("h1").length,
		brokenImages: Array.from(document.images)
			.filter((img) => img.complete && img.naturalWidth === 0)
			.map((img) => img.currentSrc || img.src),
	}));
}

async function run() {
	const browser = await chromium.launch({ headless: true });
	const failures = [];

	for (const viewport of VIEWPORTS) {
		const page = await browser.newPage({
			viewport: { width: viewport.width, height: viewport.height },
		});

		for (const route of PUBLIC_ROUTES) {
			let response = null;
			try {
				response = await gotoAndSettle(page, route.path);
			} catch (error) {
				failures.push(`${viewport.name} ${route.path}: failed to load (${error.message})`);
				continue;
			}

			if (!response || status(response) >= 400) {
				failures.push(`${viewport.name} ${route.path}: HTTP ${status(response)}`);
				continue;
			}

			const layout = await layoutState(page);
			if (layout.scrollWidth > layout.clientWidth + 2) {
				failures.push(
					`${viewport.name} ${route.path}: horizontal overflow ${layout.scrollWidth}/${layout.clientWidth}`,
				);
			}
			if (layout.mainCount !== 1) {
				failures.push(`${viewport.name} ${route.path}: expected one page main landmark, found ${layout.mainCount}`);
			}
			if (layout.h1Count < 1) {
				failures.push(`${viewport.name} ${route.path}: missing h1`);
			}
			if (layout.brokenImages.length) {
				failures.push(`${viewport.name} ${route.path}: broken images ${layout.brokenImages.join(", ")}`);
			}

			for (let index = 0; index < viewport.tabLimit; index += 1) {
				await page.keyboard.press("Tab");
				const focus = await focusedElementState(page);
				if (focus.tag === "body") continue;

				if (!focus.visible) {
					failures.push(`${viewport.name} ${route.path}: hidden focused element ${JSON.stringify(focus)}`);
				}
				if (!focus.inViewport) {
					failures.push(`${viewport.name} ${route.path}: focused element outside viewport ${JSON.stringify(focus)}`);
				}

				const hasVisibleFocus =
					focus.proxyFocusVisible || focus.outlineWidth >= 2 || (focus.boxShadow && focus.boxShadow !== "none");
				if (!hasVisibleFocus) {
					failures.push(`${viewport.name} ${route.path}: weak focus indicator ${JSON.stringify(focus)}`);
				}
			}
		}

		await page.close();
	}

	await browser.close();

	if (failures.length) {
		console.error("Manual accessibility probe failures:");
		for (const failure of failures) console.error(` - ${failure}`);
		process.exit(1);
	}

	console.log("manual accessibility probe passed");
}

run().catch((error) => {
	console.error(error);
	process.exit(1);
});
