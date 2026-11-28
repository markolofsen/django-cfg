import { describe, expect, it } from "vitest";

import {
  defaultRecipient,
  filterMentionItems,
  isPrivate,
  mentionedSeats,
  mentionSpans,
  mentionsAssistant,
  mentionToken,
  pickablePeople,
  recipientId,
  stillPickable,
  type MentionItem,
  type Person,
} from "./recipient";

const ITEMS: readonly MentionItem[] = [
  { id: "assistant", label: "Assistant", hint: "Answers when you mention it" },
  { id: "p1", label: "Mark Olofsen", seat: "u1" },
  { id: "p2", label: "Assistant Bot", seat: "g2" },
  { id: "p3", label: "Anna", seat: "g3" },
];

describe("the recipient", () => {
  const anna: Person = { id: "g3", label: "Anna" };

  it("is the room by default", () => {
    expect(defaultRecipient).toBe("all");
    expect(isPrivate(defaultRecipient)).toBe(false);
    expect(recipientId(defaultRecipient)).toBeUndefined();
  });

  it("is a private line when it is a person, and the wire id is the seat", () => {
    expect(isPrivate(anna)).toBe(true);
    expect(recipientId(anna)).toBe("g3");
  });

  it("is picked from the roster without this seat and without the assistant", () => {
    const roster: Person[] = [
      { id: "u1", label: "Mark" },
      { id: "g3", label: "Anna" },
      { id: "assistant", label: "Assistant" },
      { id: "g4", label: "Left Guest" },
    ];
    expect(pickablePeople(roster, "u1").map((p) => p.id)).toEqual(["g3", "g4"]);
  });

  it("never offers the assistant, whatever it is called", () => {
    expect(pickablePeople([{ id: "bot-1", label: "Aria" }], "u1", "bot-1")).toEqual([]);
  });

  it("falls back to the room once a sticky recipient is not in the roster", () => {
    const roster: Person[] = [{ id: "g3", label: "Anna" }];
    expect(stillPickable(anna, roster)).toBe(anna);
    expect(stillPickable({ id: "gone", label: "Gone" }, roster)).toBe("all");
    expect(stillPickable("all", roster)).toBe("all");
  });
});

describe("the token", () => {
  it("is the label after an @", () => {
    expect(mentionToken(ITEMS[1] as MentionItem)).toBe("@Mark Olofsen");
  });
});

describe("filtering the menu", () => {
  it("offers everything on a bare @", () => {
    expect(filterMentionItems(ITEMS, "")).toHaveLength(4);
  });

  it("matches the start of a label, ignoring case", () => {
    expect(filterMentionItems(ITEMS, "ass").map((i) => i.id)).toEqual(["assistant", "p2"]);
  });

  it("does not match the middle of a label", () => {
    expect(filterMentionItems(ITEMS, "lof")).toEqual([]);
  });

  it("matches across a space, for a name with two words", () => {
    expect(filterMentionItems(ITEMS, "mark o").map((i) => i.id)).toEqual(["p1"]);
  });

  it("offers nothing once the label is complete and a space follows", () => {
    expect(filterMentionItems(ITEMS, "Anna ")).toEqual([]);
  });
});

describe("mention spans", () => {
  it("is empty without a token", () => {
    expect(mentionSpans("hello there", ITEMS)).toEqual([]);
  });

  it("reports where each token sits, left to right", () => {
    const text = "@Anna and @Assistant, summarise";
    const spans = mentionSpans(text, ITEMS);
    expect(spans.map((s) => [text.slice(s.start, s.end), s.item.id])).toEqual([
      ["@Anna", "p3"],
      ["@Assistant", "assistant"],
    ]);
  });

  it("is case-insensitive", () => {
    expect(mentionSpans("@assistant hi", ITEMS).map((s) => s.item.id)).toEqual(["assistant"]);
  });

  it("lets the longer label win where one contains the other", () => {
    expect(mentionSpans("@Assistant Bot, hello", ITEMS).map((s) => s.item.id)).toEqual(["p2"]);
  });

  it("needs a boundary on both sides, so an address or a longer word is not a token", () => {
    expect(mentionSpans("mail me@Anna", ITEMS)).toEqual([]);
    expect(mentionSpans("@Annabel is here", ITEMS)).toEqual([]);
    expect(mentionSpans("@Anna, hi", ITEMS)).toHaveLength(1);
  });

  it("works with a non-Latin label", () => {
    const ru: readonly MentionItem[] = [{ id: "assistant", label: "Ассистент" }];
    expect(mentionSpans("@Ассистент, привет", ru)).toHaveLength(1);
    expect(mentionSpans("@Ассистентка", ru)).toEqual([]);
  });

  it("escapes a label that holds regex characters", () => {
    const odd: readonly MentionItem[] = [{ id: "x", label: "C++ (bot)" }];
    expect(mentionSpans("@C++ (bot) hi", odd)).toHaveLength(1);
  });

  it("is empty with no items", () => {
    expect(mentionSpans("@Anna hi", [])).toEqual([]);
  });
});

describe("the seats a text names", () => {
  it("lists seats once each, in order of first mention", () => {
    expect(mentionedSeats("@Anna @Mark Olofsen @Anna again", ITEMS)).toEqual(["g3", "u1"]);
  });

  it("leaves the assistant out: it is not a seat", () => {
    expect(mentionedSeats("@Assistant what did Anna say", ITEMS)).toEqual([]);
  });

  it("stops at eight", () => {
    const many = Array.from({ length: 12 }, (_, n): MentionItem => ({ id: `p${n}`, label: `P${n}x`, seat: `s${n}` }));
    const text = many.map((item) => mentionToken(item)).join(" ");
    expect(mentionedSeats(text, many)).toHaveLength(8);
  });
});

describe("a mention of the assistant", () => {
  it("is found anywhere in the text", () => {
    expect(mentionsAssistant("what did we decide, @Assistant", ITEMS)).toBe(true);
  });

  it("is not the assistant when a longer name wins", () => {
    expect(mentionsAssistant("@Assistant Bot", ITEMS)).toBe(false);
  });

  it("is not there without a token", () => {
    expect(mentionsAssistant("is the assistant here?", ITEMS)).toBe(false);
  });
});
