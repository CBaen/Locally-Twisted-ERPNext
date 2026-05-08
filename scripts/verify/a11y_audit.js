const fs = require("fs");
const path = require("path");
const { chromium } = require("@playwright/test");
const { BASE_URL, PUBLIC_ROUTES, gotoAndSettle } = require("./layout_helpers");

const OUTPUT_DIR = path.join(process.cwd(), "output", "a11y");
const AXE_SOURCE = fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");

const VIEWPORTS = [
	{ name: "desktop", width: 1366, height: 900, file: "a11y-desktop.json" },
	{ name: "mobile", width: 390, height: 900, file: "a11y-mobile.json" },
];

function trimResults(result) {
	return {
		testEngine: result.testEngine,
		testRunner: result.testRunner,
		testEnvironment: result.testEnvironment,
		timestamp: result.timestamp,
		url: result.url,
		toolOptions: result.toolOptions,
		violations: result.violations,
	};
}

function summarize(resultSets) {
	const summary = {
		scannedResults: 0,
		routeViewportFailures: 0,
		totalViolations: 0,
		totalNodes: 0,
		byRule: {},
		byRoute: {},
	};
	const findings = [];

	for (const { viewport, results } of resultSets) {
		for (const result of results) {
			summary.scannedResults += 1;
			const violations = result.violations || [];
			if (!violations.length) continue;

			const routePath = new URL(result.url).pathname;
			const key = `${viewport} ${routePath}`;
			summary.routeViewportFailures += 1;
			summary.byRoute[key] = [];

			const compactViolations = violations.map((violation) => {
				const nodeCount = violation.nodes.length;
				summary.totalViolations += 1;
				summary.totalNodes += nodeCount;
				summary.byRule[violation.id] = (summary.byRule[violation.id] || 0) + nodeCount;
				summary.byRoute[key].push(`${violation.id}:${nodeCount}`);
				return {
					id: violation.id,
					impact: violation.impact,
					help: violation.help,
					helpUrl: violation.helpUrl,
					nodes: violation.nodes.map((node) => ({
						target: node.target,
						html: node.html,
						failureSummary: node.failureSummary,
					})),
				};
			});

			findings.push({ viewport, url: result.url, violations: compactViolations });
		}
	}

	return { summary, findings };
}

async function runViewport(browser, viewport) {
	const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height } });
	const page = await context.newPage();
	const results = [];
	try {
		for (const route of PUBLIC_ROUTES) {
			await gotoAndSettle(page, route.path);
			await page.addScriptTag({ content: AXE_SOURCE });
			const result = await page.evaluate(async () => {
				return await window.axe.run(document, {
					reporter: "v1",
				});
			});
			results.push(trimResults(result));
		}
	} finally {
		await context.close();
	}
	return results;
}

async function main() {
	fs.mkdirSync(OUTPUT_DIR, { recursive: true });
	const browser = await chromium.launch();
	const resultSets = [];
	try {
		for (const viewport of VIEWPORTS) {
			const results = await runViewport(browser, viewport);
			resultSets.push({ viewport: viewport.name, results });
			fs.writeFileSync(path.join(OUTPUT_DIR, viewport.file), JSON.stringify(results, null, 2));
		}
	} finally {
		await browser.close();
	}

	const summary = summarize(resultSets);
	fs.writeFileSync(path.join(OUTPUT_DIR, "a11y-summary.json"), JSON.stringify(summary, null, 2));

	if (summary.summary.totalViolations > 0) {
		console.error(
			`axe found ${summary.summary.totalViolations} violation type(s) across ${summary.summary.routeViewportFailures} route/viewport result(s); see output/a11y/a11y-summary.json`,
		);
		process.exit(1);
	}

	console.log(`axe passed: ${summary.summary.scannedResults} route/viewport results, 0 violations`);
}

main().catch((error) => {
	console.error(error);
	process.exit(1);
});
