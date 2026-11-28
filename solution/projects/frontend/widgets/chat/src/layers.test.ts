import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * The package's import rights, enforced.
 *
 * The layers are declared in each barrel's header comment, and a comment
 * forbids nothing. This is what makes the boundary real: a folder earns its
 * place by answering "what may this import?", so that question has to be
 * answerable automatically, not by a reviewer's memory at the end of a long day.
 *
 * Direction:
 *   ui → composer → primitives → store → core
 *   ui, composer, primitives → media ; media, content → core
 *   ui → blocks → primitives, store, core ; store → sounds (a leaf)
 *   utils imports nothing local at all.
 *   copilot → page-snapshot, browser-bridge, core ; page-snapshot → browser-bridge ; browser-bridge imports nothing local.
 *   session → wire, store, core, utils, i18n ; wire → core, utils.
 *   shell → ui and everything below it, never session or wire.
 *   assistant → shell, session, wire and everything below: the one layer allowed to join them.
 */

const SRC = import.meta.dirname;

/** What each layer may import. `core` and `utils` are the two sinks. */
const ALLOWED: Record<string, readonly string[]> = {
  core: ["utils"],
  store: ["sounds", "core", "utils"],
  // Sound assets and the player: a leaf, imports nothing local.
  sounds: [],
  primitives: ["store", "core", "utils", "media", "content", "i18n"],
  // Interactive block renderers (ask, approval, changes). They answer through
  // the store, so they sit above `store` and `primitives` and below `ui`.
  blocks: ["primitives", "store", "core", "utils", "i18n"],
  media: ["core", "utils", "content", "i18n"],
  content: ["core", "utils", "i18n"],
  composer: ["primitives", "store", "core", "utils", "content", "i18n"],
  ui: ["composer", "blocks", "primitives", "media", "content", "store", "core", "utils", "i18n"],
  // A util that needs a chat concept is not a util — it belongs in core. That
  // is the whole membership test, so `utils` reaching anything local is the
  // one violation that cannot be argued down to a style preference.
  utils: [],
  // Copy is data. A dictionary that imports a chat concept has started
  // deciding something, and the point of typing the schema is that it decides
  // nothing — it is the words, and the layer that renders them picks which.
  i18n: [],
  testing: ["core", "store", "utils"],
  // Page tooling. `page-snapshot` captures and `browser-bridge` acts. The
  // bridge is a sink and never imports the capture engine (it depends on the
  // structural `RefResolver`), so it can be used and tested alone; the capture
  // provider installs the bridge's resolver, so the edge runs one way only.
  "page-snapshot": ["browser-bridge"],
  "browser-bridge": [],
  // The one place the two meet the chat: wraps a `ChatAdapter` (core types)
  // and gates what may act on the page. It must not reach the chat's UI layers.
  copilot: ["page-snapshot", "browser-bridge", "primitives", "core", "store", "utils"],
  // The assistant's wire and session. `wire` is the frames and the transport
  // and knows only the chat's contracts; `session` is one conversation over
  // it and draws nothing, so it never reaches `ui`, `composer` or `primitives`.
  wire: ["core", "utils"],
  session: ["wire", "store", "core", "utils", "i18n"],
  // The assistant's shell: frame, dock, fab, host, chat body, composer
  // behaviour. It sits above `ui` and is session-free on purpose, so a host
  // with its own transport (a call polls its lines) never pulls `wire` or
  // `session` into its graph.
  shell: ["ui", "composer", "blocks", "primitives", "media", "content", "store", "core", "utils", "i18n"],
  // The assistant: the shell wired to a session over the wire, plus the
  // history UI and the worked examples. It is the only layer above `shell`
  // and the only one that may import `session` and `shell` together.
  assistant: ["shell", "session", "wire", "ui", "composer", "blocks", "primitives", "media", "content", "store", "core", "utils", "i18n"],
};

/**
 * Files that never reach a consumer's bundle: tests, stories, and the workbench
 * the stories share.
 *
 * The rule this table enforces is about what SHIPS. `testing/` holds test
 * doubles and is deliberately unreachable from the package root, so a shipped
 * file importing it would drag a mock adapter into a production bundle. A story
 * cannot: nothing exports it, no entry point reaches it, and Storybook loads it
 * by its own glob. Excluding these is therefore the same decision as excluding
 * `*.test.tsx`, not a loophole.
 *
 * The workbench is excluded by DIRECTORY, not by filename. A filename pattern
 * has to name every harness file, and the one this replaced (`^stories-harness`)
 * was silently outlived by a split: the file that moved out of it kept none of
 * the name and so kept none of the exemption. A `stories/` segment cannot be
 * escaped that way, because the next split lands in the same folder.
 */
const NOT_SHIPPED = /\.test\.tsx?$|\.stories\.tsx$/;

/** A path inside a workbench folder, at any depth. */
const isWorkbench = (path: string): boolean => relative(SRC, path).split("/").includes("stories");

function sourceFiles(dir: string, out: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry);
    if (statSync(path).isDirectory()) {
      sourceFiles(path, out);
      continue;
    }
    if (/\.tsx?$/.test(entry) && !NOT_SHIPPED.test(entry) && !isWorkbench(path)) out.push(path);
  }
  return out;
}

/**
 * The layer a path belongs to, derived from the PATH, not from a folder-name
 * table: the first segment that names a layer. A new top-level folder is
 * therefore either a layer in `ALLOWED` or a failure of "knows every file"
 * below, never silently unchecked.
 *
 * Families wrap layers (`chat/<layer>`, `page-tooling/<layer>`) and
 * `assistant/{wire,session,shell}` are layers of their own; anything else under
 * `assistant/` (history, examples) is the `assistant` layer. Null is a file
 * sitting directly in `src/` (the package barrel) or in no layer at all.
 */
const FAMILIES = new Set(["chat", "page-tooling"]);

function layerOf(path: string): string | null {
  const [top, second] = relative(SRC, path).split("/");
  if (!top) return null;
  if (FAMILIES.has(top)) return second && second in ALLOWED ? second : null;
  if (top === "assistant") return second && ["wire", "session", "shell"].includes(second) ? second : "assistant";
  return top in ALLOWED ? top : null;
}

/**
 * Which layer an import statement reaches, or null when it stays inside the
 * importer's own layer or leaves the package.
 *
 * Only two forms can cross a boundary: a package subpath
 * (`@djangocfg/widget-chat/store`) and a relative path that climbs out of the current
 * folder (`../store/x`). A bare `./x` or a bare dependency never can.
 */
function crossedLayer(spec: string, from: string): string | null {
  const subpath = spec.match(/^@djangocfg\/widget-chat\/([\w-]+)/);
  if (subpath?.[1]) return subpath[1] in ALLOWED ? subpath[1] : null;
  if (!spec.startsWith(".")) return null;

  const resolved = relative(SRC, join(from, "..", spec));
  if (resolved.startsWith("..")) return null; // outside src/ — not our concern
  return layerOf(join(SRC, resolved));
}

const IMPORT = /(?:^|\n)\s*(?:import|export)[\s\S]{0,400}?from\s+["']([^"']+)["']/g;

describe("layer import rights", () => {
  const files = sourceFiles(SRC);

  it("sees the source tree", () => {
    // The control. Every assertion below is a loop over `files`; if the walk
    // returns nothing they all pass while checking nothing. A zero here means
    // "I could not look", which is not the same answer as "no violations".
    expect(files.length).toBeGreaterThan(5);
  });

  it("knows the layer of every shipped file", () => {
    // A folder nobody declared would otherwise be silently unchecked: `layerOf`
    // returns null and the loop below skips it. Only the package barrel sits
    // outside a layer.
    const unknown = files.map((path) => relative(SRC, path)).filter((name) => name !== "index.ts" && !layerOf(join(SRC, name)));
    expect(unknown).toEqual([]);
  });

  it("never lets a layer import one it may not", () => {
    const violations: string[] = [];

    for (const path of files) {
      const layer = layerOf(path);
      if (!layer) continue;
      const source = readFileSync(path, "utf8");

      for (const [, spec] of source.matchAll(IMPORT)) {
        if (!spec) continue;
        const target = crossedLayer(spec, path);
        if (!target || target === layer) continue;
        if (ALLOWED[layer]?.includes(target)) continue;
        violations.push(`${relative(SRC, path)}: ${layer} → ${target} ("${spec}")`);
      }
    }

    expect(violations).toEqual([]);
  });

  /**
   * The invariant the exclusion above could otherwise hide.
   *
   * Stories may reach `testing/` because they never ship. That freedom is only
   * safe while nothing that DOES ship reaches it, and the loop above can no
   * longer answer that question for the excluded files — so it is asked here
   * directly, against the shipped set, naming the one folder that must stay
   * unreachable. Without this, moving a mock import from a story into the
   * component beside it would turn a red gate green.
   */
  it("keeps the shipped tree clear of test doubles", () => {
    const leaks = files
      .filter((path) => layerOf(path) !== "testing")
      .filter((path) => /from\s+["'][^"']*\btesting\b/.test(readFileSync(path, "utf8")))
      .map((path) => relative(SRC, path));

    expect(leaks).toEqual([]);
  });

  it("imports nothing from a host site", () => {
    // The package must move to the framework as it is: no app aliases and no
    // Next.js imports, anywhere in the shipped tree.
    const hostImport = /from ['"](?:@(?:core|routes|i18n|features)\b|next\/)/;
    const leaks = files.filter((path) => hostImport.test(readFileSync(path, "utf8"))).map((path) => relative(SRC, path));

    expect(leaks).toEqual([]);
  });

  it("keeps core free of React, which is what makes it testable without a renderer", () => {
    // MUTANT: import React anywhere under core/ → this dies. The rule is load
    // bearing rather than stylistic: core holds the reducers, and they are only
    // fast to test because no renderer has to exist to run them.
    const reactInCore = files
      .filter((path) => layerOf(path) === "core")
      .filter((path) => /from\s+["']react/.test(readFileSync(path, "utf8")))
      .map((path) => relative(SRC, path));

    expect(reactInCore).toEqual([]);
  });
});
