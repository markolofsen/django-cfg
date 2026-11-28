import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ToolCatalogEntry } from "../../core";
import { ToolMenu } from "./menu";
import { ToolRows } from "./rows";

/**
 * The sheet's contract, asserted on the markup it emits. Static markup only:
 * the workspace has no jsdom, and every claim here is about what a row says.
 */

const entry = (id: string, extra: Partial<ToolCatalogEntry> = {}): ToolCatalogEntry => ({
  id,
  name: id,
  summary: `${id} summary`,
  category: "misc",
  ...extra,
});

const TRANSCRIBE = entry("transcribe_audio", {
  name: "Transcribe audio",
  summary: "Read back what was said",
  category: "stt",
  keywords: ["voice", "speech"],
});
const SEARCH = entry("web_search", { name: "Search the web", category: "web" });

const COPY = {
  label: "Tools",
  searchLabel: "Find a tool",
  emptyLabel: "No such tool",
  recentLabel: "Recent",
  forgetLabel: "Remove from recent",
};

const render = (node: Parameters<typeof renderToStaticMarkup>[0]) => renderToStaticMarkup(node);

describe("the sheet", () => {
  it("names every tool it was given", () => {
    const html = render(
      <ToolMenu entries={[TRANSCRIBE, SEARCH]} onPick={() => {}} {...COPY} />,
    );

    expect(html).toContain("Transcribe audio");
    expect(html).toContain("Search the web");
  });

  /** The summary is what tells two neighbouring tools apart. */
  it("carries each tool's summary, not only its name", () => {
    const html = render(<ToolMenu entries={[TRANSCRIBE]} onPick={() => {}} {...COPY} />);
    expect(html).toContain("Read back what was said");
  });

  it("groups under the registry's own category key", () => {
    const html = render(
      <ToolMenu
        entries={[TRANSCRIBE, SEARCH]}
        onPick={() => {}}
        categoryLabel={(category) => `<${category}>`}
        {...COPY}
      />,
    );

    // The label function receives the RAW key; a local re-grouping would pass
    // something the host's map has never seen.
    expect(html).toContain("&lt;stt&gt;");
    expect(html).toContain("&lt;web&gt;");
  });

  it("says so when nothing matches, rather than rendering an empty box", () => {
    const html = render(<ToolMenu entries={[]} onPick={() => {}} {...COPY} />);

    expect(html).toContain("No such tool");
    expect(html).not.toContain('role="menu"');
  });

  /** Below the threshold the filter has nothing to narrow. */
  it("omits the filter for a short catalogue", () => {
    const html = render(<ToolMenu entries={[TRANSCRIBE, SEARCH]} onPick={() => {}} {...COPY} />);
    expect(html).not.toContain('type="search"');
  });

  it("offers the filter once the catalogue is long", () => {
    const many = Array.from({ length: 8 }, (_, index) => entry(`tool_${index}`));
    const html = render(<ToolMenu entries={many} onPick={() => {}} {...COPY} />);

    expect(html).toContain('type="search"');
    expect(html).toContain('aria-label="Find a tool"');
  });
});

describe("the rows", () => {
  /**
   * A listbox may not contain the `<button>` each row is.
   *
   * The role is asserted with its closing quote: `menuitemcheckbox` CONTAINS
   * `menuitem`, so a bare substring check passes on either and distinguishes
   * nothing.
   */
  it("is a labelled menu of checkable items", () => {
    const html = render(
      <ToolRows
        groups={[{ category: "web", entries: [SEARCH] }]}
        onPick={() => {}}
        label="Tools"
      />,
    );

    expect(html).toContain('role="menu"');
    expect(html).toContain('aria-label="Tools"');
    expect(html).toContain('role="menuitemcheckbox"');
    // A catalogue row is CHECKABLE, never a plain item: `menuitemcheckbox`
    // contains `menuitem`, so the closing quote is what tells them apart. The
    // forget control IS a plain `menuitem`, which is why this group carries
    // none — the assertion would stop distinguishing anything.
    expect(html).not.toContain('role="menuitem"');
    expect(html).not.toContain('role="listbox"');
  });

  it("draws the glyph the entry's icon key maps to", () => {
    const html = render(
      <ToolRows
        groups={[{ category: "stt", entries: [entry("t", { icon: "mic" })] }]}
        onPick={() => {}}
        label="Tools"
        icon={(key) => <i data-glyph={key} />}
      />,
    );

    expect(html).toContain('data-glyph="mic"');
  });

  /** An unmapped key ships a row without a picture, never a broken one. */
  it("survives an icon key the host does not map", () => {
    const html = render(
      <ToolRows
        groups={[{ category: "stt", entries: [entry("t", { icon: "unknown" })] }]}
        onPick={() => {}}
        label="Tools"
        icon={() => null}
      />,
    );

    expect(html).toContain('role="menuitemcheckbox"');
  });

  /** `aria-selected` belongs to a listbox; a checkable menu item says `checked`. */
  it("marks nothing selected", () => {
    const html = render(
      <ToolRows
        groups={[{ category: "web", entries: [SEARCH] }]}
        onPick={() => {}}
        label="Tools"
      />,
    );

    expect(html).not.toContain("aria-selected");
  });

  /**
   * A staged tool READS as staged.
   *
   * MUTANT: ignore `picked` and always render false → this dies. Without it the
   * only feedback is the chip row, which the open menu covers.
   */
  it("checks the rows already staged, and only those", () => {
    const other = entry("other");
    const html = render(
      <ToolRows
        groups={[{ category: "web", entries: [SEARCH, other] }]}
        onPick={() => {}}
        picked={new Set([SEARCH.id])}
        label="Tools"
      />,
    );

    expect(html).toContain('aria-checked="true"');
    // The control: without an unchecked row beside it, "true" appearing
    // somewhere would pass on a menu that checks everything.
    expect(html).toContain('aria-checked="false"');
  });

  /** Nothing staged ⇒ nothing checked, however many rows there are. */
  it("checks nothing when the draft has picked nothing", () => {
    const html = render(
      <ToolRows
        groups={[{ category: "web", entries: [SEARCH] }]}
        onPick={() => {}}
        label="Tools"
      />,
    );

    expect(html).not.toContain('aria-checked="true"');
  });
});

describe("recents", () => {
  const RECENT = { category: " recent", entries: [SEARCH] };

  it("labels the recents group with the host's copy, never the marker key", () => {
    const html = render(
      <ToolRows
        groups={[RECENT]}
        onPick={() => {}}
        label="Tools"
        categoryLabel={() => "Recent"}
        recentCategory=" recent"
        onForget={() => {}}
        forgetLabel="Remove from recent"
      />,
    );

    expect(html).toContain("Recent");
    expect(html).not.toContain(" recent<");
  });

  it("offers a forget control on a recent row", () => {
    const html = render(
      <ToolRows
        groups={[RECENT]}
        onPick={() => {}}
        label="Tools"
        recentCategory=" recent"
        onForget={() => {}}
        forgetLabel="Remove from recent"
      />,
    );

    expect(html).toContain('aria-label="Remove from recent"');
  });

  /** The control belongs to the history, not to the catalogue. */
  it("offers none on an ordinary category row", () => {
    const html = render(
      <ToolRows
        groups={[{ category: "web", entries: [SEARCH] }]}
        onPick={() => {}}
        label="Tools"
        recentCategory=" recent"
        onForget={() => {}}
        forgetLabel="Remove from recent"
      />,
    );

    expect(html).not.toContain('aria-label="Remove from recent"');
  });

  /**
   * One column, one meaning. A check on a recent row would sit under the forget
   * control, and the two would compete for the same corner.
   */
  it("shows no check on a recent row, even when that tool is staged", () => {
    const html = render(
      <ToolRows
        groups={[RECENT]}
        onPick={() => {}}
        picked={new Set([SEARCH.id])}
        label="Tools"
        recentCategory=" recent"
        onForget={() => {}}
        forgetLabel="Remove from recent"
      />,
    );

    // Still announced as staged — only the glyph yields the column.
    expect(html).toContain('aria-checked="true"');
    expect(html).toContain('aria-label="Remove from recent"');
  });

  it("marks the keyboard's row, and only that one", () => {
    const html = render(
      <ToolRows
        groups={[{ category: "web", entries: [SEARCH, TRANSCRIBE] }]}
        onPick={() => {}}
        label="Tools"
        activeIndex={1}
      />,
    );

    expect(html.match(/data-active/g)).toHaveLength(1);
  });
});
