import { describe, expect, it } from "vitest";

import { readUiAction } from "./ui-action";

const CLICK = { id: "a1", label: "Save", action: { kind: "click", ref: "@e1" } };

describe("readUiAction", () => {
  it("reads a click block", () => {
    expect(readUiAction(CLICK)).toEqual(CLICK);
  });

  it("reads a fill block with its value", () => {
    const block = {
      id: "a2",
      label: "Fill the name",
      action: { kind: "fill", ref: "@e4", value: "Ada" },
    };
    expect(readUiAction(block)).toEqual(block);
  });

  it.each([
    ["not an object", "nope"],
    ["null", null],
    ["no id", { label: "Save", action: CLICK.action }],
    ["empty id", { id: "", label: "Save", action: CLICK.action }],
    ["no label", { id: "a1", action: CLICK.action }],
    ["no action", { id: "a1", label: "Save" }],
    ["unknown action kind", { ...CLICK, action: { kind: "drag", ref: "@e1" } }],
    ["action without a ref", { ...CLICK, action: { kind: "click" } }],
  ])("returns null for %s", (_name, input) => {
    expect(readUiAction(input)).toBeNull();
  });

  /**
   * The sharpest case: a `fill` missing its value would otherwise read as a
   * fill with an empty one, and CLEAR the field the user approved typing into.
   */
  it("returns null for a fill with no value", () => {
    expect(
      readUiAction({ id: "a3", label: "Fill", action: { kind: "fill", ref: "@e4" } })
    ).toBeNull();
  });
});
