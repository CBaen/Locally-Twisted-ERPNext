/**
 * render.spec.js
 * Playwright spec to screenshot all 32 contestant pages at mobile (390px) and desktop (1440px).
 * Outputs 64 PNGs to screenshots/contestant-N/{page}-{viewport}.png
 */
const { test } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

const CONTESTANTS = [1, 2, 3, 4, 5, 6, 7, 8];
const PAGES = ['civic-community', 'corporate-events', 'private-celebrations', 'schools-campuses'];
const VIEWPORTS = [
  { name: 'mobile', width: 390, height: 844 },
  { name: 'desktop', width: 1440, height: 900 },
];

const GALLERY_DIR = __dirname;
const SCREENSHOTS_DIR = path.join(GALLERY_DIR, 'screenshots');
const PREVIEW_DIR = path.join(GALLERY_DIR, 'preview');

for (const c of CONTESTANTS) {
  const ssDir = path.join(SCREENSHOTS_DIR, `contestant-${c}`);
  if (!fs.existsSync(ssDir)) fs.mkdirSync(ssDir, { recursive: true });
}

for (const c of CONTESTANTS) {
  for (const page of PAGES) {
    for (const vp of VIEWPORTS) {
      test(`C${c} / ${page} / ${vp.name}`, async ({ browser }) => {
        const context = await browser.newContext({
          viewport: { width: vp.width, height: vp.height },
        });
        const browserPage = await context.newPage();

        const filePath = path.join(PREVIEW_DIR, `contestant-${c}`, `${page}.html`);
        const fileUrl = `file:///${filePath.replace(/\\/g, '/')}`;

        await browserPage.goto(fileUrl, { waitUntil: 'networkidle', timeout: 15000 });

        // Wait for fonts (Google Fonts CDN)
        await browserPage.waitForTimeout(1200);

        const ssPath = path.join(
          SCREENSHOTS_DIR,
          `contestant-${c}`,
          `${page}-${vp.name}.png`
        );

        await browserPage.screenshot({
          path: ssPath,
          fullPage: true,
        });

        await context.close();
      });
    }
  }
}
