import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, sep } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * `Response` belongs to this package, and the evidence is its call sites.
 *
 * The question — should the markdown renderer move to `@djangocfg/widget-media`
 * alongside the diagram and the document markdown? — was open long enough to
 * be worth settling in code rather than in a plan. It was settled by counting:
 * every consumer of `Response` imports two to four OTHER things from `chat`,
 * so there is no caller that wants markdown without the chat around it.
 *
 * `channel-row` is the one that looks like a counterexample and is not. A
 * channel post is a message: it pulls `ChatMessageFrame`, `MessageProse` and
 * `ChatMessage` beside the renderer.
 *
 * This asserts the PREMISE, not the conclusion. If a consumer ever appears
 * that imports `Response` and nothing else from this package, the reasoning
 * above has expired and the move deserves a second look — which is exactly
 * when a red test here is useful.
 */

const ROOT = join(import.meta.dirname, "..", "..", "..", "..", "..");
const SEARCHED = ["widgets", "packages", "apps"];
const SKIP = new Set(["node_modules", "dist", ".turbo", ".archive", "@sources", "@dev"]);

describe("Response's consumers want the chat, not just markdown", () => {
  const consumers = filesImporting("@djangocfg/widget-chat/content");

  /**
   * The control, currently PENDING.
   *
   * This widget has just been seeded and no app mounts it yet, so the walk
   * finds nothing and the premise cannot be tested. Skipped rather than
   * weakened: an assertion relaxed to `>= 0` would pass forever and stop being
   * a control at all.
   *
   * Unskip when the first host mounts the chat — see
   * `widgets/@dev/active/ui-tools-to-widgets/PLAN.md`, Phase 4.
   */
  it.skip("finds the consumers it is reasoning about", () => {
    expect(consumers.length).toBeGreaterThan(2);
  });

  it("has no consumer that imports ONLY the content subpath", () => {
    const markdownOnly = consumers.filter((path) => chatImportCount(path) < 2);

    expect(markdownOnly).toEqual([]);
  });
});

/**
 * Files that CONSUME the content subpath.
 *
 * Three kinds of file mention it without being a consumer, and all three are
 * excluded here rather than tolerated in the assertion: this package's own
 * barrel re-exports it, a test asserting the export surface imports it to check
 * that it resolves, and this file names it in prose. Counting them would report
 * three counterexamples that are really one bad question.
 */
function filesImporting(specifier: string): string[] {
  return SEARCHED.flatMap((dir) => sourceFiles(join(ROOT, dir)))
    .filter((path) => !path.includes(`${sep}widgets${sep}chat${sep}`))
    .filter((path) => !/\.test\.tsx?$/.test(path))
    .filter((path) => readFileSync(path, "utf8").includes(specifier));
}

/** How many distinct `@djangocfg/widget-chat` specifiers a file imports. */
function chatImportCount(path: string): number {
  const source = readFileSync(path, "utf8");
  const specifiers = source.matchAll(/from\s+["'](@djangocfg\/widget-chat[^"']*)["']/g);
  return new Set([...specifiers].map(([, spec]) => spec)).size;
}

function sourceFiles(dir: string, out: string[] = []): string[] {
  let entries: string[];
  try {
    entries = readdirSync(dir);
  } catch {
    return out;
  }
  for (const entry of entries) {
    if (SKIP.has(entry)) continue;
    const path = join(dir, entry);
    if (statSync(path).isDirectory()) {
      sourceFiles(path, out);
      continue;
    }
    if (/\.tsx?$/.test(entry)) out.push(path);
  }
  return out;
}
