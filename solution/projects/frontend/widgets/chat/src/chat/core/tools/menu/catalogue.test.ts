import { describe, expect, it } from "vitest";

import {
  filterToolCatalogue,
  groupToolsByCategory,
  toolMatchesQuery,
  type ToolCatalogEntry,
} from "./catalogue";

const entry = (id: string, extra: Partial<ToolCatalogEntry> = {}): ToolCatalogEntry => ({
  id,
  name: id,
  summary: `${id} summary`,
  category: "misc",
  ...extra,
});

/** The tool this whole menu exists for, with the registry's own keywords. */
const TRANSCRIBE = entry("transcribe_audio", {
  name: "Транскрибация аудио",
  summary: "Расшифровать речь из файла",
  category: "stt",
  keywords: ["stt", "speech", "transcribe", "audio", "voice", "recording", "listen", "said"],
});
const SEARCH = entry("web_search", { name: "Веб-поиск", category: "web" });
const FETCH = entry("web_fetch", { name: "Открыть страницу", category: "web" });

const ALL = [TRANSCRIBE, SEARCH, FETCH];

describe("toolMatchesQuery", () => {
  it("keeps everything for an empty or blank query", () => {
    expect(toolMatchesQuery(SEARCH, "")).toBe(true);
    expect(toolMatchesQuery(SEARCH, "   ")).toBe(true);
  });

  /**
   * The measured reason keywords are on the entry at all. A user who has a
   * recording types what they have, and neither the id nor the display name
   * contains "voice".
   */
  it("matches a keyword the name does not contain", () => {
    expect(TRANSCRIBE.name.toLowerCase()).not.toContain("voice");
    expect(toolMatchesQuery(TRANSCRIBE, "voice")).toBe(true);
  });

  it("matches the id, which is what a transcript shows", () => {
    expect(toolMatchesQuery(TRANSCRIBE, "transcribe_au")).toBe(true);
  });

  it("matches the summary", () => {
    expect(toolMatchesQuery(TRANSCRIBE, "речь")).toBe(true);
  });

  it("is case-insensitive on both sides", () => {
    expect(toolMatchesQuery(SEARCH, "WEB_SEARCH")).toBe(true);
  });

  it("rejects a query nothing carries", () => {
    expect(toolMatchesQuery(SEARCH, "zzz")).toBe(false);
  });

  /** A tool with no keywords must not throw on the branch that reads them. */
  it("survives an entry with no keywords", () => {
    expect(toolMatchesQuery(SEARCH, "anything-at-all")).toBe(false);
  });
});

describe("groupToolsByCategory", () => {
  it("uses the catalogue's own category, in first-appearance order", () => {
    expect(groupToolsByCategory(ALL)).toEqual([
      { category: "stt", entries: [TRANSCRIBE] },
      { category: "web", entries: [SEARCH, FETCH] },
    ]);
  });

  /**
   * Order is the HOST's. Sorting here would be a second opinion about display
   * order, and the catalogue is generated with one already.
   */
  it("does not sort categories", () => {
    const groups = groupToolsByCategory([SEARCH, TRANSCRIBE]);
    expect(groups.map((group) => group.category)).toEqual(["web", "stt"]);
  });

  it("is empty for an empty catalogue", () => {
    expect(groupToolsByCategory([])).toEqual([]);
  });
});

describe("filterToolCatalogue", () => {
  it("drops a category whose every tool was filtered out", () => {
    expect(filterToolCatalogue(ALL, "voice")).toEqual([
      { category: "stt", entries: [TRANSCRIBE] },
    ]);
  });

  it("returns nothing when the query matches nothing", () => {
    expect(filterToolCatalogue(ALL, "zzz")).toEqual([]);
  });
});
