// three.js port of VirtualMall MallBuilder / ProductFactory / MallCatalog (same coordinates, Unity space).
// Everything is built in Unity coordinates under root group U, which is mirrored on Z at the end
// so the rendered image matches Unity's left-handed view.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const D2R = Math.PI / 180;
export const U = new THREE.Group();

// ------------------------------------------------------------ geometry / materials
const GEO = {
  cube: new THREE.BoxGeometry(1, 1, 1),
  sphere: new THREE.SphereGeometry(0.5, 24, 16),
  cylinder: new THREE.CylinderGeometry(0.5, 0.5, 2, 28),
  capsule: new THREE.CapsuleGeometry(0.5, 1, 8, 16),
};
const matCache = new Map();
function clamp01(v) { return Math.min(1, Math.max(0, v)); }

let floorCanvas = null;
function floorTex(tiling) {
  if (!floorCanvas) {
    const size = 128;
    floorCanvas = document.createElement('canvas');
    floorCanvas.width = floorCanvas.height = size;
    const ctx = floorCanvas.getContext('2d');
    const img = ctx.createImageData(size, size);
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      const grout = x < 2 || y < 2;
      const n = (Math.sin(x * 0.21) * Math.cos(y * 0.17) * 0.5 + 0.5) * 0.06;
      const v = grout ? 0.62 : 0.93 - n;
      const i = (y * size + x) * 4;
      img.data[i] = img.data[i + 1] = v * 255; img.data[i + 2] = v * 0.98 * 255; img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
  }
  const t = new THREE.CanvasTexture(floorCanvas);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(tiling[0], tiling[1]);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}

export function M(c, smooth = 0.15, tiling = null) {
  const key = c.map(v => clamp01(v).toFixed(3)).join(',') + '|' + smooth + '|' + (tiling ? tiling.join('x') : '');
  if (matCache.has(key)) return matCache.get(key);
  const m = new THREE.MeshStandardMaterial({ roughness: 1 - smooth * 0.85, metalness: 0 });
  m.color.setRGB(clamp01(c[0]), clamp01(c[1]), clamp01(c[2]), THREE.SRGBColorSpace);
  if (tiling) m.map = floorTex(tiling);
  matCache.set(key, m);
  return m;
}
const mul = (c, k) => [c[0] * k, c[1] * k, c[2] * k];
const lerpC = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];

function setRot(o, e) { o.rotation.set(e[0] * D2R, e[1] * D2R, e[2] * D2R, 'YXZ'); }
export function grp(name, parent, pos = [0, 0, 0], euler = [0, 0, 0]) {
  const g = new THREE.Group(); g.name = name;
  g.position.set(...pos); setRot(g, euler);
  parent.add(g); g.updateMatrixWorld(true);
  return g;
}
function part(name, type, parent, pos, scale, mat, euler = [0, 0, 0], cast = true) {
  const m = new THREE.Mesh(GEO[type], mat); m.name = name;
  m.position.set(...pos); m.scale.set(...scale); setRot(m, euler);
  m.castShadow = cast; m.receiveShadow = true; m.userData.static = true;
  parent.add(m); m.updateMatrixWorld(true);
  return m;
}
const block = (name, parent, c, s, mat, collider = true, cast = true) => part(name, 'cube', parent, c, s, mat, [0, 0, 0], cast);
const tp = (o, p) => o.localToWorld(new THREE.Vector3(...p));
const td = (o, d) => new THREE.Vector3(...d).transformDirection(o.matrixWorld);

// ------------------------------------------------------------ labels (Unity world-space Canvas + Text)
function hexColor(c) { return '#' + c.slice(0, 3).map(v => Math.round(clamp01(v) * 255).toString(16).padStart(2, '0')).join(''); }
function rgba(c) { return `rgba(${Math.round(clamp01(c[0]) * 255)},${Math.round(clamp01(c[1]) * 255)},${Math.round(clamp01(c[2]) * 255)},${c[3] ?? 1})`; }

function parseRich(text, baseColor, baseBold, baseSize) {
  // returns lines: [[{t,bold,color,size}]]
  const lines = [[]];
  const stack = { bold: [baseBold], color: [baseColor], size: [baseSize] };
  const re = /<(\/?)(b|color|size)(=([^>]+))?>/g;
  let last = 0, m;
  const push = (s) => {
    const parts = s.split('\n');
    parts.forEach((p, i) => {
      if (i > 0) lines.push([]);
      if (p) lines[lines.length - 1].push({ t: p, bold: stack.bold.at(-1), color: stack.color.at(-1), size: stack.size.at(-1) });
    });
  };
  while ((m = re.exec(text))) {
    push(text.slice(last, m.index)); last = re.lastIndex;
    const [, close, tag, , val] = m;
    const key = tag === 'b' ? 'bold' : tag;
    if (close) { if (stack[key].length > 1) stack[key].pop(); }
    else stack[key].push(tag === 'b' ? true : tag === 'size' ? parseFloat(val) : val);
  }
  push(text.slice(last));
  return lines;
}

const FONT = '"Liberation Sans", Arial, "DejaVu Sans", sans-serif';
function wrapLines(ctx, lines, maxW, k) {
  // simple word wrap of runs
  const out = [];
  for (const line of lines) {
    let cur = [], w = 0;
    for (const run of line) {
      const words = run.t.split(/(\s+)/);
      for (const word of words) {
        if (!word) continue;
        ctx.font = `${run.bold ? 'bold ' : ''}${run.size * k}px ${FONT}`;
        const ww = ctx.measureText(word).width;
        if (w + ww > maxW && cur.length && word.trim()) { out.push(cur); cur = []; w = 0; }
        if (!cur.length && !word.trim()) continue;
        cur.push({ ...run, t: word }); w += ww;
      }
    }
    out.push(cur);
  }
  return out;
}

export function label(name, text, wpos, face, size, fontSize, color, bg = null, bold = true) {
  const PPM = 200, RES = 2;
  const pw = size[0] * PPM, ph = size[1] * PPM;
  const canvas = document.createElement('canvas');
  canvas.width = Math.min(2048, Math.ceil(pw * RES)); canvas.height = Math.min(1024, Math.ceil(ph * RES));
  const sx = canvas.width / pw, sy = canvas.height / ph;
  const ctx = canvas.getContext('2d');
  ctx.scale(sx, sy);
  if (bg) { ctx.fillStyle = rgba(bg); ctx.fillRect(0, 0, pw, ph); }
  const padX = 6, padY = 4, aw = pw - padX * 2, ah = ph - padY * 2;
  const lines0 = parseRich(text, hexColor(color), bold, fontSize);
  // best fit (Unity resizeTextForBestFit)
  let k = 1, lines;
  for (let iter = 0; iter < 60; iter++) {
    lines = wrapLines(ctx, lines0, aw, k);
    const h = lines.reduce((s, l) => s + Math.max(...(l.length ? l.map(r => r.size) : [fontSize])) * k * 1.15, 0);
    let maxW = 0;
    for (const l of lines) { let w = 0; for (const r of l) { ctx.font = `${r.bold ? 'bold ' : ''}${r.size * k}px ${FONT}`; w += ctx.measureText(r.t).width; } maxW = Math.max(maxW, w); }
    if (h <= ah && maxW <= aw + 0.5) break;
    k *= 0.94;
  }
  const lineH = lines.map(l => Math.max(...(l.length ? l.map(r => r.size) : [fontSize])) * k * 1.15);
  const total = lineH.reduce((a, b) => a + b, 0);
  let y = padY + (ah - total) / 2;
  ctx.textBaseline = 'middle';
  lines.forEach((l, i) => {
    let w = 0; for (const r of l) { ctx.font = `${r.bold ? 'bold ' : ''}${r.size * k}px ${FONT}`; w += ctx.measureText(r.t).width; }
    let x = padX + (aw - w) / 2;
    for (const r of l) {
      ctx.font = `${r.bold ? 'bold ' : ''}${r.size * k}px ${FONT}`;
      ctx.fillStyle = r.color; ctx.fillText(r.t, x, y + lineH[i] / 2);
      x += ctx.measureText(r.t).width;
    }
    y += lineH[i];
  });
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, side: THREE.DoubleSide, toneMapped: false, depthWrite: false });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat);
  mesh.name = name;
  const f = new THREE.Vector3(...(Array.isArray(face) ? face : [face.x, face.y, face.z])).normalize().negate();
  const up = new THREE.Vector3(0, 1, 0);
  const right = new THREE.Vector3().crossVectors(up, f).normalize();
  const n = new THREE.Vector3().crossVectors(right, up);
  const p = Array.isArray(wpos) ? new THREE.Vector3(...wpos) : wpos;
  mesh.matrixAutoUpdate = false;
  mesh.matrix.makeBasis(right.multiplyScalar(size[0]), up.multiplyScalar(size[1]), n).setPosition(p);
  mesh.renderOrder = 1;
  U.add(mesh);
  return mesh;
}

// ------------------------------------------------------------ catalog
const C = (r, g, b) => [r, g, b];
export const SHOPS = [
  ['FASHION STORE', 'Explore shirts, jackets, jeans and t-shirts for every season.', C(0.82, 0.22, 0.50), C(0.96, 0.90, 0.93), C(0.72, 0.62, 0.66), [
    ['Shirt', 1299, 'Shirt', C(0.30, 0.55, 0.85), 'Slim-fit cotton formal shirt, perfect for office wear and special occasions.'],
    ['Jacket', 3499, 'Jacket', C(0.25, 0.28, 0.32), 'Water-resistant casual jacket with a warm inner lining.'],
    ['Jeans', 2199, 'Jeans', C(0.18, 0.30, 0.55), 'Classic blue stretch-denim jeans with a comfortable regular fit.'],
    ['T-Shirt', 599, 'TShirt', C(0.95, 0.75, 0.20), 'Soft 100% cotton round-neck t-shirt for everyday wear.']]],
  ['ELECTRONICS STORE', 'Explore smartphones, laptops, headphones and smartwatches.', C(0.15, 0.45, 0.90), C(0.88, 0.92, 0.97), C(0.55, 0.60, 0.68), [
    ['Smartphone', 29999, 'Smartphone', C(0.12, 0.12, 0.14), 'Modern smartphone with a 6.5-inch display and triple camera, available in the Electronics Store.'],
    ['Laptop', 59999, 'Laptop', C(0.70, 0.72, 0.75), 'Lightweight 14-inch laptop with a fast processor and all-day battery life.'],
    ['Headphones', 4999, 'Headphones', C(0.10, 0.10, 0.12), 'Wireless over-ear headphones with active noise cancellation.'],
    ['Smartwatch', 8999, 'Smartwatch', C(0.15, 0.15, 0.18), 'Fitness smartwatch with heart-rate monitor, GPS and notifications.']]],
  ['SPORTS STORE', 'Explore footballs, basketballs, sports shoes and tennis rackets.', C(0.15, 0.65, 0.30), C(0.90, 0.96, 0.90), C(0.45, 0.55, 0.45), [
    ['Football', 1499, 'Football', C(0.97, 0.97, 0.97), 'FIFA-size 5 match football with durable stitched panels.'],
    ['Basketball', 1799, 'Basketball', C(0.92, 0.45, 0.12), 'Official size 7 indoor/outdoor basketball with superior grip.'],
    ['Sports Shoes', 3999, 'SportsShoes', C(0.90, 0.20, 0.20), 'Cushioned training shoes for gym workouts and court sports.'],
    ['Tennis Racket', 2499, 'TennisRacket', C(0.10, 0.45, 0.80), 'Lightweight graphite tennis racket for beginners and intermediate players.']]],
  ['FOOTWEAR STORE', 'Explore sneakers, running shoes, sandals and boots.', C(0.80, 0.45, 0.15), C(0.97, 0.93, 0.87), C(0.62, 0.50, 0.40), [
    ['Sneakers', 2999, 'Sneakers', C(0.95, 0.95, 0.95), 'Classic low-top canvas sneakers that go with everything.'],
    ['Running Shoes', 4499, 'RunningShoes', C(0.20, 0.75, 0.85), 'Breathable mesh running shoes with responsive foam cushioning.'],
    ['Sandals', 899, 'Sandals', C(0.55, 0.35, 0.20), 'Comfortable everyday sandals with adjustable straps.'],
    ['Boots', 5499, 'Boots', C(0.40, 0.25, 0.12), 'Genuine leather ankle boots with a rugged anti-slip sole.']]],
  ['GROCERY STORE', 'Explore fresh juices, cereals, milk and snacks.', C(0.55, 0.75, 0.15), C(0.96, 0.98, 0.88), C(0.60, 0.62, 0.50), [
    ['Juice Bottle', 120, 'JuiceBottle', C(0.98, 0.60, 0.10), '1 litre bottle of 100% natural orange juice with no added sugar.'],
    ['Cereal Box', 349, 'CerealBox', C(0.98, 0.80, 0.20), 'Crunchy whole-grain breakfast cereal, 500 g family pack.'],
    ['Milk Bottle', 65, 'MilkBottle', C(0.98, 0.98, 0.98), '1 litre bottle of fresh toned milk from local farms.'],
    ['Snack Packet', 40, 'SnackPacket', C(0.85, 0.15, 0.15), 'Crispy salted potato chips, 90 g party pack.']]],
  ['ACCESSORIES STORE', 'Explore watches, sunglasses, backpacks and wallets.', C(0.55, 0.30, 0.80), C(0.94, 0.91, 0.98), C(0.55, 0.50, 0.62), [
    ['Watch', 6999, 'Watch', C(0.85, 0.70, 0.30), 'Elegant analog wrist watch with a genuine leather strap.'],
    ['Sunglasses', 1999, 'Sunglasses', C(0.10, 0.10, 0.10), 'Polarised UV400 sunglasses with a lightweight frame.'],
    ['Backpack', 2499, 'Backpack', C(0.20, 0.35, 0.55), 'Water-resistant 30 L backpack with a padded laptop compartment.'],
    ['Wallet', 999, 'Wallet', C(0.45, 0.25, 0.12), 'Slim genuine leather wallet with RFID protection.']]],
].map(([name, desc, accent, wall, floor, products]) => ({ name, desc, accent, wall, floor,
  products: products.map(([n, price, model, color, d]) => ({ name: n, price, model, color, desc: d })) }));

export function formatPrice(v) {
  const s = String(v); if (s.length <= 3) return '₹' + s;
  const last3 = s.slice(-3), rest = s.slice(0, -3);
  let out = ''; const fg = rest.length % 2;
  for (let i = 0; i < rest.length; i++) { if (i > 0 && (i - fg) % 2 === 0) out += ','; out += rest[i]; }
  return '₹' + out + ',' + last3;
}

// ------------------------------------------------------------ product factory
const Metal = C(0.62, 0.64, 0.67), Dark = C(0.08, 0.08, 0.09), White = C(0.96, 0.96, 0.96), Screen = C(0.10, 0.35, 0.75);
const Cube = (p, n, pos, s, c, e = [0, 0, 0], sm = 0.2) => part(n, 'cube', p, pos, s, M(c, sm), e);
const Cyl = (p, n, pos, s, c, e = [0, 0, 0], sm = 0.2) => part(n, 'cylinder', p, pos, s, M(c, sm), e);
const Sph = (p, n, pos, s, c, sm = 0.3) => part(n, 'sphere', p, pos, s, M(c, sm));

function stand(t, h) {
  Cyl(t, 'StandBase', [0, 0.01, -0.05], [0.3, 0.01, 0.3], Metal, [0, 0, 0], 0.6);
  Cyl(t, 'StandPole', [0, h * 0.5, -0.05], [0.03, h * 0.5, 0.03], Metal, [0, 0, 0], 0.6);
}
function garment(t, c, len, ang, collar, zip) {
  stand(t, 0.9);
  Cube(t, 'Body', [0, 0.6, 0], [0.44, 0.54, 0.07], c);
  const sx = 0.22 + Math.sin(ang * D2R) * len * 0.5 + 0.04, sy = 0.84 - Math.cos(ang * D2R) * len * 0.5;
  Cube(t, 'SleeveL', [-sx, sy, 0], [0.13, len, 0.065], c, [0, 0, -ang]);
  Cube(t, 'SleeveR', [sx, sy, 0], [0.13, len, 0.065], c, [0, 0, ang]);
  Cube(t, 'Collar', [0, 0.88, 0.005], [0.18, 0.05, 0.075], collar);
  if (zip) {
    Cube(t, 'Zip', [0, 0.6, 0.037], [0.015, 0.52, 0.005], Metal, [0, 0, 0], 0.7);
    Cube(t, 'PocketL', [-0.12, 0.45, 0.037], [0.1, 0.08, 0.005], mul(c, 0.7));
    Cube(t, 'PocketR', [0.12, 0.45, 0.037], [0.1, 0.08, 0.005], mul(c, 0.7));
  } else Cube(t, 'Placket', [0, 0.6, 0.037], [0.02, 0.5, 0.004], mul(c, 0.75));
}
function shoe(s, model, c) {
  if (model === 'Sandals') {
    Cube(s, 'Sole', [0, 0.015, 0], [0.1, 0.03, 0.26], C(0.3, 0.2, 0.12));
    Cube(s, 'StrapFront', [0, 0.045, 0.06], [0.102, 0.03, 0.04], c);
    Cube(s, 'StrapBack', [0, 0.05, -0.04], [0.102, 0.04, 0.035], c);
  } else if (model === 'Boots') {
    Cube(s, 'Sole', [0, 0.02, 0], [0.11, 0.04, 0.28], Dark);
    Cube(s, 'Foot', [0, 0.08, 0.02], [0.1, 0.08, 0.22], c);
    Cube(s, 'Shaft', [0, 0.18, -0.06], [0.1, 0.24, 0.13], c);
    Cube(s, 'Lace', [0, 0.14, 0], [0.05, 0.12, 0.01], mul(c, 0.6), [-20, 0, 0]);
  } else {
    const running = model === 'RunningShoes', sole = running ? 0.045 : 0.03;
    Cube(s, 'Sole', [0, sole * 0.5, 0], [0.105, sole, 0.28], White);
    Cube(s, 'Upper', [0, sole + 0.045, -0.03], [0.1, 0.09, 0.2], c);
    Cube(s, 'Toe', [0, sole + 0.025, 0.08], [0.1, 0.05, 0.1], c);
    Cube(s, 'Laces', [0, sole + 0.091, 0], [0.05, 0.004, 0.1], White);
    const stripe = model === 'SportsShoes' ? White : running ? C(1, 0.5, 0.1) : C(0.2, 0.3, 0.7);
    Cube(s, 'Stripe', [0, sole + 0.045, -0.03], [0.104, 0.02, 0.12], stripe, [-15, 0, 0]);
  }
}
function wrist(t, c, smart) {
  Cube(t, 'Pillow', [0, 0.09, 0], [0.1, 0.18, 0.07], C(0.25, 0.25, 0.28));
  const strap = smart ? c : C(0.4, 0.22, 0.1);
  Cube(t, 'StrapFront', [0, 0.09, 0.038], [0.045, 0.18, 0.006], strap);
  Cube(t, 'StrapTop', [0, 0.183, 0], [0.045, 0.006, 0.08], strap);
  if (smart) {
    Cube(t, 'Case', [0, 0.12, 0.05], [0.075, 0.09, 0.02], c, [0, 0, 0], 0.7);
    Cube(t, 'Screen', [0, 0.12, 0.061], [0.062, 0.077, 0.003], C(0.1, 0.6, 0.4), [0, 0, 0], 0.9);
  } else {
    Cyl(t, 'Case', [0, 0.12, 0.05], [0.085, 0.01, 0.085], c, [90, 0, 0], 0.8);
    Cyl(t, 'Dial', [0, 0.12, 0.052], [0.07, 0.0115, 0.07], White, [90, 0, 0], 0.6);
    Cube(t, 'HourHand', [0, 0.13, 0.064], [0.004, 0.022, 0.002], Dark);
    Cube(t, 'MinuteHand', [0.012, 0.12, 0.064], [0.028, 0.003, 0.002], Dark);
  }
}
function bottle(t, c, cap, h) {
  const half = h * 0.5;
  Cyl(t, 'Body', [0, half, 0], [0.1, half, 0.1], c, [0, 0, 0], 0.6);
  Cyl(t, 'Label', [0, half, 0], [0.103, h * 0.18, 0.103], cap);
  Cyl(t, 'Shoulder', [0, h + 0.015, 0], [0.065, 0.015, 0.065], c, [0, 0, 0], 0.6);
  Cyl(t, 'Cap', [0, h + 0.04, 0], [0.045, 0.012, 0.045], cap);
}
export function createProductModel(model, name, c, parent) {
  const t = grp(name, parent);
  switch (model) {
    case 'Shirt': garment(t, c, 0.38, 22, White, false); break;
    case 'Jacket': garment(t, c, 0.52, 10, Dark, true); break;
    case 'TShirt': garment(t, c, 0.17, 45, mul(c, 0.8), false); break;
    case 'Jeans':
      stand(t, 0.9);
      Cube(t, 'Waist', [0, 0.86, 0], [0.36, 0.08, 0.1], mul(c, 0.85));
      Cube(t, 'LegL', [-0.095, 0.5, 0], [0.16, 0.64, 0.09], c);
      Cube(t, 'LegR', [0.095, 0.5, 0], [0.16, 0.64, 0.09], c);
      Cube(t, 'Button', [0, 0.86, 0.052], [0.025, 0.025, 0.005], Metal, [0, 0, 0], 0.7); break;
    case 'Smartphone': {
      Cube(t, 'Stand', [0, 0.015, -0.02], [0.18, 0.03, 0.14], Metal, [0, 0, 0], 0.6);
      const ph = grp('Phone', t, [0, 0.03, 0], [-12, 0, 0]);
      Cube(ph, 'Body', [0, 0.18, 0], [0.18, 0.36, 0.02], c, [0, 0, 0], 0.7);
      Cube(ph, 'Screen', [0, 0.18, 0.0105], [0.16, 0.33, 0.002], Screen, [0, 0, 0], 0.9);
      Cube(ph, 'Camera', [0.05, 0.31, -0.0115], [0.05, 0.05, 0.004], Dark); break; }
    case 'Laptop': {
      Cube(t, 'Base', [0, 0.0125, 0], [0.5, 0.025, 0.34], c, [0, 0, 0], 0.6);
      Cube(t, 'Keyboard', [0, 0.026, 0.03], [0.44, 0.004, 0.17], Dark);
      Cube(t, 'Touchpad', [0, 0.026, 0.13], [0.12, 0.004, 0.06], mul(c, 0.85));
      const lid = grp('Lid', t, [0, 0.025, -0.165], [-15, 0, 0]);
      Cube(lid, 'Back', [0, 0.17, 0], [0.5, 0.34, 0.015], c, [0, 0, 0], 0.6);
      Cube(lid, 'Display', [0, 0.17, 0.008], [0.46, 0.3, 0.002], Screen, [0, 0, 0], 0.9); break; }
    case 'Headphones':
      Cyl(t, 'StandBase', [0, 0.01, 0], [0.18, 0.01, 0.18], Metal, [0, 0, 0], 0.6);
      Cyl(t, 'StandPole', [0, 0.22, 0], [0.03, 0.21, 0.03], Metal, [0, 0, 0], 0.6);
      Cube(t, 'BandTop', [0, 0.45, 0], [0.3, 0.03, 0.05], c);
      Cube(t, 'BandL', [-0.15, 0.38, 0], [0.03, 0.15, 0.04], c);
      Cube(t, 'BandR', [0.15, 0.38, 0], [0.03, 0.15, 0.04], c);
      Cyl(t, 'CupL', [-0.15, 0.27, 0], [0.12, 0.03, 0.12], c, [0, 0, 90]);
      Cyl(t, 'CupR', [0.15, 0.27, 0], [0.12, 0.03, 0.12], c, [0, 0, 90]);
      Cyl(t, 'CushionL', [-0.115, 0.27, 0], [0.1, 0.01, 0.1], Dark, [0, 0, 90]);
      Cyl(t, 'CushionR', [0.115, 0.27, 0], [0.1, 0.01, 0.1], Dark, [0, 0, 90]);
      Cyl(t, 'AccentL', [-0.182, 0.27, 0], [0.06, 0.004, 0.06], Screen, [0, 0, 90], 0.8);
      Cyl(t, 'AccentR', [0.182, 0.27, 0], [0.06, 0.004, 0.06], Screen, [0, 0, 90], 0.8); break;
    case 'Smartwatch': wrist(t, c, true); break;
    case 'Watch': wrist(t, c, false); break;
    case 'Football': {
      Cyl(t, 'Ring', [0, 0.02, 0], [0.14, 0.02, 0.14], Metal, [0, 0, 0], 0.6);
      const ctr = [0, 0.16, 0];
      Sph(t, 'Ball', ctr, [0.24, 0.24, 0.24], c);
      [[0, 0.3, 1], [0.9, 0.4, 0.3], [-0.9, 0.4, 0.3], [0.5, 1, -0.4], [-0.5, 1, -0.4], [0, -0.2, -1], [0, 1, 0.3]].forEach((d, i) => {
        const v = new THREE.Vector3(...d).normalize().multiplyScalar(0.104);
        Sph(t, 'Patch' + i, [ctr[0] + v.x, ctr[1] + v.y, ctr[2] + v.z], [0.05, 0.05, 0.05], Dark);
      }); break; }
    case 'Basketball': {
      Cyl(t, 'Ring', [0, 0.02, 0], [0.14, 0.02, 0.14], Metal, [0, 0, 0], 0.6);
      const ctr = [0, 0.165, 0];
      Sph(t, 'Ball', ctr, [0.25, 0.25, 0.25], c);
      Cyl(t, 'SeamH', ctr, [0.252, 0.003, 0.252], Dark);
      Cyl(t, 'SeamV1', ctr, [0.252, 0.003, 0.252], Dark, [90, 0, 0]);
      Cyl(t, 'SeamV2', ctr, [0.252, 0.003, 0.252], Dark, [0, 0, 90]); break; }
    case 'TennisRacket':
      Cube(t, 'Stand', [0, 0.015, 0], [0.2, 0.03, 0.12], Metal, [0, 0, 0], 0.6);
      Cyl(t, 'Handle', [0, 0.16, 0], [0.035, 0.13, 0.035], Dark);
      Cube(t, 'ThroatL', [-0.03, 0.32, 0], [0.015, 0.08, 0.015], c, [0, 0, 20]);
      Cube(t, 'ThroatR', [0.03, 0.32, 0], [0.015, 0.08, 0.015], c, [0, 0, -20]);
      Cyl(t, 'Frame', [0, 0.52, 0], [0.27, 0.008, 0.35], c, [90, 0, 0], 0.5);
      Cyl(t, 'Strings', [0, 0.52, 0], [0.235, 0.011, 0.315], C(0.95, 0.95, 0.8), [90, 0, 0]); break;
    case 'SportsShoes': case 'Sneakers': case 'RunningShoes': case 'Sandals': case 'Boots':
      shoe(grp('LeftShoe', t, [-0.075, 0, 0], [0, -6, 0]), model, c);
      shoe(grp('RightShoe', t, [0.075, 0, 0], [0, 6, 0]), model, c); break;
    case 'JuiceBottle': bottle(t, c, C(0.15, 0.6, 0.2), 0.22); break;
    case 'MilkBottle': bottle(t, c, C(0.15, 0.35, 0.85), 0.24); break;
    case 'CerealBox':
      Cube(t, 'Box', [0, 0.16, 0], [0.22, 0.32, 0.07], c);
      Cube(t, 'Banner', [0, 0.24, 0.0355], [0.2, 0.07, 0.002], C(0.85, 0.15, 0.15));
      Cyl(t, 'Bowl', [0, 0.11, 0.036], [0.12, 0.002, 0.08], White, [90, 0, 0]); break;
    case 'SnackPacket':
      Cube(t, 'Pack', [0, 0.14, 0], [0.2, 0.24, 0.05], c, [0, 0, 0], 0.7);
      Cube(t, 'TopSeal', [0, 0.27, 0], [0.2, 0.025, 0.015], Metal, [0, 0, 0], 0.7);
      Cube(t, 'BottomSeal', [0, 0.015, 0], [0.2, 0.025, 0.015], Metal, [0, 0, 0], 0.7);
      Cube(t, 'Window', [0, 0.12, 0.026], [0.13, 0.07, 0.002], C(1, 0.85, 0.3)); break;
    case 'Sunglasses':
      Cyl(t, 'StandBase', [0, 0.01, -0.06], [0.14, 0.01, 0.14], Metal, [0, 0, 0], 0.6);
      Cyl(t, 'StandPole', [0, 0.1, -0.06], [0.025, 0.09, 0.025], Metal, [0, 0, 0], 0.6);
      Cyl(t, 'LensL', [-0.058, 0.2, 0], [0.09, 0.006, 0.07], c, [90, 0, 0], 0.95);
      Cyl(t, 'LensR', [0.058, 0.2, 0], [0.09, 0.006, 0.07], c, [90, 0, 0], 0.95);
      Cube(t, 'Bridge', [0, 0.21, 0], [0.03, 0.01, 0.01], Dark);
      Cube(t, 'ArmL', [-0.105, 0.21, -0.08], [0.008, 0.012, 0.16], Dark);
      Cube(t, 'ArmR', [0.105, 0.21, -0.08], [0.008, 0.012, 0.16], Dark); break;
    case 'Backpack':
      Cube(t, 'Body', [0, 0.2, 0], [0.3, 0.4, 0.16], c);
      Cube(t, 'Flap', [0, 0.39, 0.01], [0.31, 0.06, 0.17], mul(c, 0.8));
      Cube(t, 'Pocket', [0, 0.14, 0.09], [0.22, 0.16, 0.04], mul(c, 0.8));
      Cube(t, 'Zip', [0, 0.22, 0.111], [0.2, 0.008, 0.002], Metal, [0, 0, 0], 0.7);
      Cube(t, 'Handle', [0, 0.44, 0], [0.08, 0.03, 0.02], Dark);
      Cube(t, 'StrapL', [-0.08, 0.22, -0.09], [0.04, 0.34, 0.02], Dark);
      Cube(t, 'StrapR', [0.08, 0.22, -0.09], [0.04, 0.34, 0.02], Dark); break;
    case 'Wallet': {
      Cube(t, 'Stand', [0, 0.02, -0.02], [0.16, 0.04, 0.1], Metal, [0, 0, 0], 0.6);
      const w = grp('Wallet', t, [0, 0.04, 0], [-20, 0, 0]);
      Cube(w, 'Body', [0, 0.06, 0], [0.18, 0.12, 0.03], c);
      Cube(w, 'Stitch', [0, 0.06, 0.0155], [0.16, 0.1, 0.001], mul(c, 1.25));
      Cube(w, 'Card', [0.03, 0.125, 0], [0.12, 0.02, 0.02], C(0.2, 0.45, 0.85)); break; }
  }
  return t;
}

// ------------------------------------------------------------ mall builder (port of MallBuilder.cs)
export const HalfWidth = 20, Length = 62, H = 5, CorridorHalf = 4, LobbyEnd = 12, ShopsEnd = 54, ShopWidth = 14, ShopDepth = 16;
const LabelDark = [0.08, 0.09, 0.11, 0.88], LabelGold = C(1, 0.83, 0.3);
export const products = []; // {name, shop, group, featured}
export const lights = [];
export const shopAreas = [];

function pointLight(parent, pos, range, intensity, color) {
  const l = new THREE.PointLight(0xffffff, intensity, range, 1.2);
  l.color.setRGB(...color, THREE.SRGBColorSpace);
  l.position.set(...pos); parent.add(l); lights.push(l);
}
const ceilingPanel = (p, pos, s) => block('CeilingLightPanel', p, pos, s, M(C(1, 1, 0.97), 0.9), false, false);

function tree(p, pos) {
  const t = grp('Tree', p, pos);
  part('Trunk', 'cylinder', t, [0, 1.5, 0], [0.35, 1.5, 0.35], M(C(0.4, 0.28, 0.18)));
  part('Leaves', 'sphere', t, [0, 3.8, 0], [2.8, 2.6, 2.8], M(C(0.2, 0.5, 0.22)));
}
function bench(p, pos, yaw) {
  const b = grp('Bench', p, pos, [0, yaw, 0]);
  const wood = M(C(0.55, 0.38, 0.22), 0.3), metal = M(C(0.25, 0.25, 0.28), 0.5);
  part('Seat', 'cube', b, [0, 0.45, 0], [2.2, 0.08, 0.55], wood);
  part('Back', 'cube', b, [0, 0.75, -0.25], [2.2, 0.4, 0.06], wood);
  part('LegL', 'cube', b, [-0.95, 0.21, 0], [0.08, 0.42, 0.5], metal);
  part('LegR', 'cube', b, [0.95, 0.21, 0], [0.08, 0.42, 0.5], metal);
}
function planter(p, pos) {
  const t = grp('Planter', p, pos);
  part('Pot', 'cube', t, [0, 0.3, 0], [0.9, 0.6, 0.9], M(C(0.85, 0.85, 0.82), 0.4));
  part('Soil', 'cube', t, [0, 0.6, 0], [0.8, 0.02, 0.8], M(C(0.3, 0.2, 0.12)));
  part('Bush', 'sphere', t, [0, 1.05, 0], [0.95, 1.0, 0.95], M(C(0.22, 0.55, 0.25)));
}

function buildExterior(ext) {
  block('Ground', ext, [0, -0.25, 25], [100, 0.5, 120], M(C(0.36, 0.55, 0.30), 0.05));
  const paving = M(C(0.78, 0.77, 0.74), 0.1, [16, 9]);
  block('EntrancePlaza', ext, [0, 0.005, -9], [32, 0.01, 18], paving, false);
  block('ExitPlaza', ext, [0, 0.005, 67], [16, 0.01, 10], M(C(0.78, 0.77, 0.74), 0.1, [8, 5]), false);
  block('Road', ext, [0, 0.004, -22], [100, 0.01, 8], M(C(0.2, 0.2, 0.22)), false);
  for (let i = -6; i <= 6; i++) block('RoadMarking', ext, [i * 7, 0.012, -22], [3, 0.01, 0.25], M(C(0.95, 0.95, 0.95)), false, false);
  [[-13, -6], [13, -6], [-13, -14], [13, -14], [-25, 8], [25, 8], [-25, 30], [25, 30], [-25, 52], [25, 52], [-10, 70], [10, 70]]
    .forEach(([x, z]) => tree(ext, [x, 0, z]));
  for (const x of [-8, 8]) {
    const lamp = grp('StreetLamp', ext, [x, 0, -12]);
    part('Pole', 'cylinder', lamp, [0, 2, 0], [0.15, 2, 0.15], M(C(0.2, 0.2, 0.22), 0.5));
    part('Lamp', 'sphere', lamp, [0, 4.1, 0], [0.45, 0.45, 0.45], M(C(1, 0.97, 0.85), 0.9));
  }
  bench(ext, [-8, 0, -6], 0); bench(ext, [8, 0, -6], 0);
}

function buildShell(b) {
  const wall = M(C(0.93, 0.92, 0.89)), facade = M(C(0.28, 0.31, 0.36), 0.3), gold = M(C(0.95, 0.72, 0.25), 0.5);
  const floor = M(C(0.96, 0.95, 0.93), 0.35, [20, 31]);
  block('Floor', b, [0, 0.01, Length / 2], [40, 0.02, Length], floor);
  block('Ceiling', b, [0, H + 0.1, Length / 2], [40.6, 0.2, Length + 0.6], M(C(0.97, 0.97, 0.97)), true, false).userData.ceiling = true;
  const T = 0.3;
  block('FrontWall_L', b, [-11.5, H / 2, 0], [17, H, T], wall);
  block('FrontWall_R', b, [11.5, H / 2, 0], [17, H, T], wall);
  block('FrontWall_Header', b, [0, (3.6 + H) / 2, 0], [6, H - 3.6, T], wall);
  block('BackWall_L', b, [-11, H / 2, Length], [18, H, T], wall);
  block('BackWall_R', b, [11, H / 2, Length], [18, H, T], wall);
  block('BackWall_Header', b, [0, (3 + H) / 2, Length], [4, H - 3, T], wall);
  block('SideWall_L', b, [-HalfWidth, H / 2, Length / 2], [T, H, Length + T], wall);
  block('SideWall_R', b, [HalfWidth, H / 2, Length / 2], [T, H, Length + T], wall);
  block('RoofTrim_Front', b, [0, H + 0.45, -0.05], [40.8, 0.5, 0.5], facade, false);
  block('RoofTrim_Back', b, [0, H + 0.45, Length + 0.05], [40.8, 0.5, 0.5], facade, false);
  const e = grp('MainEntrance', b);
  block('FramePillar_L', e, [-3.15, 1.8, 0], [0.3, 3.6, 0.45], gold);
  block('FramePillar_R', e, [3.15, 1.8, 0], [0.3, 3.6, 0.45], gold);
  block('Canopy', e, [0, 3.7, -1.7], [9.4, 0.2, 3.4], facade);
  block('CanopyFascia', e, [0, 3.62, -3.38], [9.4, 0.4, 0.06], gold, false);
  block('Column_L', e, [-4.3, 1.8, -3], [0.3, 3.6, 0.3], facade);
  block('Column_R', e, [4.3, 1.8, -3], [0.3, 3.6, 0.3], facade);
  block('DoorMat', e, [0, 0.025, 1.2], [5, 0.01, 1.8], M(C(0.25, 0.22, 0.22)), false);
  block('MallSignBoard', e, [0, 4.4, -0.3], [15, 1.1, 0.15], facade, false);
  label('MallSign', 'VIRTUAL SHOPPING COMPLEX', [0, 4.4, -0.39], [0, 0, -1], [14.6, 1], 120, LabelGold);
  label('EntranceSign', 'MAIN ENTRANCE', [0, 3.62, -3.42], [0, 0, -1], [5, 0.36], 56, C(0.1, 0.1, 0.12));
  label('EntranceInside', 'MAIN ENTRANCE', [0, 4.3, 0.17], [0, 0, 1], [5.6, 1.0], 90, LabelGold, LabelDark);
}

function directoryBoard(p, pos, text) {
  const b = grp('DirectoryBoard', p, pos);
  const dark = M(C(0.15, 0.17, 0.2), 0.4);
  part('Panel', 'cube', b, [0, 1.9, 0], [3.6, 2.4, 0.12], dark);
  part('Leg_L', 'cube', b, [-1.5, 0.35, 0], [0.12, 0.7, 0.12], dark);
  part('Leg_R', 'cube', b, [1.5, 0.35, 0], [0.12, 0.7, 0.12], dark);
  label('DirectoryText', text, [pos[0], pos[1] + 1.9, pos[2] - 0.07], [0, 0, -1], [3.4, 2.25], 52, C(1, 1, 1));
}
function hangingSign(p, name, pos, front, back, h = 0.7, fs = 56) {
  const s = grp(name, p, pos);
  block('Board', s, [0, 0, 0], [7.6, h + (h > 0.75 ? 0 : 0), 0.08], M(C(0.15, 0.17, 0.2)), false);
  block('Rod_L', s, [-3, 0.57, 0], [0.04, 0.45, 0.04], M(C(0.5, 0.5, 0.5)), false);
  block('Rod_R', s, [3, 0.57, 0], [0.04, 0.45, 0.04], M(C(0.5, 0.5, 0.5)), false);
  label('Front', front, [pos[0], pos[1], pos[2] - 0.05], [0, 0, -1], [7.4, h - 0.08], fs, C(1, 1, 1));
  label('Back', back, [pos[0], pos[1], pos[2] + 0.05], [0, 0, 1], [7.4, h - 0.08], fs, C(1, 1, 1));
}

function buildLobby(l) {
  const f = grp('Fountain', l, [0, 0, 6.5]);
  const stone = M(C(0.8, 0.78, 0.75), 0.4);
  part('Basin', 'cylinder', f, [0, 0.3, 0], [3.2, 0.3, 3.2], stone);
  part('Water', 'cylinder', f, [0, 0.55, 0], [2.9, 0.06, 2.9], M(C(0.25, 0.55, 0.85), 0.95));
  part('Pillar', 'cylinder', f, [0, 1.0, 0], [0.35, 0.5, 0.35], stone);
  part('TopBowl', 'cylinder', f, [0, 1.5, 0], [1.2, 0.08, 1.2], stone);
  part('Spray', 'sphere', f, [0, 1.75, 0], [0.6, 0.45, 0.6], M(C(0.55, 0.8, 1), 0.95));
  directoryBoard(l, [-7, 0, 9.5], 'MALL DIRECTORY\n<size=44>←  LEFT SIDE</size>\n\n<color=#FFD54A>1</color>  FASHION STORE\n<color=#FFD54A>3</color>  SPORTS STORE\n<color=#FFD54A>5</color>  GROCERY STORE');
  directoryBoard(l, [7, 0, 9.5], 'MALL DIRECTORY\n<size=44>RIGHT SIDE  →</size>\n\n<color=#FFD54A>2</color>  ELECTRONICS STORE\n<color=#FFD54A>4</color>  FOOTWEAR STORE\n<color=#FFD54A>6</color>  ACCESSORIES STORE');
  const desk = grp('InformationDesk', l, [-13, 0, 4]);
  block('Desk', desk, [0, 0.55, 0], [3.2, 1.1, 1], M(C(0.28, 0.31, 0.36), 0.3));
  block('DeskTop', desk, [0, 1.13, 0], [3.4, 0.06, 1.1], M(C(0.95, 0.95, 0.95), 0.6), false);
  label('DeskSign', 'INFORMATION', [-13, 0.6, 3.48], [0, 0, -1], [3, 0.45], 60, C(1, 1, 1));
  bench(l, [13, 0, 4], 180); bench(l, [13, 0, 8], 0);
  planter(l, [-18.8, 0, 1.2]); planter(l, [18.8, 0, 1.2]); planter(l, [-18.8, 0, 10.8]); planter(l, [18.8, 0, 10.8]);
  hangingSign(l, 'CorridorEntranceSign', [0, 4.15, 12], '↑  ALL SHOPS   |   EXIT AT THE END  ↑', '↑  MAIN LOBBY & ENTRANCE  ↑', 0.8, 64);
  const warm = C(1, 0.95, 0.88);
  pointLight(l, [0, 4.4, 6], 18, 1.2, warm);
  pointLight(l, [-12, 4.4, 6], 12, 0.8, warm);
  pointLight(l, [12, 4.4, 6], 12, 0.8, warm);
  for (let i = -2; i <= 2; i++) ceilingPanel(l, [i * 7.5, 4.98, 6], [3, 0.04, 1]);
}

function buildCorridor(c) {
  const mid = (LobbyEnd + ShopsEnd) / 2;
  block('FloorStripe', c, [0, 0.025, mid], [1.4, 0.01, ShopsEnd - LobbyEnd], M(C(0.55, 0.57, 0.62), 0.5), false);
  for (let row = 0; row < 3; row++) {
    const z = LobbyEnd + ShopWidth * (row + 0.5);
    bench(c, [0, 0, z], 90); planter(c, [0, 0, z - 2.4]); planter(c, [0, 0, z + 2.4]);
    const L = SHOPS[row * 2].name, R = SHOPS[row * 2 + 1].name;
    hangingSign(c, 'DirectionSign', [0, 4.2, z - 4.5], `← ${L}        ${R} →`, `← ${R}        ${L} →`);
    pointLight(c, [0, 4.4, z], 12, 1.0, C(1, 0.97, 0.92));
    ceilingPanel(c, [0, 4.98, z - 3.5], [1.2, 0.04, 3]); ceilingPanel(c, [0, 4.98, z + 3.5], [1.2, 0.04, 3]);
  }
}

function buildExitHall(h) {
  const green = M(C(0.1, 0.6, 0.3), 0.4);
  block('ExitSignBoard', h, [0, 3.95, Length - 0.2], [3.4, 0.9, 0.1], green, false);
  label('ExitSign', 'EXIT  ↑', [0, 3.95, Length - 0.26], [0, 0, -1], [3.2, 0.8], 90, C(1, 1, 1));
  block('ExitSignBoardOutside', h, [0, 3.95, Length + 0.2], [3.4, 0.9, 0.1], green, false);
  label('ExitSignOutside', 'EXIT', [0, 3.95, Length + 0.26], [0, 0, 1], [3.2, 0.8], 90, C(1, 1, 1));
  label('ThankYou_L', 'THANK YOU FOR\nVISITING!', [-10, 2.6, Length - 0.17], [0, 0, -1], [7, 1.8], 80, LabelGold, LabelDark);
  label('ThankYou_R', 'PLEASE VISIT\nAGAIN', [10, 2.6, Length - 0.17], [0, 0, -1], [7, 1.8], 80, LabelGold, LabelDark);
  block('ExitFrame_L', h, [-2.15, 1.5, Length], [0.3, 3, 0.45], green);
  block('ExitFrame_R', h, [2.15, 1.5, Length], [0.3, 3, 0.45], green);
  bench(h, [-12, 0, 57], 0); bench(h, [12, 0, 57], 0);
  planter(h, [-18.8, 0, 61]); planter(h, [18.8, 0, 61]);
  pointLight(h, [0, 4.4, 58], 16, 1.1, C(1, 0.97, 0.92));
  ceilingPanel(h, [-8, 4.98, 58], [3, 0.04, 1]); ceilingPanel(h, [8, 4.98, 58], [3, 0.04, 1]);
}

function rendererBoundsTop(obj) {
  const box = new THREE.Box3().setFromObject(obj);
  return box.max.y;
}

function createProduct(p, shop, parent, pos, scale, featured) {
  const g = createProductModel(p.model, p.name, p.color, parent);
  g.position.set(...pos); g.scale.setScalar(scale); g.updateMatrixWorld(true);
  products.push({ name: p.name, shop: shop.name, group: g, featured });
  if (featured) g.traverse(o => { o.userData.static = false; });
  return g;
}

function buildShop(def, parent, center, yaw, number) {
  const hw = ShopWidth / 2, hd = ShopDepth / 2, doorHalf = 2;
  const shop = grp(def.name, parent, center, [0, yaw, 0]);
  const LL = (name, text, lp, lf, size, fs, color, bg = null) => label(name, text, tp(shop, lp), td(shop, lf), size, fs, color, bg);
  const wall = M(def.wall), floor = M(def.floor, 0.35, [7, 8]), accent = M(def.accent, 0.3), accentDark = M(mul(def.accent, 0.55), 0.3), white = M(C(0.97, 0.97, 0.97), 0.5);
  const s = grp('Structure', shop);
  block('Floor', s, [0, 0.02, 0], [ShopWidth - 0.4, 0.02, ShopDepth - 0.4], floor, false);
  block('BackWall', s, [0, H / 2, -hd + 0.1], [ShopWidth - 0.4, H, 0.2], wall);
  block('SideWall_L', s, [-hw + 0.1, H / 2, 0], [0.2, H, ShopDepth], wall);
  block('SideWall_R', s, [hw - 0.1, H / 2, 0], [0.2, H, ShopDepth], wall);
  const fw = hw - 0.2 - doorHalf, fx = doorHalf + fw / 2;
  block('FrontWall_L', s, [-fx, H / 2, hd - 0.1], [fw, H, 0.2], wall);
  block('FrontWall_R', s, [fx, H / 2, hd - 0.1], [fw, H, 0.2], wall);
  block('DoorHeader', s, [0, (3.2 + H) / 2, hd - 0.1], [doorHalf * 2, H - 3.2, 0.2], wall);
  block('DoorFrame_L', s, [-doorHalf - 0.1, 1.6, hd - 0.1], [0.2, 3.2, 0.32], accent);
  block('DoorFrame_R', s, [doorHalf + 0.1, 1.6, hd - 0.1], [0.2, 3.2, 0.32], accent);
  block('DoorFrame_Top', s, [0, 3.25, hd - 0.1], [doorHalf * 2 + 0.4, 0.12, 0.32], accent, false);

  const f = grp('Storefront', shop);
  block('Fascia', f, [0, 4.2, hd + 0.04], [ShopWidth - 0.4, 1.4, 0.08], accentDark, false);
  block('NameBoard', f, [0, 4.2, hd + 0.1], [7.2, 1.05, 0.06], white, false);
  LL('ShopName', def.name, [0, 4.2, hd + 0.14], [0, 0, 1], [7, 0.95], 110, mul(def.accent, 0.8));
  LL('ShopNumber', 'SHOP ' + number, [-5.2, 4.2, hd + 0.09], [0, 0, 1], [2.2, 0.5], 56, C(1, 1, 1));
  LL('OpenSign', 'OPEN', [5.2, 4.2, hd + 0.09], [0, 0, 1], [2.2, 0.5], 56, C(0.6, 1, 0.6));
  const glass = M(C(0.55, 0.7, 0.82), 0.95);
  block('Window_L', f, [-fx, 1.7, hd + 0.02], [fw - 0.6, 2.4, 0.04], glass, false);
  block('Window_R', f, [fx, 1.7, hd + 0.02], [fw - 0.6, 2.4, 0.04], glass, false);
  LL('WindowText_L', 'NEW ARRIVALS', [-fx, 1.9, hd + 0.05], [0, 0, 1], [3.6, 0.5], 56, C(1, 1, 1), [0, 0, 0, 0.35]);
  LL('WindowText_R', 'WELCOME!', [fx, 1.9, hd + 0.05], [0, 0, 1], [3.6, 0.5], 56, C(1, 1, 1), [0, 0, 0, 0.35]);
  block('BladeSign', f, [-hw + 1, 3.0, hd + 0.75], [0.08, 0.7, 1.3], accent, false);
  LL('BladeText_A', def.name, [-hw + 1.05, 3.0, hd + 0.75], [1, 0, 0], [1.25, 0.65], 40, C(1, 1, 1));
  LL('BladeText_B', def.name, [-hw + 0.95, 3.0, hd + 0.75], [-1, 0, 0], [1.25, 0.65], 40, C(1, 1, 1));

  const it = grp('Interior', shop);
  block('Rug', it, [0, 0.035, -1], [12, 0.01, 2.8], accentDark, false);
  block('BackSignBoard', it, [0, 3.55, -hd + 0.23], [8.4, 1.1, 0.06], white, false);
  LL('BackSign', def.name, [0, 3.55, -hd + 0.27], [0, 0, 1], [8, 1], 110, mul(def.accent, 0.8));
  block('PosterBoard', it, [-hw + 0.23, 2.3, 1], [0.06, 1.6, 3.4], accent, false);
  LL('PosterText', def.desc, [-hw + 0.27, 2.3, 1], [1, 0, 0], [3.2, 1.4], 48, C(1, 1, 1));
  const lp = tp(shop, [0, 4.2, 0]);
  pointLight(U, [lp.x, lp.y, lp.z], 13, 1.4, lerpC(C(1, 1, 1), def.accent, 0.12));
  ceilingPanel(it, [-3, 4.98, 0], [2.5, 0.04, 0.8]); ceilingPanel(it, [3, 4.98, 0], [2.5, 0.04, 0.8]); ceilingPanel(it, [0, 4.98, -5], [2.5, 0.04, 0.8]);

  const counter = grp('Counter', shop, [4.4, 0, 4.6]);
  part('Body', 'cube', counter, [0, 0.5, 0], [3.4, 1, 0.9], accentDark);
  part('Top', 'cube', counter, [0, 1.03, 0], [3.6, 0.06, 1], white);
  part('Register', 'cube', counter, [1, 1.18, -0.1], [0.45, 0.25, 0.35], M(C(0.15, 0.15, 0.17), 0.5));
  part('RegisterScreen', 'cube', counter, [1, 1.4, -0.15], [0.35, 0.22, 0.03], M(C(0.1, 0.35, 0.75), 0.9), [-15, 0, 0]);
  label('CounterSign', 'SHOP INFO & CHECKOUT\n<size=36>look here and press E</size>', tp(counter, [-0.3, 0.55, 0.47]), td(shop, [0, 0, 1]), [2.6, 0.6], 48, C(1, 1, 1));
  const keeper = grp('Shopkeeper', shop, [4.6, 0, 3.6]);
  part('BodyCapsule', 'capsule', keeper, [0, 0.8, 0], [0.5, 0.8, 0.5], accent);
  part('Head', 'sphere', keeper, [0, 1.75, 0], [0.3, 0.3, 0.3], M(C(0.87, 0.68, 0.52)));
  shopAreas.push({ name: def.name, center, yaw });

  const pr = grp('Products', shop);
  [-5.1, -1.7, 1.7, 5.1].forEach((x, i) => {
    const p = def.products[i];
    const d = grp('Display_' + p.name, pr, [x, 0, -1]);
    block('Podium', d, [0, 0.45, 0], [0.9, 0.9, 0.9], white);
    block('PodiumTrim', d, [0, 0.92, 0], [0.96, 0.04, 0.96], accent, false);
    const item = createProduct(p, def, d, [0, 0.94, 0], 1, true);
    const top = rendererBoundsTop(item);
    const dp = tp(d, [0, 0, 0]);
    label('Label', `<b>${p.name.toUpperCase()}</b>\n<color=#FFD54A>${formatPrice(p.price)}</color>`,
      [dp.x, top + 0.32, dp.z], td(shop, [0, 0, 1]), [1.4, 0.44], 34, C(1, 1, 1), LabelDark, false);
  });
  shelfUnit(shop, pr, def, [-3.5, 0, -hd + 0.65], def.products[0], def.products[1]);
  shelfUnit(shop, pr, def, [3.5, 0, -hd + 0.65], def.products[2], def.products[3]);
}

function shelfUnit(shop, parent, def, pos, a, b) {
  const W = 5.6, Dp = 0.7, Hh = 2.3;
  const u = grp('ShelfUnit', parent, pos);
  const wood = M(C(0.92, 0.9, 0.86), 0.3), trim = M(mul(def.accent, 0.7), 0.3);
  part('Side_L', 'cube', u, [-W / 2 + 0.025, Hh / 2, 0], [0.05, Hh, Dp], trim);
  part('Side_R', 'cube', u, [W / 2 - 0.025, Hh / 2, 0], [0.05, Hh, Dp], trim);
  part('BackPanel', 'cube', u, [0, Hh / 2, -Dp / 2 + 0.02], [W, Hh, 0.04], wood);
  part('Plinth', 'cube', u, [0, 0.075, 0], [W - 0.1, 0.15, Dp - 0.04], trim);
  part('Board_1', 'cube', u, [0, 0.88, 0], [W - 0.1, 0.04, Dp - 0.04], wood);
  part('Board_2', 'cube', u, [0, 1.63, 0], [W - 0.1, 0.04, Dp - 0.04], wood);
  part('TopBoard', 'cube', u, [0, Hh - 0.02, 0], [W, 0.04, Dp], trim);
  const tops = [0.15, 0.9, 1.65], levels = [a, b, a];
  tops.forEach((top, lvl) => {
    const p = levels[lvl];
    for (let k = -1; k <= 1; k++) createProduct(p, def, u, [k * 1.8, top, 0.02], 0.55, false);
    label('PriceTag', `<b>${p.name.toUpperCase()}</b>   ${formatPrice(p.price)}`, tp(u, [0, top - 0.065, Dp / 2 + 0.01]), td(shop, [0, 0, 1]),
      [1.6, 0.12], 22, C(0.1, 0.1, 0.12), [1, 0.92, 0.45, 1], false);
  });
}

export function buildMall(scene) {
  scene.add(U);
  const env = grp('Environment', U);
  buildExterior(grp('Exterior', env));
  buildShell(grp('Building', env));
  buildLobby(grp('Lobby', env));
  buildCorridor(grp('Corridor', env));
  buildExitHall(grp('ExitHall', env));
  const shops = grp('Shops', env);
  SHOPS.forEach((def, i) => {
    const left = i % 2 === 0, row = Math.floor(i / 2);
    const z = LobbyEnd + ShopWidth * (row + 0.5), x = (CorridorHalf + ShopDepth / 2) * (left ? -1 : 1);
    buildShop(def, shops, [x, 0, z], left ? 90 : -90, i + 1);
  });

  // Sun (same direction as Unity rotation (62,-35,0))
  const dir = new THREE.Vector3(0, 0, 1).applyEuler(new THREE.Euler(62 * D2R, -35 * D2R, 0, 'YXZ'));
  const sun = new THREE.DirectionalLight(0xffffff, 2.2);
  sun.color.setRGB(1, 0.96, 0.9, THREE.SRGBColorSpace);
  const tgt = new THREE.Object3D(); tgt.position.set(0, 0, 28); U.add(tgt);
  sun.target = tgt;
  sun.position.copy(tgt.position).addScaledVector(dir, -70);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  Object.assign(sun.shadow.camera, { left: -55, right: 55, top: 55, bottom: -55, near: 1, far: 200 });
  sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03;
  U.add(sun);

  // merge static meshes by material + shadow flag to keep draw calls low
  U.updateMatrixWorld(true);
  const buckets = new Map();
  const toRemove = [];
  U.traverse(o => {
    if (!o.isMesh || !o.userData.static || o.material.isMeshBasicMaterial) return;
    const key = o.material.uuid + '|' + o.castShadow;
    if (!buckets.has(key)) buckets.set(key, { mat: o.material, cast: o.castShadow, geos: [] });
    const g = o.geometry.clone().applyMatrix4(o.matrixWorld);
    if (o.matrixWorld.determinant() < 0) { /* no negative scales used */ }
    buckets.get(key).geos.push(g.index ? g.toNonIndexed() : g);
    toRemove.push(o);
  });
  toRemove.forEach(o => o.parent.remove(o));
  for (const { mat, cast, geos } of buckets.values()) {
    const m = new THREE.Mesh(mergeGeometries(geos, false), mat);
    m.castShadow = cast; m.receiveShadow = true;
    U.add(m);
  }
  U.scale.z = -1; // Unity (left-handed) -> three.js (right-handed)
  U.updateMatrixWorld(true);
}
