import { describe, expect, it } from "vitest";

import { filterToolCatalogue, type ToolCatalogEntry } from "./catalogue";
import { queryLayoutForms } from "./layout";
import { scoreTool } from "./rank";
import { NO_ROW, nextRow, stepForKey } from "./nav";
import { forgetTool, recentTools, rememberTool, RECENT_LIMIT } from "./recent";

const GENERATE: ToolCatalogEntry = {
  id: "generate_image",
  name: "Generate image",
  summary: "Create an image from a description",
  category: "web",
};

// The row that outranked Generate image for "gen" in production: the hit is in
// its summary, inside the word "agent's".
const NAVIGATE: ToolCatalogEntry = {
  id: "browser_navigate",
  name: "Browser navigate",
  summary: "Go to a web address in the agent's browser",
  category: "browser",
};

const TRANSCRIBE: ToolCatalogEntry = {
  id: "transcribe_audio",
  name: "Transcribe audio",
  summary: "Turn speech into text",
  category: "stt",
  keywords: ["voice", "речь"],
};

const ALL = [NAVIGATE, GENERATE, TRANSCRIBE];

const flat = (query: string): string[] =>
  filterToolCatalogue(ALL, query).flatMap((group) => group.entries.map((entry) => entry.id));

describe("queryLayoutForms", () => {
  it("reads a Russian-layout query as what the keys would have typed", () => {
    expect(queryLayoutForms("пут")).toContain("gen");
  });

  it("reads it the other way too — the mistake runs in both directions", () => {
    expect(queryLayoutForms("dtn")).toContain("вет");
  });

  it("returns what was typed FIRST, so a caller can rank an exact hit higher", () => {
    expect(queryLayoutForms("gen")[0]).toBe("gen");
  });

  it("de-duplicates: an ASCII query that transliterates to itself stays one form", () => {
    expect(queryLayoutForms("123")).toEqual(["123"]);
  });

  it("has nothing to match on an empty query", () => {
    expect(queryLayoutForms("   ")).toEqual([]);
  });
});

describe("scoreTool", () => {
  it("ranks a name hit above a summary hit", () => {
    expect(scoreTool(GENERATE, "gen")).toBeGreaterThan(scoreTool(NAVIGATE, "gen"));
  });

  it("ranks a prefix above the same word mid-string", () => {
    expect(scoreTool(GENERATE, "gen")).toBeGreaterThan(scoreTool(GENERATE, "image"));
  });

  it("reaches a keyword the name does not contain", () => {
    expect(scoreTool(TRANSCRIBE, "voice")).toBeGreaterThan(0);
  });

  it("scores a wrong-layout query below the same query typed correctly", () => {
    expect(scoreTool(GENERATE, "пут")).toBeGreaterThan(0);
    expect(scoreTool(GENERATE, "пут")).toBeLessThan(scoreTool(GENERATE, "gen"));
  });

  it("scores every entry alike on an empty query, so the registry order survives", () => {
    expect(scoreTool(GENERATE, "")).toBe(scoreTool(NAVIGATE, ""));
  });

  it("is 0 for a miss", () => {
    expect(scoreTool(GENERATE, "zzz")).toBe(0);
  });
});

describe("filterToolCatalogue", () => {
  it("puts the tool the user meant first", () => {
    // The whole point of ranking: unranked, browser_navigate came first because
    // the registry lists it first and "gen" appears in "agent's".
    expect(flat("gen")[0]).toBe("generate_image");
  });

  it("finds a tool typed in the wrong layout", () => {
    expect(flat("пут")).toContain("generate_image");
  });

  it("leaves the registry order alone when there is no query", () => {
    expect(flat("")).toEqual(["browser_navigate", "generate_image", "transcribe_audio"]);
  });

  it("returns no groups when nothing matches", () => {
    expect(filterToolCatalogue(ALL, "zzz")).toEqual([]);
  });
});

describe("recent tools", () => {
  it("puts the newest first", () => {
    expect(rememberTool(["a"], "b")).toEqual(["b", "a"]);
  });

  it("moves a repeat to the front rather than duplicating it", () => {
    expect(rememberTool(["a", "b"], "b")).toEqual(["b", "a"]);
  });

  it("caps the list, so the group stays a shortcut", () => {
    let recent: readonly string[] = [];
    for (const id of ["a", "b", "c", "d", "e", "f", "g"]) recent = rememberTool(recent, id);
    expect(recent).toHaveLength(RECENT_LIMIT);
    expect(recent[0]).toBe("g");
  });

  it("forgets one without touching the others", () => {
    expect(forgetTool(["a", "b", "c"], "b")).toEqual(["a", "c"]);
  });

  it("resolves ids against the CURRENT catalogue, in recency order", () => {
    expect(recentTools(ALL, ["transcribe_audio", "generate_image"]).map((e) => e.id)).toEqual([
      "transcribe_audio",
      "generate_image",
    ]);
  });

  it("drops an id the host no longer offers instead of rendering a dead row", () => {
    expect(recentTools(ALL, ["gone", "generate_image"]).map((e) => e.id)).toEqual([
      "generate_image",
    ]);
  });
});

describe("menu navigation", () => {
  it("opens at the top on Down", () => {
    expect(nextRow(NO_ROW, 1, 3)).toBe(0);
  });

  it("opens at the BOTTOM on Up, so the last row is one keystroke away", () => {
    expect(nextRow(NO_ROW, -1, 3)).toBe(2);
  });

  it("wraps past the end, and before the start", () => {
    expect(nextRow(2, 1, 3)).toBe(0);
    expect(nextRow(0, -1, 3)).toBe(2);
  });

  it("moves one row at a time — a held key is the browser repeating the press", () => {
    expect(nextRow(nextRow(nextRow(NO_ROW, 1, 5), 1, 5), 1, 5)).toBe(2);
  });

  it("refuses to move an empty list", () => {
    expect(nextRow(NO_ROW, 1, 0)).toBe(NO_ROW);
  });

  it("reads only the arrow keys", () => {
    expect(stepForKey("ArrowDown")).toBe(1);
    expect(stepForKey("ArrowUp")).toBe(-1);
    expect(stepForKey("a")).toBe(0);
    expect(stepForKey("Enter")).toBe(0);
  });
});
