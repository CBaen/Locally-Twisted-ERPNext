const fs = require("node:fs");
const { defineConfig } = require("@playwright/test");

const WINDOWS_CHROME_PATHS = [
	"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
	"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
	"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
	"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
];

function findBrowserExecutable() {
	if (process.env.PLAYWRIGHT_CHROME_PATH) {
		return process.env.PLAYWRIGHT_CHROME_PATH;
	}

	return WINDOWS_CHROME_PATHS.find((candidate) => fs.existsSync(candidate));
}

const executablePath = findBrowserExecutable();
const workerCount = Number.parseInt(process.env.LT_PLAYWRIGHT_WORKERS || "4", 10) || 4;
const fullyParallel = process.env.LT_PLAYWRIGHT_FULLY_PARALLEL !== "0";

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
