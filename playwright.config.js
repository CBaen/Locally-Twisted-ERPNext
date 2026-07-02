const fs = require("node:fs");
const { defineConfig } = require("@playwright/test");

const LINUX_CHROME_PATHS = [
	"/usr/bin/brave-browser",
	"/usr/bin/chromium",
	"/usr/bin/chromium-browser",
	"/usr/bin/google-chrome",
];
const BROWSER_PATHS = [...LINUX_CHROME_PATHS];

function findBrowserExecutable() {
	if (process.env.PLAYWRIGHT_CHROME_PATH) {
		return process.env.PLAYWRIGHT_CHROME_PATH;
	}

	return BROWSER_PATHS.find((candidate) => fs.existsSync(candidate));
}

const executablePath = findBrowserExecutable();
const workerCount = Number.parseInt(process.env.LT_PLAYWRIGHT_WORKERS || "1", 10) || 1;
const fullyParallel = process.env.LT_PLAYWRIGHT_FULLY_PARALLEL === "1";

module.exports = defineConfig({
	timeout: 45_000,
	fullyParallel,
	workers: workerCount,
	expect: {
		timeout: 10_000,
	},
	reporter: "line",
	use: {
		browserName: "chromium",
		headless: true,
		launchOptions: executablePath ? { executablePath } : {},
	},
});
