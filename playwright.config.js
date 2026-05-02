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

module.exports = defineConfig({
	timeout: 45_000,
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
