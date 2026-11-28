import { describe, expect, it } from "vitest";

import { CHAT_DICTIONARIES } from "../../../i18n";
import { step } from "../../ui/run/stories/steps";
import { phraseText, stepPhrase, stepVerb, type PhraseWords } from "./phrase";
import { selectRun } from "./view";

const words: PhraseWords = { verb: CHAT_DICTIONARIES.en.run.verb, kind: (k) => `<${k}>` };
const first = (parts: Parameters<typeof selectRun>[0]) => selectRun(parts).steps[0]!;

describe("stepVerb", () => {
  it("reads the kind of work from the role, then from the tool's own words", () => {
    expect(stepVerb(first([step("s1", { name: "mcp__srv__get_order" })]))).toBe("read");
    expect(stepVerb(first([step("s1", { name: "kbSearch" })]))).toBe("search");
    expect(stepVerb(first([step("s1", { name: "create_ticket" })]))).toBe("write");
    expect(stepVerb(first([step("s1", { name: "weather" })]))).toBe("other");
    expect(stepVerb(first([step("s1", { name: "weather", role: "retriever" })]))).toBe("search");
    expect(stepVerb(first([{ type: "reasoning", id: "r", text: "" }]))).toBe("think");
  });
});

describe("stepPhrase", () => {
  it("a server label is the whole sentence, and the host's map comes first", () => {
    const s = first([step("s1", { name: "kb_search", label: "Searching the knowledge base" })]);
    expect(stepPhrase(s, words, undefined, "Ignored")).toMatchObject({ before: "Searching the knowledge base", after: "" });
    expect(phraseText(stepPhrase(s, words, { kb_search: "Looking it up" }, undefined))).toBe("Looking it up");
  });

  it("with no label a template speaks, around a server-named object", () => {
    const s = first([step("s1", { name: "read_page" })]);
    expect(stepPhrase(s, words, undefined, "Sales")).toEqual({ before: "Read ", object: "Sales", after: "", named: true });
    // No name from the server: the tool's own readable name, plain (not a named chip).
    expect(stepPhrase(s, words, undefined, undefined)).toMatchObject({ object: "read_page", named: false });
  });

  it("uses the live form while the step runs", () => {
    const s = first([step("s1", { name: "search_pages", status: "running" })]);
    expect(phraseText(stepPhrase(s, words, undefined, "Projects"))).toBe("Searching Projects");
  });

  it("puts the object where the language wants it", () => {
    const ja = { ...words, verb: CHAT_DICTIONARIES.ja.run.verb };
    const p = stepPhrase(first([step("s1", { name: "read_page" })]), ja, undefined, "Sales");
    expect(p).toMatchObject({ before: "", object: "Sales", after: " を読み取りました" });
  });

  it("a thought is named by its summary, else Thought / Thinking…; other kinds by their generic word", () => {
    const thought = (meta: object, streaming: boolean) => first([{ type: "reasoning", id: "r", text: "", streaming, meta }]);
    expect(phraseText(stepPhrase(thought({ summary: "Considering user needs" }, false), words, undefined, undefined))).toBe("Considering user needs");
    expect(phraseText(stepPhrase(thought({}, false), words, undefined, undefined))).toBe("Thought");
    expect(phraseText(stepPhrase(thought({}, true), words, undefined, undefined))).toBe("Thinking…");
    expect(phraseText(stepPhrase(first([step("s1", { kind: "usage", name: undefined })]), words, undefined, undefined))).toBe("<usage>");
  });
});
