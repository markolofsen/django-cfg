import { describe, expect, it } from "vitest";

import { buildOutbound, emptyDraft, isEmpty, type Draft } from "./outbound";

describe("emptiness", () => {
  it("treats whitespace as empty", () => {
    expect(isEmpty({ text: "  \n " })).toBe(true);
    expect(isEmpty(emptyDraft)).toBe(true);
  });

  it("treats typed words as sendable", () => {
    expect(isEmpty({ text: "hi" })).toBe(false);
  });
});

describe("a picked tool reaches the model and not the transcript", () => {
  const picked: Draft = {
    text: "have a look",
    pickedTools: [{ id: "read_file", label: "Read a file" }],
  };

  /** The whole point of the marker: the model must be able to see the pick. */
  it("appends the marker to the outbound text", () => {
    expect(buildOutbound(picked, "m1", 0).text).toBe(
      "have a look [Read a file](app://tool/read_file)",
    );
  });

  /**
   * MUTANT: append the markers to `message` too → this dies.
   *
   * The sent bubble shows what the user WROTE. A marker there reads as
   * something they typed, and the chip beside it already says the same thing.
   */
  it("leaves the transcript's own text alone", () => {
    const { message } = buildOutbound(picked, "m1", 0);
    const text = message.parts.find((part) => part.type === "text");

    expect(text).toEqual({ type: "text", id: "m1:text", text: "have a look" });
    expect(JSON.stringify(message)).not.toContain("app://tool/");
  });

  /** A pick with no words is a request in itself. */
  it("sends a marker alone when nothing was typed", () => {
    const draft: Draft = { text: "", pickedTools: picked.pickedTools };

    expect(isEmpty(draft)).toBe(false);
    expect(buildOutbound(draft, "m2", 0).text).toBe("[Read a file](app://tool/read_file)");
  });

  /** Every draft written before the field existed still sends. */
  it("sends a draft that carries no list at all", () => {
    const legacy: Draft = { text: "plain" };

    expect(isEmpty(legacy)).toBe(false);
    expect(buildOutbound(legacy, "m3", 0).text).toBe("plain");
  });
});

/**
 * The link between a reply and what it answers must survive the send.
 *
 * The bubble the sender sees is built HERE, not from the wire — so a `replyTo`
 * the draft carried and this dropped leaves the sender looking at a turn whose
 * quote is gone, while every other reader (who loads it from storage) sees one.
 * Two renderings of the same message that disagree.
 */
describe("a reply keeps what it answers", () => {
  it("carries replyTo onto the echoed message", () => {
    const draft: Draft = { text: "круто", pickedTools: [], replyTo: "m-earlier" };

    expect(buildOutbound(draft, "m9", 0).message.replyTo).toBe("m-earlier");
  });

  it("leaves the field ABSENT when the draft answers nothing", () => {
    // Absent, not "" — `MessageQuote` keys on `undefined`, and an empty string
    // would send it looking up a message id nothing can match.
    const draft: Draft = { text: "просто так", pickedTools: [] };

    expect(buildOutbound(draft, "m10", 0).message.replyTo).toBeUndefined();
    expect("replyTo" in buildOutbound(draft, "m10", 0).message).toBe(false);
  });
});

describe("attachments", () => {
  const file = { id: "f1", name: "a.png", mime: "image/png", size: 10, kind: "image" as const, url: "https://x/a.png" };

  it("makes a draft with only a file sendable", () => {
    expect(isEmpty({ text: "", pickedTools: [], attachments: [file] })).toBe(false);
    expect(isEmpty({ text: "", pickedTools: [] })).toBe(true);
  });

  it("puts each file in the transcript after the words, and leaves the model text alone", () => {
    const out = buildOutbound({ text: "look", pickedTools: [], attachments: [file] }, "m1", 0);
    expect(out.message.parts.map((p) => p.type)).toEqual(["text", "attachment"]);
    expect(out.text).toBe("look");
  });
});
