// Render the explainer's three SVG diagrams (with their boxes) to PNG, light theme, 2x.
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const body = fs.readFileSync(process.argv[2], 'utf8');
  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${body}</body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2, colorScheme: 'light' });
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const names = ['data_flow', 'pipeline', 'check'];
  const svgs = await page.$$('svg');
  for (let i = 0; i < names.length; i++) {
    const box = await svgs[i].evaluateHandle(e => e.closest('.box'));
    await box.asElement().screenshot({ path: `${process.argv[3]}/${names[i]}.png` });
  }
  await browser.close();
})();
