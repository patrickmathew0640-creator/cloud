// Frame-accurate screen captures of threeui.com for the B-roll cards.
// The page clock (performance.now / Date.now / requestAnimationFrame) is virtualised and stepped one
// frame at a time, so Three.js scenes and scrolling come out smooth even under software WebGL.
// Usage: node capture.mjs <shot> <outdir>   (frames are written as PNGs, then encoded with ffmpeg)
import { chromium } from "/opt/node-tools/node_modules/playwright/index.mjs";
import fs from "node:fs";

const FPS = 30, W = 1280, H = 720, DPR = 1.5;
const [shot, outDir] = process.argv.slice(2);

const CLOCK = `(() => {
  let t = 0, id = 0; const cbs = new Map(); const d0 = Date.now(); const realNow = performance.now.bind(performance);
  performance.now = () => t; Date.now = () => d0 + t;
  window.requestAnimationFrame = cb => { cbs.set(++id, cb); return id; };
  window.cancelAnimationFrame = i => cbs.delete(i);
  window.__step = ms => { t += ms; const c = [...cbs.values()]; cbs.clear(); for (const f of c) { try { f(t); } catch (e) {} } };
})();`;

const CURSOR = `(() => {
  const c = document.createElement('div'); c.id = '__cur';
  c.innerHTML = '<svg viewBox="0 0 24 24" width="30" height="30"><path d="M4 2l16 10-7 1.6L9.6 21z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  Object.assign(c.style, { position: 'fixed', left: '0', top: '0', zIndex: 2147483647, pointerEvents: 'none', transformOrigin: '4px 2px', filter: 'drop-shadow(0 3px 6px rgba(0,0,0,.5))', display: 'none' });
  document.documentElement.appendChild(c);
  window.__cursor = (x, y, s = 1) => { c.style.display = 'block'; c.style.transform = 'translate(' + x + 'px,' + y + 'px) scale(' + s + ')'; };
})();`;

const ease = x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const lerp = (a, b, k) => a + (b - a) * k;

const SHOTS = {
  // three landing-page heroes, ~1.15s each, for the hook card
  hook: [
    { url: "https://threeui.com/landing-pages/oblo.html", secs: 1.2 },
    { url: "https://threeui.com/landing-pages/dayward.html", secs: 1.2 },
    { url: "https://threeui.com/landing-pages/drift.html", secs: 1.2 },
  ],
  // browse gallery, smooth scroll down the main pane
  browse: [{ url: "https://threeui.com/browse?sort=recent", secs: 4.6, scroll: [".pane-scroll", 0, 1150] }],
  // cursor glides onto the Kage card in the gallery
  pick: [{ url: "https://threeui.com/browse?sort=recent", secs: 2.2, cursor: [[620, 560], [650, 330]], hover: true }],
  // Kage page: cursor to "Copy Prompt" and click
  copy: [{ url: "https://threeui.com/landing-pages/kage-landing-page", secs: 2.4, cursor: [[900, 420], [1140, 48]], click: 1.45 }],
  // the finished 3D site, scrolled through its scenes
  result: [{ url: "https://threeui.com/landing-pages/kage.html", secs: 4.8, wheel: 1900 }],
};

const browser = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
fs.mkdirSync(outDir, { recursive: true });
let n = 0;
for (const s of SHOTS[shot]) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DPR, colorScheme: "dark", permissions: ["clipboard-read", "clipboard-write"] });
  await ctx.addInitScript(CLOCK);
  const p = await ctx.newPage();
  const cdp = await ctx.newCDPSession(p);
  await p.goto(s.url, { waitUntil: "networkidle", timeout: 90000 }).catch(e => console.log("goto:", e.message));
  await p.evaluate(CURSOR);
  for (let i = 0; i < 90; i++) { await p.evaluate(() => window.__step(1000 / 30)); }  // warm up 3s of scene time
  await p.waitForTimeout(1500);
  const frames = Math.round(s.secs * FPS);
  let clicked = false;
  for (let f = 0; f < frames; f++) {
    const k = f / (frames - 1);
    if (s.scroll) {
      const [sel, a, b] = s.scroll;
      await p.evaluate(([sel, y]) => { const e = document.querySelector(sel); if (e) e.scrollTop = y; }, [sel, lerp(a, b, ease(k))]);
    }
    if (s.wheel) await p.evaluate(y => window.scrollTo(0, y), s.wheel * ease(k));
    if (s.cursor) {
      const mk = s.click ? Math.min(1, (f / FPS) / (s.click - 0.15)) : Math.min(1, k * 1.3);
      const x = lerp(s.cursor[0][0], s.cursor[1][0], ease(mk)), y = lerp(s.cursor[0][1], s.cursor[1][1], ease(mk));
      const pressed = s.click && Math.abs(f / FPS - s.click) < 0.08;
      await p.evaluate(([x, y, sc]) => window.__cursor(x, y, sc), [x, y, pressed ? 0.82 : 1]);
      if (s.hover) await p.mouse.move(x, y);
      if (s.click && !clicked && f / FPS >= s.click) { clicked = true; await p.mouse.click(x, y); }
    }
    await p.evaluate(() => window.__step(1000 / 30));
    const { data } = await cdp.send("Page.captureScreenshot", { format: "png" });  // CDP: no rAF wait
    fs.writeFileSync(`${outDir}/f${String(n++).padStart(4, "0")}.png`, Buffer.from(data, "base64"));
  }
  if (s.click) console.log("clipboard:", (await p.evaluate(() => navigator.clipboard.readText()).catch(() => "")).slice(0, 80));
  await ctx.close();
}
await browser.close();
console.log(shot, n, "frames");
