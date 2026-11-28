import { describe, expect, it } from "vitest";

import { parentFolderLabel } from "./media-button";

describe("parentFolderLabel", () => {
  it("names the containing folder", () => {
    expect(parentFolderLabel("/Users/me/Music/Sanya.mp3")).toBe("Music");
  });

  it("says nothing for a file with no folder above it", () => {
    // A blank label is right here: an empty second row would make every card
    // taller for a fact that does not exist.
    expect(parentFolderLabel("Sanya.mp3")).toBe("");
    expect(parentFolderLabel("/Sanya.mp3")).toBe("");
  });

  it("reads a Windows path", () => {
    expect(parentFolderLabel("C:\\Users\\me\\Music\\Sanya.mp3")).toBe("Music");
  });

  it("survives repeated and trailing separators", () => {
    // Real paths arrive with both, and an empty segment would otherwise be
    // reported as the folder name.
    expect(parentFolderLabel("/Users//me///Music//Sanya.mp3")).toBe("Music");
  });
});
