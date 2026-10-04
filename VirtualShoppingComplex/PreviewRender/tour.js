import * as THREE from 'three';
import { buildMall, SHOPS, products, formatPrice, HalfWidth, Length, LobbyEnd, ShopsEnd, ShopWidth, ShopDepth } from './mall.js';

const W = 1280, Hh = 720;
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, Hh);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.getElementById('wrap').prepend(renderer.domElement);

const scene = new THREE.Scene();
{ // sky gradient like Unity's default procedural skybox
  const c = document.createElement('canvas'); c.width = 4; c.height = 256;
  const g = c.getContext('2d'); const gr = g.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, '#5a8fd0'); gr.addColorStop(0.55, '#a9c8ea'); gr.addColorStop(0.62, '#d9dde0'); gr.addColorStop(1, '#6d6a66');
  g.fillStyle = gr; g.fillRect(0, 0, 4, 256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; scene.background = t;
}
const hemi = new THREE.HemisphereLight(0xffffff, 0xffffff, 1.0);
hemi.color.setRGB(0.80, 0.82, 0.86, THREE.SRGBColorSpace);
hemi.groundColor.setRGB(0.40, 0.38, 0.36, THREE.SRGBColorSpace);
scene.add(hemi);
buildMall(scene);

const camera = new THREE.PerspectiveCamera(70, W / Hh, 0.05, 400);

// --------------------------------------------------------------- tour keyframes (Unity coords)
// [time, x, z, yaw, pitch, stop]   yaw 0 = +Z (into mall), 90 = +X ; pitch + = look down
const K = [
  [0, 0, -7, 0, -9, 1], [4.6, 0, -7, 0, -9, 1],
  [6.5, 0, -4.5, 0, -4, 0], [9, 0, 1.5, -5, 0, 0], [10.5, -2.8, 5, -15, 0, 0], [12, -2.7, 9, 0, 0, 0], [13.5, -2.5, 13.5, -10, 0, 0],
  [15, -2.6, 16, -55, 3, 0], [16.5, -4.2, 19, -90, 3, 0], [18, -7, 19, -90, 3, 1],
  [19.5, -7, 19, -55, 3, 1], [21, -7, 19, -125, 3, 1],
  [23, -11.2, 20.7, -90, 9, 1], [28.8, -11.2, 20.7, -90, 9, 1],
  [30, -8.5, 17.5, -110, 12, 0], [31.5, -5.3, 15.0, -90, 21, 1], [37.3, -5.3, 15.0, -90, 21, 1],
  [38.5, -5.6, 19, 30, 3, 0], [40, -2.5, 23.4, 75, 0, 0], [41.5, 2.5, 23.4, 115, 2, 0], [43, 5, 19.3, 95, 3, 0], [44.3, 8, 17, 120, 5, 0],
  [45.6, 11.2, 13.9, 90, 15, 1], [52.2, 11.2, 13.9, 90, 15, 1], [53.8, 11.2, 13.9, 35, 6, 1],
  [55.3, 7.5, 18.5, -40, 2, 0], [56.8, 2.6, 24.5, 0, 0, 0], [58.8, 2.6, 30, 0, 0, 0], [60.3, 2.6, 33, -70, 2, 1],
  [61.8, 2.6, 33, 70, 2, 1], [63.5, 2.6, 38.5, 10, 0, 0], [64.6, 2.4, 43.3, -45, 2, 0], [66, -2.6, 43.3, -75, 2, 0],
  [67.4, -5.5, 46.5, -90, 3, 0], [68.6, -9, 46.8, -90, 5, 0], [70.2, -11.6, 45.3, -90, 20, 1], [76, -11.6, 45.3, -90, 20, 1],
  [77.8, -14.8, 46.6, -90, 8, 1], [79.2, -14.8, 46.6, -110, 8, 1],
  [80.8, -6, 47, 90, 2, 0], [82.2, -2.6, 43.3, 100, 2, 0], [83.6, 2.6, 43.3, 75, 2, 0], [85, 5.5, 46.5, 90, 3, 0],
  [86.4, 11.3, 45.3, 90, 15, 1], [92, 11.3, 45.3, 90, 15, 1],
  [93.6, 6, 48.5, -10, 2, 0], [95, 2.6, 51.5, 0, 0, 0], [97, 0.6, 56, 0, -6, 0], [99.2, 0, 60.5, 0, -4, 0], [100.8, 0, 63.3, 0, 0, 1],
  [106.5, 0, 63.3, 0, 0, 1],
];
export const DURATION = 106.5;

// precompute legs (stop -> stop) as Catmull-Rom curves
const legs = [];
{
  let start = 0;
  for (let i = 1; i < K.length; i++) {
    if (!K[i][5]) continue;
    const pts = K.slice(start, i + 1);
    const vecs = pts.map(k => new THREE.Vector3(k[1], 0, k[2]));
    const len = vecs.reduce((s, v, j) => s + (j ? v.distanceTo(vecs[j - 1]) : 0), 0);
    const curve = len > 1e-3 ? new THREE.CatmullRomCurve3(vecs, false, 'centripetal') : null;
    // fraction of each keyframe along the leg (by time)
    const t0 = pts[0][0], t1 = pts.at(-1)[0];
    legs.push({ t0, t1, pts, curve, len, fr: pts.map(k => (k[0] - t0) / (t1 - t0)) });
    start = i;
  }
}
const ease = x => x * x * (3 - 2 * x);
const easeLeg = (x, len, dur) => {
  if (len < 1e-3) return ease(x);
  // accelerate / decelerate over ~0.5 s, constant speed in between
  const a = Math.min(0.5 / dur, 0.3);
  const v = 1 / (1 - a);
  if (x < a) return v * x * x / (2 * a);
  if (x > 1 - a) return 1 - v * (1 - x) * (1 - x) / (2 * a);
  return v * (x - a / 2);
};
function poseAt(t) {
  const leg = legs.find(l => t >= l.t0 && t <= l.t1) || legs.at(-1);
  const x = Math.min(1, Math.max(0, (t - leg.t0) / (leg.t1 - leg.t0)));
  const s = easeLeg(x, leg.len, leg.t1 - leg.t0);
  const p = leg.curve ? leg.curve.getPointAt(s) : new THREE.Vector3(leg.pts[0][1], 0, leg.pts[0][2]);
  // yaw/pitch: interpolate between keyframes using the eased fraction
  let i = 0; while (i < leg.fr.length - 2 && s > leg.fr[i + 1]) i++;
  const a = leg.pts[i], b = leg.pts[i + 1];
  const f = ease(Math.min(1, Math.max(0, (s - leg.fr[i]) / Math.max(1e-6, leg.fr[i + 1] - leg.fr[i]))));
  return { x: p.x, z: p.z, yaw: a[3] + (b[3] - a[3]) * f, pitch: a[4] + (b[4] - a[4]) * f, moving: leg.len > 1e-3 && x > 0 && x < 1 };
}

// --------------------------------------------------------------- UI timeline (mirrors UIManager behaviour)
const shopByName = n => SHOPS.find(s => s.name === n);
const prodInfo = (shop, name) => {
  const s = shopByName(shop), p = s.products.find(q => q.name === name);
  const title = shop.toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
  return { header: 'PRODUCT INFORMATION', title: p.name.toUpperCase(), sub: 'Price: ' + formatPrice(p.price),
    body: p.desc + '\n\nAvailable at: ' + title, accent: s.accent };
};
const shopInfo = shop => {
  const s = shopByName(shop);
  return { header: 'SHOP INFORMATION', title: s.name, sub: 'Number of Products: 4   (22 items on display)', body: s.desc, accent: s.accent };
};
const EV = {
  start: [0, 4.6],
  welcome: [4.6, 8.6],
  prompts: [
    [23.2, 24.6, 'Press E to Interact', 'Jacket', ['FASHION STORE', 'Jacket']],
    [31.6, 32.8, 'Press E to Explore Shop', 'FASHION STORE', null],
    [45.7, 47.0, 'Press E to Interact', 'Smartphone', ['ELECTRONICS STORE', 'Smartphone']],
    [70.3, 71.6, 'Press E to Interact', 'Milk Bottle', ['GROCERY STORE', 'Milk Bottle']],
    [86.5, 87.8, 'Press E to Interact', 'Sunglasses', ['ACCESSORIES STORE', 'Sunglasses']],
  ],
  panels: [
    [24.6, 28.6, prodInfo('FASHION STORE', 'Jacket'), 'click'],
    [32.8, 37.1, shopInfo('FASHION STORE'), 'key'],
    [47.0, 52.0, prodInfo('ELECTRONICS STORE', 'Smartphone'), 'click'],
    [71.6, 75.8, prodInfo('GROCERY STORE', 'Milk Bottle'), 'key'],
    [87.8, 91.8, prodInfo('ACCESSORIES STORE', 'Sunglasses'), 'click'],
  ],
  exit: [100.9, 106.5],
};
const $ = id => document.getElementById(id);
const show = (id, on) => $(id).classList.toggle('hidden', !on);
const hex = c => '#' + c.map(v => Math.round(Math.min(1, v) * 255).toString(16).padStart(2, '0')).join('');
const inR = (t, r) => t >= r[0] && t < r[1];

function describeLocation(x, z) {
  for (let i = 0; i < SHOPS.length; i++) {
    const left = i % 2 === 0, row = Math.floor(i / 2);
    const cz = LobbyEnd + ShopWidth * (row + 0.5), cx = (4 + ShopDepth / 2) * (left ? -1 : 1);
    if (Math.abs(x - cx) < ShopDepth / 2 && Math.abs(z - cz) < ShopWidth / 2)
      return SHOPS[i].name.toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
  }
  if (Math.abs(x) >= HalfWidth) return 'Outside the Shopping Complex';
  if (z < 0) return 'Main Entrance (Outside)';
  if (z > Length) return 'Outside - Exit';
  if (z < LobbyEnd) return 'Main Lobby';
  if (z < ShopsEnd) return 'Central Corridor';
  return 'Exit Hall';
}

function moveMouse(t, r, from, to) { // animate cursor (UI px)
  const k = ease(Math.min(1, Math.max(0, (t - r[0]) / Math.max(0.01, r[1] - r[0]))));
  const m = $('mouse'); m.style.left = (from[0] + (to[0] - from[0]) * k) + 'px'; m.style.top = (from[1] + (to[1] - from[1]) * k) + 'px';
}

function updateUI(t, pose) {
  const playing = !inR(t, EV.start) && !EV.panels.some(p => inR(t, p)) && !inR(t, EV.exit);
  show('start', inR(t, EV.start));
  show('crosshair', playing); show('hint', playing); show('loc', !inR(t, EV.start));
  $('loc').textContent = 'Location:  ' + describeLocation(pose.x, pose.z);

  // welcome fade (last 0.8 s)
  const w = inR(t, EV.welcome);
  show('welcome', w);
  if (w) $('welcome').style.opacity = Math.min(1, (EV.welcome[1] - t) / 0.8);

  const pr = EV.prompts.find(p => t >= p[0] && t < p[1]);
  show('prompt', !!pr && playing);
  if (pr) { $('prompt').querySelector('.p').textContent = pr[2]; $('prompt').querySelector('.t').textContent = pr[3]; }

  const pn = EV.panels.find(p => inR(t, p));
  show('info', !!pn);
  let mouse = false;
  if (pn) {
    const d = pn[2], info = $('info');
    info.querySelector('.bar').style.background = hex(d.accent);
    info.querySelector('.h').style.color = hex(d.accent.map(v => v + (1 - v) * 0.35));
    info.querySelector('.h').textContent = d.header; info.querySelector('.ti').textContent = d.title;
    info.querySelector('.su').textContent = d.sub; info.querySelector('.de').textContent = d.body;
    const cb = info.querySelector('.cb');
    if (pn[3] === 'click') {
      mouse = true;
      moveMouse(t, [pn[1] - 1.3, pn[1] - 0.35], [960, 560], [1215, 715]);
      cb.style.filter = t > pn[1] - 0.3 ? 'brightness(0.78)' : t > pn[1] - 0.9 ? 'brightness(0.96)' : 'none';
    } else {
      mouse = true; moveMouse(t, [0, 1], [960, 560], [960, 560]);
      cb.style.filter = 'none';
    }
  }
  if (inR(t, EV.start)) {
    mouse = true; moveMouse(t, [1.4, 3.6], [1100, 300], [860, 790]);
    $('start').querySelector('.sb').style.filter = t > 4.1 ? 'brightness(0.78)' : t > 3.6 ? 'brightness(0.96)' : 'none';
  }
  show('exit', inR(t, EV.exit));
  if (inR(t, EV.exit)) { mouse = true; moveMouse(t, [101.5, 103.5], [960, 560], [1000, 650]); }
  show('mouse', mouse);

  // focused product grows 1.08x (InteractableProduct.SetFocused)
  for (const p of products) if (p.featured) p.group.scale.setScalar(1);
  if (pr && pr[4] && playing) {
    const p = products.find(q => q.featured && q.shop === pr[4][0] && q.name === pr[4][1]);
    if (p) p.group.scale.setScalar(1.08);
  }
}

// --------------------------------------------------------------- render one frame
const D2R = Math.PI / 180;
const INTRO = 4.5;
window.renderAt = (T) => {
  document.getElementById('intro').classList.toggle('hidden', T >= INTRO);
  if (T < INTRO) { // establishing shot of the building (not part of the Unity game flow)
    for (const id of ['start', 'loc', 'hint', 'crosshair', 'prompt', 'welcome', 'info', 'exit', 'mouse']) show(id, false);
    const k = ease(T / INTRO);
    camera.position.set(-16 + 10 * k, 7 - 2.5 * k, 27 - 6 * k);
    camera.lookAt(0, 2.8, 0);
    renderer.render(scene, camera);
    return true;
  }
  const t = T - INTRO;
  const pose = poseAt(t);
  const bob = pose.moving ? Math.sin(t * Math.PI * 2 * 1.7) * 0.022 : 0;
  const eye = 0.05 + 1.62 + bob;
  const yaw = pose.yaw * D2R, pitch = pose.pitch * D2R;
  const fwd = [Math.sin(yaw) * Math.cos(pitch), -Math.sin(pitch), Math.cos(yaw) * Math.cos(pitch)];
  // Unity -> three: negate Z
  camera.position.set(pose.x, eye, -pose.z);
  camera.lookAt(pose.x + fwd[0], eye + fwd[1], -(pose.z + fwd[2]));
  updateUI(t, pose);
  renderer.render(scene, camera);
  return true;
};
window.DURATION = DURATION + INTRO;
window.ready = true;
