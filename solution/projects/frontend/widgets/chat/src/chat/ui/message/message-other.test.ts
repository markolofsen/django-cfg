import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import { isOtherParticipant, type ChatMessage } from "../../core/conversation/parts";
import { OTHER_BUBBLE } from "./author";

const strip = (file: string) =>
  readFileSync(new URL(file, import.meta.url), "utf8")
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/\/\/.*$/gm, "");

const turn = (extra: Partial<ChatMessage>): ChatMessage => ({
  id: "m",
  role: "user",
  parts: [],
  status: { state: "complete" },
  createdAt: 0,
  ...extra,
});

describe("who is 'another participant'", () => {
  it("is a user turn marked from another seat", () => {
    expect(isOtherParticipant(turn({ from: "other" }))).toBe(true);
  });

  it("is never this seat's own turn, marked or not", () => {
    expect(isOtherParticipant(turn({}))).toBe(false);
    expect(isOtherParticipant(turn({ from: "me" }))).toBe(false);
  });

  it("is never the assistant, whatever it is marked", () => {
    expect(isOtherParticipant(turn({ role: "assistant", from: "other" }))).toBe(false);
  });
});

describe("the other participant's bubble", () => {
  it("is a bubble of its own, in stock tokens and not the sender's", () => {
    expect(OTHER_BUBBLE).toContain("bg-muted");
    expect(OTHER_BUBBLE).toContain("rounded-2xl");
    expect(OTHER_BUBBLE).not.toContain("bg-secondary");
    // A palette of our own would stop tracking the theme.
    expect(OTHER_BUBBLE).not.toMatch(/#[0-9a-f]{3,6}|rgb\(|hsl\(|\[--/i);
  });

  it("is chosen by the frame, on the left, apart from `is-user`", () => {
    const code = strip("./message.tsx");
    expect(code).toContain("OTHER_BUBBLE");
    expect(code).toContain('"is-other"');
    expect(code).toContain("isOther && OTHER_BUBBLE");
    // The sender's own styling stays gated on `is-user`, which an other turn lacks.
    expect(code).toContain("const isUser = message.role === \"user\" && !isOther");
  });

  it("puts the speaker line in as the default header", () => {
    expect(strip("./message.tsx")).toContain("<MessageAuthor message={message} />");
  });
});
