import { describe, expect, it } from "vitest";

import { markdownToLine, markdownToText } from "./markdown-text";

/**
 * The roster's vocabulary. Supplied by the caller in the real thing, spelled
 * here so the expectations read as a person would see them.
 */
const LABELS = { code: "код", table: "таблица", image: "фото", formula: "формула" };

describe("markdown collapses to a line a person can read", () => {
  it("strips emphasis without editing the words", () => {
    expect(markdownToText("**жирный** и `код`")).toBe("жирный и код");
  });

  it("keeps punctuation a regex pipeline would eat", () => {
    // The three failures that put this on a parser rather than regexes. Each
    // one is text a person typed, silently rewritten.
    expect(markdownToText("fix file_name_here.txt")).toBe("fix file_name_here.txt");
    expect(markdownToText("5 * 3 = 15")).toBe("5 * 3 = 15");
  });

  it("separates blocks instead of fusing them", () => {
    // `toString` on a container concatenates bare: without the join this is
    // "донеnext" — two sentences welded into a non-word.
    expect(markdownToText("готово\n\nдальше")).toBe("готово дальше");
  });

  it("keeps a link's words and drops its target", () => {
    expect(markdownToText("смотри [документацию](https://example.com/docs) тут")).toBe(
      "смотри документацию тут",
    );
  });

  it("re-emits task state, which lives outside the text", () => {
    // A checkbox carries completion in `checked`, so dropping it claims an
    // unfinished item is done.
    expect(markdownToText("- [ ] не сделано\n- [x] сделано")).toBe(
      "◻ не сделано ✓ сделано",
    );
  });
});

describe("a block whose content does not belong in a label", () => {
  it("collapses a fenced block to a glyph and a word", () => {
    // MUTANT: return the code's text → this dies. Flattened, it reads as if the
    // agent said "const x = 1 const y = 2" in prose.
    expect(markdownToText("```js\nconst x = 1\nconst y = 2\n```", { blockLabels: LABELS }))
      .toBe("💻 код");
  });

  it("collapses a table, whose structure cannot survive one line", () => {
    const table = "| файл | статус |\n|---|---|\n| a.ts | ok |\n| b.ts | fail |";
    expect(markdownToText(table, { blockLabels: LABELS })).toBe("📊 таблица");
  });

  it("keeps the prose around a collapsed block", () => {
    // The block is opaque; the sentence that introduced it is not, and it is
    // usually the part that says what happened.
    expect(markdownToText("Вот код:\n\n```js\nx\n```\n\nготово", { blockLabels: LABELS }))
      .toBe("Вот код: 💻 код готово");
  });

  it("falls through to the text when the caller supplied no label", () => {
    // MUTANT: emit a bare glyph when the label is missing → this dies. A lone
    // "💻" tells the reader less than the content it replaced, and a caller
    // with no catalogue must not be worse off than before.
    expect(markdownToText("```js\nconst x = 1\n```")).toBe("const x = 1");
  });

  it("labels only the kinds it was given", () => {
    // A partial catalogue is the realistic case: a caller may name code and not
    // tables. The unnamed kind keeps its old behaviour rather than vanishing.
    const table = "| a | b |\n|---|---|\n| 1 | 2 |";
    expect(markdownToText(table, { blockLabels: { code: "код" } })).toBe("a b 1 2");
  });
});

describe("the first line, for a name rather than a preview", () => {
  it("takes the first block that carries words", () => {
    expect(markdownToLine("# Заголовок\n\nтекст под ним")).toBe("Заголовок");
  });

  it("skips a block with nothing renderable", () => {
    expect(markdownToLine("---\n\nнастоящий заголовок")).toBe("настоящий заголовок");
  });

  it("returns empty rather than punctuation, so a caller can fall back", () => {
    // MUTANT: return the collapsed source → this dies. A row titled "---" is
    // worse than a row titled by its own placeholder.
    expect(markdownToLine("---")).toBe("");
  });

  it("leaves task marks off for a name", () => {
    // The surface draws completion itself; a leading glyph would state the same
    // fact twice.
    expect(markdownToLine("- [x] сделано")).toBe("сделано");
  });
});

describe("degradation", () => {
  it("returns empty for empty input", () => {
    expect(markdownToText("")).toBe("");
    expect(markdownToLine("")).toBe("");
  });

  it("collapses whitespace and drops html tags", () => {
    expect(markdownToText("<b>жирный</b>   текст")).toBe("жирный текст");
  });
});
