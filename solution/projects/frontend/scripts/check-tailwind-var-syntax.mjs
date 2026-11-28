import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Tailwind 4 reads a custom property with PARENTHESES: `w-(--sidebar-width)`.
 * Square brackets mean an arbitrary VALUE, so the v3 spelling
 * `w-[--sidebar-width]` compiles to `width:--sidebar-width` — a bare token, not
 * a `var()` call. The declaration is invalid, the browser drops it, and the
 * element gets NO rule at all.
 *
 * Nothing else catches this: it compiles, emits CSS, and logs clean. It shipped
 * in @djangocfg/ui-core 2.1.562 and a consuming app's sidebar rail sized itself
 * to its content (374px against an intended 18rem), visible only in a browser.
 *
 * Only the bare `-[--x]` form is wrong. An arbitrary value that spells the
 * var() itself — `right-[calc(var(--sidebar-width)*-1)]` — is correct and must
 * pass, which is why the pattern requires `--name` to be the WHOLE bracket.
 */

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const ROOTS = ["packages", "widgets", "apps"];
const EXTENSIONS = new Set([".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css", ".md", ".mdx", ".html"]);
const SKIP_DIRS = new Set(["node_modules", "dist", "build", ".next", ".turbo", ".git", "storybook-static", "coverage"]);

const BAD = /[a-zA-Z][a-zA-Z0-9-]*-\[(--[a-z][a-zA-Z0-9-]*)\]/g;

/**
 * Prose that quotes the broken form to warn against it is not the defect.
 * Put this marker on the line; it is per-line, so it cannot silence a file.
 */
const ALLOW = "tailwind-var-syntax-ok";

function* walk(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".") || SKIP_DIRS.has(entry.name)) continue;
    const full = join(dir, entry.name);
    if (entry.isDirectory()) yield* walk(full);
    else if (EXTENSIONS.has(entry.name.slice(entry.name.lastIndexOf(".")))) yield full;
  }
}

const violations = [];
let scanned = 0;

for (const root of ROOTS) {
  const dir = join(repoRoot, root);
  if (!existsSync(dir) || !statSync(dir).isDirectory()) continue;
  for (const file of walk(dir)) {
    scanned++;
    const lines = readFileSync(file, "utf8").split("\n");
    lines.forEach((line, i) => {
      if (line.includes(ALLOW)) return;
      for (const m of line.matchAll(BAD)) {
        violations.push({ file: relative(repoRoot, file), line: i + 1, match: m[0], prop: m[1] });
      }
    });
  }
}

// A gate that resolved nothing passes forever. Assert the inputs exist before
// trusting a clean verdict.
if (scanned === 0) {
  console.error(`[tailwind-var-syntax] scanned 0 files under ${ROOTS.join(", ")} — a clean result would mean nothing.`);
  process.exitCode = 1;
} else if (violations.length > 0) {
  console.error(
    [
      "Tailwind 3 custom-property syntax. Square brackets emit an invalid",
      "declaration the browser drops, so the element gets no rule at all:",
      "",
      ...violations.map(
        ({ file, line, match, prop }) =>
          `  ${file}:${line}  ${match}  →  ${match.replace(`[${prop}]`, `(${prop})`)}`,
      ),
      "",
      "Tailwind 4 reads a variable with parentheses: `-(--x)`, not `-[--x]`.",
      "An arbitrary value that spells var() itself is fine and is not matched.",
    ].join("\n"),
  );
  process.exitCode = 1;
} else {
  console.log(`[tailwind-var-syntax] clean; ${scanned} file(s) checked`);
}
