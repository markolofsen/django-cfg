import { describe, expect, it } from "vitest";

import type { Draft } from "./outbound";
import { unmetNeed, type ToolNeed } from "./tool-prompt";

const NEEDS: Record<string, ToolNeed> = {
  transcribe_audio: "file",
  skill: "skill",
};

const draft = (over: Partial<Draft> = {}): Draft => ({
  text: "",
  pickedTools: [],
  ...over,
});

const pick = (id: string) => ({ id, label: id, needs: NEEDS[id] });

describe("unmetNeed", () => {
  it("says nothing with no picks", () => {
    expect(unmetNeed(draft())).toBeNull();
  });

  it("says nothing for a tool whose object is the next sentence", () => {
    // generate_image wants a prompt, and the prompt IS what the user types.
    expect(unmetNeed(draft({ pickedTools: [pick("generate_image")] }))).toBeNull();
  });

  /** Text-only surface: nothing on the draft can answer a `file` need. */
  it("names the file a picked tool has no way to get otherwise", () => {
    expect(unmetNeed(draft({ pickedTools: [pick("transcribe_audio")] }))).toBe("file");
  });

  /**
   * One line, one need. The FIRST unmet need wins, which is what keeps the
   * placeholder a sentence rather than a list.
   */
  it("names only the first need when two picks want different things", () => {
    const both = [pick("transcribe_audio"), pick("skill")];

    expect(unmetNeed(draft({ pickedTools: both }))).toBe("file");
    expect(unmetNeed(draft({ pickedTools: [pick("skill"), pick("transcribe_audio")] }))).toBe(
      "skill",
    );
  });

  /** A tool the catalogue does not describe asks for nothing it cannot prove. */
  it("says nothing for an unknown tool", () => {
    expect(unmetNeed(draft({ pickedTools: [pick("some_future_tool")] }))).toBeNull();
  });
});
