// Checks every registered ThreeUI file against the SHA-256 in threeui-manifest.json.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

const root = new URL("../", import.meta.url);
const manifest = JSON.parse(readFileSync(new URL("threeui-manifest.json", root), "utf8"));

let failures = 0;
for (const { path, sha256 } of manifest.files) {
  let actual;
  try {
    actual = createHash("sha256").update(readFileSync(new URL(path, root))).digest("hex");
  } catch {
    actual = "missing";
  }
  const ok = actual === sha256;
  if (!ok) failures++;
  console.log(`${ok ? "ok  " : "FAIL"} ${path}`);
}
console.log(`${manifest.files.length - failures}/${manifest.files.length} match`);
process.exit(failures ? 1 : 0);
