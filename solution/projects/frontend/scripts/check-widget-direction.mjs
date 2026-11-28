import { readdirSync, readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

/**
 * `widgets/` holds self-contained product blocks; `packages/` holds the
 * plumbing beneath them. A widget may depend on a package. A package may not
 * depend on a widget — that edge would make the block unliftable, which is the
 * only property the directory split exists to protect.
 *
 * The check reads manifests, not imports: a dependency a package does not
 * declare cannot resolve, so the manifest is the enforceable boundary.
 *
 * Ported from cmdop-web, which enforces the same layering.
 */

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const WIDGETS_DIR = "widgets";
const PACKAGES_DIR = "packages";

/** Named exemptions: package name → why it is a consumer rather than plumbing. */
/**
 * Named, dated exemptions. Each is a package that legitimately points at a
 * widget WHILE its own contents are mid-move, and each must name the track
 * that removes it — an exemption with no removal condition is the rule being
 * quietly deleted.
 */
const ALLOWED = new Map([
  // Empty, and that is the point: `ui-tools` was the only entry, and it left
  // with the package in Phase 5. A new entry must name the track that removes
  // it — an exemption with no removal condition is the rule being quietly
  // deleted.
]);

function listPackages(group) {
  const root = join(repoRoot, group);
  if (!existsSync(root)) return [];
  return readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && entry.name !== "node_modules")
    // `@archive` / `@dev` / `@sources` are kept on disk for reference and are
    // excluded from the workspace; a manifest in there is not a live edge.
    .filter((entry) => !entry.name.startsWith("@"))
    .map((entry) => join(root, entry.name, "package.json"))
    .filter((path) => existsSync(path))
    .map((path) => ({ path, manifest: JSON.parse(readFileSync(path, "utf8")) }));
}

const widgets = listPackages(WIDGETS_DIR);
const packages = listPackages(PACKAGES_DIR);
const widgetNames = new Set(widgets.map(({ manifest }) => manifest.name));

const violations = [];
const usedExemptions = new Set();

for (const { path, manifest } of packages) {
  const declared = {
    ...manifest.dependencies,
    ...manifest.devDependencies,
    ...manifest.peerDependencies,
  };
  const crossings = Object.keys(declared).filter((name) => widgetNames.has(name));
  if (crossings.length === 0) continue;

  if (ALLOWED.has(manifest.name)) {
    usedExemptions.add(manifest.name);
    continue;
  }
  violations.push({ file: path.slice(repoRoot.length + 1), name: manifest.name, crossings });
}

// A gate that resolved nothing passes forever. Assert the inputs exist before
// trusting a clean verdict.
if (widgets.length === 0 || packages.length === 0) {
  console.error(
    `[widget-direction] resolved ${widgets.length} widget(s) and ${packages.length} package(s) — ` +
      "one group is empty, so a clean result would mean nothing. Check the directory names.",
  );
  process.exitCode = 1;
} else if (violations.length > 0) {
  console.error(
    [
      "A package depends on a widget. The dependency points the wrong way:",
      ...violations.map(({ file, name, crossings }) => `  ${file}: ${name} → ${crossings.join(", ")}`),
      "",
      "Move the shared code down into a package, or move the consumer up into",
      "widgets/. A named exemption goes in ALLOWED in",
      "scripts/check-widget-direction.mjs with the reason it is a consumer",
      "rather than plumbing.",
    ].join("\n"),
  );
  process.exitCode = 1;
} else {
  const stale = [...ALLOWED.keys()].filter((name) => !usedExemptions.has(name));
  if (stale.length > 0) {
    console.error(
      [
        "Stale exemption — the package no longer depends on any widget:",
        ...stale.map((name) => `  ${name}`),
        "",
        "Remove it; an exemption must describe an edge that exists.",
      ].join("\n"),
    );
    process.exitCode = 1;
  } else {
    console.log(
      `[widget-direction] clean; ${packages.length} package(s) checked against ` +
        `${widgets.length} widget(s), ${usedExemptions.size} named exemption(s)`,
    );
  }
}
