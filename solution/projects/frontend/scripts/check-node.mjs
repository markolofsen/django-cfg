import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

/**
 * The toolchain gate for build and publish: the Node that runs `make` must be new
 * enough, must run natively, and must match the native modules `pnpm install` put
 * in node_modules (rollup, esbuild, turbo). A Node started under Rosetta on Apple
 * Silicon reports `x64`, looks for `@rollup/rollup-darwin-x64` and fails with a
 * message about an npm bug, long after the real cause (the wrong Node) is out of sight.
 */

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const problems = [];

const minimum = JSON.parse(readFileSync(join(root, "package.json"), "utf8")).engines?.node?.replace(/^[>=\s]+/, "");
const [needMajor = 0, needMinor = 0] = (minimum ?? "").split(".").map(Number);
const [major, minor] = process.versions.node.split(".").map(Number);
if (major < needMajor || (major === needMajor && minor < needMinor)) {
  problems.push(`Node ${process.versions.node} is older than the ${minimum} this repo requires.`);
}

if (process.platform === "darwin" && process.arch === "x64") {
  let nativeArm = false;
  try {
    nativeArm = execFileSync("sysctl", ["-n", "hw.optional.arm64"], { encoding: "utf8" }).trim() === "1";
  } catch {}
  if (nativeArm) problems.push(`This Node (${process.execPath}) is x64 and runs under Rosetta on an Apple Silicon Mac, so it cannot load the arm64 native modules installed here.`);
}

const pnpmDir = join(root, "node_modules", ".pnpm");
const suffix = `${process.platform}-${process.arch}`;
if (existsSync(pnpmDir) && !readdirSync(pnpmDir).some((name) => name.startsWith(`@rollup+rollup-${suffix}`))) {
  problems.push(`node_modules has no @rollup/rollup-${suffix}: it was installed by a Node of another architecture. Run \`pnpm install\` with this Node.`);
}

if (problems.length) {
  console.error(`✗ Node check failed (node ${process.version}, ${suffix}):`);
  for (const problem of problems) console.error(`  - ${problem}`);
  console.error("  Fix: use an arm64 Node >= " + (minimum ?? "20") + " (nvm use; .nvmrc in this folder), then run the command again.");
  process.exit(1);
}
console.log(`[node] ${process.version} ${suffix}, native modules match`);
