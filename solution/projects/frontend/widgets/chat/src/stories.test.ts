import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, resolve, sep } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * One typing shape and one taxonomy for every story file in `widgets/`.
 *
 * WHY THIS LIVES IN chat/
 * There is no package at `widgets/` — the sixteen widgets are sixteen workspace
 * members, each with its own `vitest.config.ts`, and turbo runs `test` per
 * member. A cross-widget rule therefore has no natural home: inventing a
 * seventeenth package just to hold one file would add a manifest, a config and
 * a turbo node for 60 lines of `readdirSync`. So this walks UP to `widgets/`
 * from a widget that already runs. chat is that widget — it has the densest
 * test suite here and its gates are already the reference for the others.
 *
 * The cost is honest and worth naming: editing a story in `visual/` is only
 * caught by running chat's tests. Turbo runs every widget's `test` on any
 * widgets change, so CI still catches it; a developer running
 * `pnpm --filter @djangocfg/widget-visual test` alone does not. If `widgets/`
 * ever grows a real root package, move this file there unchanged.
 *
 * WHAT IT HOLDS
 *
 * 1. The typing shape. `satisfies Meta<typeof X>` + `StoryObj<typeof meta>` is
 *    not a style preference — it is the only combination that actually CHECKS a
 *    story's args. The alternative, annotating `const meta: Meta<typeof X>`,
 *    widens the object to the declared type, so `StoryObj` derived from the
 *    component can no longer see which args meta already supplies and stops
 *    relating the two at all.
 *
 *    Measured on the one chat file that had drifted to the annotated form:
 *    switching it to this pair surfaced SIX stories passing a required prop set
 *    that was missing `children`. None of them was a rendering bug — every story
 *    supplies its body through `render` — but the type had been proving nothing
 *    about any of them, which is what a checked story file is for.
 *
 * 2. The taxonomy. A story's `title` is its only address in the sidebar, and
 *    nothing else in the toolchain relates that string to the directory the file
 *    sits in. Asserting `Widgets/<Widget>/…` is what makes the tree a property
 *    of the repository rather than of whoever typed the string last.
 */
const WIDGETS = resolve(import.meta.dirname, "../..");

/** Directories under `widgets/` that hold no shippable source. */
const NOT_A_WIDGET = new Set(["@dev", "node_modules"]);

function storyFiles(dir: string, out: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    if (NOT_A_WIDGET.has(entry) || entry.startsWith(".")) continue;
    const path = join(dir, entry);
    if (statSync(path).isDirectory()) {
      storyFiles(path, out);
      continue;
    }
    if (entry.endsWith(".stories.tsx")) out.push(path);
  }
  return out;
}

/**
 * The `title` declared by the meta object, or null.
 *
 * Deliberately NOT a `/title:\s*['"]/` scan of the file. `title` is also an
 * ordinary data key in this repo's fixtures — `player/src/surfaces/*` describe
 * tracks (`title: "Sanya.mp3"`), `data/…/tree-JsonTree` builds nodes
 * (`title: 'First'`), and `forms/…/json-form` carries thirty of them in its
 * JSON Schemas. In five of those files a data `title` appears BEFORE `const
 * meta`, so a first-match scan reads the fixture and reports the wrong address.
 *
 * So: slice the meta object, then take only the key at its top level (exactly
 * two spaces of indent). Two files — `chat-dev/…/env-table` and
 * `forms/…/cron-preview` — carry a nested `title` inside meta itself, which the
 * indent anchor is what excludes.
 */
function metaTitle(source: string): string | null {
  const start = source.search(/^const meta(?::[^=]*)? = \{$/m);
  if (start < 0) return null;
  // Story files are Prettier-formatted, so the meta object's closing brace is
  // the first one in column 0 after it.
  const end = source.indexOf("\n}", start);
  const block = source.slice(start, end < 0 ? source.length : end);
  return block.match(/^ {2}title:\s*(['"`])(.+?)\1,?$/m)?.[2] ?? null;
}

/**
 * `charts` → `Charts`, `chat-dev` → `Chat Dev`. The widget directory name is
 * the taxonomy segment; a hyphen becomes a space so a sidebar reads as words.
 */
function segment(widget: string): string {
  // `replace` rather than `widget[0]`: a directory name is never empty, but
  // indexing says otherwise under `noUncheckedIndexedAccess` and the honest fix
  // is an expression that cannot be empty rather than an assertion that it is not.
  return widget
    .split("-")
    .map((word) => word.replace(/^./, (first) => first.toUpperCase()))
    .join(" ");
}

const FILES = storyFiles(WIDGETS).map((path) => {
  const name = relative(WIDGETS, path);
  return { name, widget: name.split(sep)[0]!, source: readFileSync(path, "utf8") };
});

const sourceOf = (name: string) => FILES.find((f) => f.name === name)!;
const NAMES = FILES.map((f) => f.name);

describe("story files", () => {
  it("has some to check", () => {
    // The control. A broken walker returns [], and every `it.each` below would
    // then vacuously pass while measuring nothing. The floor is well under the
    // real count (96 across 16 widgets) so deleting stories is allowed, but
    // losing the walk is not.
    expect(FILES.length).toBeGreaterThan(80);
    // The same walker, one level up: a bad `resolve` that stopped inside chat
    // would still clear the count above once chat grew, and silently check one
    // widget again.
    expect(new Set(FILES.map((f) => f.widget)).size).toBeGreaterThan(10);
  });

  it.each(NAMES)("%s pins its meta with satisfies", (name) => {
    const { source } = sourceOf(name);
    // `typeof X` is the load-bearing part; the type argument may itself be
    // generic. `satisfies Meta<typeof DataGrid<Host>>` is MORE precise than the
    // bare form — it pins the row type the stories actually use — and a `\w+`
    // pattern rejected exactly that, penalising the better-typed file.
    expect(source).toMatch(/^} satisfies Meta<typeof [\w.]+(<.+>)?>;$/m);
    // The annotated form is the one that silently stops checking args.
    expect(source).not.toMatch(/const meta: Meta</);
  });

  it.each(NAMES)("%s derives Story from meta", (name) => {
    expect(sourceOf(name).source).toContain("type Story = StoryObj<typeof meta>;");
  });

  it.each(NAMES)("%s types its exports through Story", (name) => {
    // Declaring `Story` correctly proves nothing if an export then annotates
    // itself past it. One file did: a `Playground` typed `StoryObj<PlaygroundArgs>`
    // over a hand-written copy of the component's props, which had already
    // drifted — `defaultExpandedDepth` was `number` where the component says
    // `number | true`. The args were checked against the copy, so the drift was
    // invisible. `Story` is the only annotation that stays tied to `meta`.
    const offenders = [...sourceOf(name).source.matchAll(/^export const \w+: (StoryObj<[^;]+>)/gm)];
    expect(offenders.map((m) => m[1])).toEqual([]);
  });

  it.each(NAMES)("%s declares a title in meta", (name) => {
    // Untitled stories still render — Storybook derives an address from the
    // file path — which is exactly why this needs asserting rather than noticing.
    expect(metaTitle(sourceOf(name).source)).toBeTruthy();
  });

  it.each(NAMES)("%s is filed under its own widget", (name) => {
    const { widget, source } = sourceOf(name);
    expect(metaTitle(source)).toMatch(
      new RegExp(`^Widgets/${segment(widget)}/.+`),
    );
  });
});
