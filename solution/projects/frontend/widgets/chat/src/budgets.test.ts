import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * The budgets from `@rules/budgets.md`, enforced.
 *
 * A written rule with no check is a rule that lasts until the first hurry — and
 * the specific failure it guards against already happened here: the predecessor
 * reached 83 props one plausible addition at a time, and no single commit
 * looked wrong. A number that fails the build is the only version of this rule
 * that survives.
 *
 * These are LOCAL to this package: nothing else runs them, so they live beside
 * the code they constrain and run whenever the package's tests do.
 */

const SRC = import.meta.dirname;

const MAX_ROOT_PROPS = 7;
const MAX_TSX_LINES = 300;
const MAX_TS_LINES = 400;

/** The root component, once it exists. Until then the prop budget self-reports. */
const CHAT_TSX = join(SRC, "chat", "ui", "chat", "chat.tsx");

/**
 * A workbench file, which these budgets do not measure.
 *
 * The limits below are written for shipped components, and applying them to a
 * workbench does not restrain anything — it fragments it. `stories/field.tsx`
 * exists because the harness crossed 300 lines, so a story was split for a
 * reason no reader of a story cares about. The `.stories.tsx` suffix was
 * already excluded implicitly by nothing at all; naming the folder covers the
 * harness files too, which carry no suffix and read as ordinary source.
 */
const isWorkbench = (path: string): boolean => relative(SRC, path).split("/").includes("stories") || /\.stories\.tsx$/.test(path);

/**
 * Files allowed past their budget, each with the reason `@rules/budgets.md`
 * requires: "exceeding a budget is not absolutely forbidden, but it requires a
 * written reason". The rule also forbids the other cure — raising the limit —
 * so the escape has to be per-file and named.
 *
 * A stale entry FAILS. An exemption describing a file that now fits is a claim
 * nobody re-checked, and leaving it silent is how a limit quietly stops
 * applying to a file that grew back.
 */
// Empty on purpose. `core/capabilities.ts` was the one entry; removing the
// mention and slash contracts brought it back under the limit on its own, and
// the rule above says a file that fits loses its exemption rather than keeping
// a dormant one.
const OVER_BUDGET_BY_DESIGN: Readonly<Record<string, string>> = {};

function sourceFiles(dir: string, out: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry);
    if (statSync(path).isDirectory()) {
      sourceFiles(path, out);
      continue;
    }
    if (/\.tsx?$/.test(entry) && !/\.test\.tsx?$/.test(entry) && !isWorkbench(path)) {
      out.push(path);
    }
  }
  return out;
}

describe("file size budgets", () => {
  it("keeps every source file within its budget", () => {
    const over: string[] = [];
    const stale: string[] = [];
    for (const path of sourceFiles(SRC)) {
      // Every file ends with a newline, so a plain split counts a phantom empty
      // last line and reports one more than `wc -l`. A budget that measures
      // wrong fails the wrong files — and the fix people reach for then is
      // raising the limit.
      const lines = readFileSync(path, "utf8").replace(/\n$/, "").split("\n").length;
      const limit = path.endsWith(".tsx") ? MAX_TSX_LINES : MAX_TS_LINES;
      const name = path.slice(SRC.length + 1);
      if (lines > limit) {
        if (!(name in OVER_BUDGET_BY_DESIGN)) over.push(`${name}: ${lines} > ${limit}`);
        continue;
      }
      if (name in OVER_BUDGET_BY_DESIGN) stale.push(`${name}: ${lines} <= ${limit}`);
    }
    expect(over).toEqual([]);
    // An exemption that no longer describes anything is removed, not kept: it
    // would silently re-cover the file if it grew past the limit again.
    expect(stale, "remove the stale entry from OVER_BUDGET_BY_DESIGN").toEqual([]);
  });

  it("actually reads files, so an empty sweep cannot pass as compliance", () => {
    // The control for the assertion above. `expect([]).toEqual([])` is also
    // green when the walker returns nothing — a broken glob, a moved SRC, a
    // renamed extension. Then the budget reports success while measuring zero
    // files, which is the exact shape of a check whose red gets ignored.
    expect(sourceFiles(SRC).length).toBeGreaterThan(5);
  });
});

/**
 * Folder width: a folder holds at most this many direct entries, files and
 * folders together, tests and stories not counted. Past it a listing stops
 * being scannable and the next file has no obvious home (`@rules` code
 * organization, section 1). The census command is this function, so the
 * definition lives in one place and not in a reader's head.
 */
const MAX_FOLDER_ENTRIES = 12;

/** Data folders that are wide by nature: one file per locale, and a registry test says so. */
const WIDTH_EXEMPT_BY_DESIGN: Readonly<Record<string, string>> = {
  "i18n/locales": "one dictionary per locale (17)",
  "i18n/assistant/locales": "one dictionary per locale (17)",
};

const isTestOrStory = (name: string): boolean => /\.test\.tsx?$|\.stories\.tsx$/.test(name);

/** Direct source entries per folder: tests, stories and `stories/` workbench folders left out. */
function folderEntries(dir: string, out = new Map<string, string[]>()): Map<string, string[]> {
  const names: string[] = [];
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry);
    if (statSync(path).isDirectory()) {
      if (entry !== "stories") names.push(entry);
      folderEntries(path, out);
      continue;
    }
    if (!isTestOrStory(entry)) names.push(entry);
  }
  out.set(relative(SRC, dir) || ".", names);
  return out;
}

describe("folder width", () => {
  const folders = folderEntries(SRC);

  it("keeps every folder at or under twelve direct entries", () => {
    const wide = [...folders]
      .filter(([dir, names]) => names.length > MAX_FOLDER_ENTRIES && !(dir in WIDTH_EXEMPT_BY_DESIGN))
      .map(([dir, names]) => `${dir}: ${names.length} > ${MAX_FOLDER_ENTRIES} (${names.join(", ")})`);
    expect(wide).toEqual([]);
  });

  it("removes an exemption once its folder fits", () => {
    const stale = Object.keys(WIDTH_EXEMPT_BY_DESIGN).filter(
      (dir) => (folders.get(dir)?.length ?? 0) <= MAX_FOLDER_ENTRIES,
    );
    expect(stale, "delete the stale entry").toEqual([]);
  });

  it("has no __tests__ buckets: a test sits beside its subject", () => {
    const buckets = [...folders.keys()].filter((dir) => dir.split("/").includes("__tests__")).sort();
    expect(buckets).toEqual([]);
  });
});

/** Members of one interface, stopping at its closing brace. */
function membersOf(source: string, name: string): string[] {
  const start = source.indexOf(`interface ${name} `);
  if (start < 0) throw new Error(`interface ${name} not found — did it get renamed?`);
  const body = source.slice(start, source.indexOf("\n}", start));
  return [...body.matchAll(/^\s{2}readonly (\w+)\??:/gm)].map((m) => m[1] ?? "");
}

describe("the root component's prop budget", () => {
  it("keeps <Chat> at or under seven props", () => {
    // `<Chat>` is not written yet. Skipping silently is the failure mode this
    // whole file exists to prevent — a green budget on an absent subject reads
    // exactly like a compliant one. So the absence is asserted explicitly:
    // this branch dies the moment chat/ui/chat/chat.tsx appears, forcing the real count.
    if (!existsSync(CHAT_TSX)) {
      expect(existsSync(join(SRC, "chat", "ui", "index.ts")), "ui/ layer is missing").toBe(true);
      return;
    }

    // Counted from the source rather than from a type, because the point is to
    // fail on the commit that ADDS the eighth — before it is load-bearing.
    const source = readFileSync(CHAT_TSX, "utf8");
    // Exactly the two interfaces that ARE the prop list. Slicing a wider region
    // swept in `ChatSlots` and `ChatLabels` and reported fifteen — a check that
    // counts the wrong thing is worse than none, because its red is ignorable.
    const props = ["ChatBase", "ChatProps"].flatMap((name) => membersOf(source, name));

    expect(props.length, `<Chat> props: ${props.join(", ")}`).toBeLessThanOrEqual(
      MAX_ROOT_PROPS,
    );
  });
});
