import { chromium } from 'playwright';
import fs from 'fs';
const [,, mode, a, b, fps = '30', outDir = 'frames'] = process.argv;
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on('console', m => console.log('console:', m.text()));
page.on('pageerror', e => console.log('pageerror:', e.message));
await page.goto('http://127.0.0.1:8099/index.html');
await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
await page.evaluate(() => document.fonts.ready);
fs.mkdirSync(outDir, { recursive: true });
const el = await page.$('#wrap');
if (mode === 'stills') {
  for (const t of a.split(',').map(Number)) {
    const t0 = Date.now();
    await page.evaluate(t => window.renderAt(t), t);
    await el.screenshot({ path: `${outDir}/still_${t}.png` });
    console.log('t', t, Date.now() - t0, 'ms');
  }
} else {
  const f = Number(fps), start = Number(a), end = Number(b);
  // warm the walk-distance accumulator from start
  for (let i = Math.round(start * f); i < Math.round(end * f); i++) {
    await page.evaluate(t => window.renderAt(t), i / f);
    await el.screenshot({ path: `${outDir}/f_${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 });
    if (i % 150 === 0) console.log('frame', i);
  }
}
await browser.close();
