import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * Every declared subpath resolves and exports something.
 *
 * The asymmetry this exists for: vitest resolves through Vite aliases and `tsc`
 * through the package `exports` map, so a subpath declared but broken leaves
 * BOTH gates green — the tests never touch it and the typechecker never sees a
 * consumer. A host importing it is the first to find out.
 */
const SUBPATHS = [
  ["root", () => import("./index")],
  ["core", () => import("./chat/core/index")],
  ["store", () => import("./chat/store/index")],
  ["primitives", () => import("./chat/primitives/index")],
  ["media", () => import("./chat/media/index")],
  ["content", () => import("./chat/content/index")],
  ["composer", () => import("./chat/composer/index")],
  ["ui", () => import("./chat/ui/index")],
  ["utils", () => import("./chat/utils/index")],
  ["i18n", () => import("./i18n/index")],
  ["testing", () => import("./chat/testing/index")],
  ["page-snapshot", () => import("./page-tooling/page-snapshot/index")],
  ["browser-bridge", () => import("./page-tooling/browser-bridge/index")],
  ["copilot", () => import("./page-tooling/copilot/index")],
  ["wire", () => import("./assistant/wire/index")],
  ["session", () => import("./assistant/session/index")],
  ["shell", () => import("./assistant/shell/index")],
  ["assistant", () => import("./assistant/index")],
] as const;

describe("declared subpaths", () => {
  it("lists exactly the subpaths package.json exports", () => {
    // The list above is hand-written, so it can drift from the map hosts
    // actually resolve. `./styles` is CSS, not a module, and is not importable.
    const pkg = JSON.parse(readFileSync(join(import.meta.dirname, "..", "package.json"), "utf8")) as {
      exports: Record<string, string>;
    };
    const declared = Object.keys(pkg.exports)
      .filter((key) => key !== "./styles")
      .map((key) => (key === "." ? "root" : key.slice(2)))
      .sort();
    expect(SUBPATHS.map(([name]) => name).sort()).toEqual(declared);
  });

  it("points every export at a file that exists", () => {
    const root = join(import.meta.dirname, "..");
    const pkg = JSON.parse(readFileSync(join(root, "package.json"), "utf8")) as { exports: Record<string, string> };
    const missing = Object.entries(pkg.exports).filter(([, target]) => {
      try {
        readFileSync(join(root, target));
        return false;
      } catch {
        return true;
      }
    });
    expect(missing).toEqual([]);
  });

  for (const [name, load] of SUBPATHS) {
    // A generous timeout, not a slow test: the root pulls streamdown, Prism and
    // katex, and transforming those under a full parallel suite exceeds the 5s
    // default while the same import takes ~80ms run alone.
    it(`${name} resolves`, async () => {
      await expect(load()).resolves.toBeDefined();
    }, 30_000);
  }

  it("the transcript is reachable from primitives", async () => {
    // Stage 6's whole output. A layer that exists but is not exported is a
    // layer no host can use.
    const mod = await import("./chat/primitives/index");
    expect(mod.Transcript).toBeTypeOf("function");
    expect(mod.useStickToBottom).toBeTypeOf("function");
    expect(mod.useRovingFocus).toBeTypeOf("function");
  });

  it("the response renderer is reachable from content", async () => {
    const mod = await import("./chat/content/index");
    expect(mod.Response).toBeDefined();
  });
});
