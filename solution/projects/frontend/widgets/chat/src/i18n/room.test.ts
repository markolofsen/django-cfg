import { describe, expect, it } from "vitest";

import { CHAT_DICTIONARIES } from "./index";
import { roomMentionItems } from "./room";

const en = CHAT_DICTIONARIES.en.room;
const ru = CHAT_DICTIONARIES.ru.room;

describe("room copy", () => {
  it("is written for every locale, none blank (key parity is the dictionaries gate's)", () => {
    for (const [locale, copy] of Object.entries(CHAT_DICTIONARIES)) {
      for (const [key, value] of Object.entries(copy.room)) {
        expect(value.trim(), `${locale} ${key}`).not.toBe("");
      }
    }
  });

  it("is not English passed off as another language", () => {
    for (const [locale, copy] of Object.entries(CHAT_DICTIONARIES)) {
      if (locale === "en") continue;
      expect(copy.room.everyone, locale).not.toBe(en.everyone);
      expect(copy.room.privateHint, locale).not.toBe(en.privateHint);
    }
  });
});

describe("roomMentionItems", () => {
  it("lists the assistant first, then the people, all as plain mentions", () => {
    const items = roomMentionItems(en, [{ id: "7", label: "Mark" }]);
    expect(items.map((i) => i.label)).toEqual(["Assistant", "Mark"]);
    expect(items[0]?.hint).toBe(en.assistantHint);
  });

  it("gives the assistant no seat, and a person the seat identity", () => {
    const [assistant, person] = roomMentionItems(en, [{ id: "7", label: "Mark" }]);
    expect(assistant).not.toHaveProperty("seat");
    expect(person?.seat).toBe("7");
    expect(person?.id).toBe("person:7");
  });

  it("offers no Everyone row: the room is the recipient chip's default, not a name", () => {
    expect(roomMentionItems(en).map((i) => i.label)).not.toContain("Everyone");
  });

  it("speaks the reader's language", () => {
    expect(roomMentionItems(ru)[0]?.label).toBe("Ассистент");
  });
});
