import { describe, expect, it } from "vitest";

import { appendToolMarkers, readToolMarkers, toolMarker, type ToolPick } from "./picks";

const pick = (id: string, label = id): ToolPick => ({ id, label });

describe("toolMarker", () => {
  it("writes a markdown link carrying the label and the id", () => {
    expect(toolMarker("upload_file", "Upload a file")).toBe(
      "[Upload a file](app://tool/upload_file)",
    );
  });

  /** A link with no text renders as nothing, hiding the pick from the model. */
  it("falls back to the id when the label is empty", () => {
    expect(toolMarker("bash", "")).toBe("[bash](app://tool/bash)");
  });

  /**
   * MUTANT: drop the label escaping → the pair closes early and the href leaks
   * into the prose as visible text.
   */
  it("escapes brackets in the label so the link's text cannot end early", () => {
    expect(toolMarker("read_file", "Read [a] file")).toBe(
      "[Read \\[a\\] file](app://tool/read_file)",
    );
  });

  /** The writer and the reader must agree, or a host reconciles against nothing. */
  it("round-trips through the reader", () => {
    expect(readToolMarkers(toolMarker("transcribe_audio", "Transcribe audio"))).toEqual([
      "transcribe_audio",
    ]);
  });

  /** An escaped bracket must not be read as the end of the label. */
  it("round-trips a label carrying brackets", () => {
    expect(readToolMarkers(toolMarker("read_file", "Read [a] file"))).toEqual(["read_file"]);
  });
});

describe("readToolMarkers", () => {
  it("finds markers in order, inside prose", () => {
    const text = "here [Read](app://tool/read_file) and then [Shell](app://tool/bash) please";

    expect(readToolMarkers(text)).toEqual(["read_file", "bash"]);
  });

  it("finds none in text that names no tool", () => {
    expect(readToolMarkers("just upload_file by name")).toEqual([]);
  });

  /**
   * The id is what identifies the pick; the label is prose. A link to any other
   * app host, or an ordinary web link, names no tool.
   */
  it("ignores links that are not tool links", () => {
    const text = "[a](app://note/read_file) [b](https://example.com/tool/bash)";

    expect(readToolMarkers(text)).toEqual([]);
  });
});

describe("appendToolMarkers", () => {
  it("returns the text unchanged when nothing was picked", () => {
    expect(appendToolMarkers("hello", [])).toBe("hello");
  });

  /**
   * MUTANT: drop the `undefined` guard → this throws.
   *
   * `Draft` crosses the package boundary, so a host's own draft and one
   * restored from storage both arrive without the field. It reached the send
   * path, which is the one place a crash loses the user's message.
   */
  it("treats a draft with no list as having picked nothing", () => {
    expect(appendToolMarkers("hello", undefined)).toBe("hello");
  });

  it("appends after the typed text", () => {
    expect(appendToolMarkers("read this", [pick("read_file", "Read a file")])).toBe(
      "read this [Read a file](app://tool/read_file)",
    );
  });

  it("is the whole text when nothing was typed", () => {
    expect(appendToolMarkers("", [pick("bash")])).toBe("[bash](app://tool/bash)");
  });

  it("appends every pick", () => {
    expect(appendToolMarkers("go", [pick("bash"), pick("read_file")])).toBe(
      "go [bash](app://tool/bash) [read_file](app://tool/read_file)",
    );
  });

  /**
   * MUTANT: drop the `already` filter → this dies.
   *
   * A restored draft carries its markers in the text AND its picks in state, so
   * without the guard every reload doubles them.
   */
  it("does not repeat a tool the text already names", () => {
    const text = "run [Shell](app://tool/bash) now";

    expect(appendToolMarkers(text, [pick("bash")])).toBe(text);
  });

  /**
   * The duplicate check reads the ID, so a label the user renamed or a locale
   * changed still counts as the same pick.
   */
  it("matches an existing marker by id, not by the label beside it", () => {
    const text = "run [Запустить shell](app://tool/bash) now";

    expect(appendToolMarkers(text, [pick("bash", "Shell")])).toBe(text);
  });

  it("appends only the picks the text does not already name", () => {
    expect(
      appendToolMarkers("run [bash](app://tool/bash)", [pick("bash"), pick("read_file")]),
    ).toBe("run [bash](app://tool/bash) [read_file](app://tool/read_file)");
  });

  /** Trailing space is the ordinary state of a draft mid-typing. */
  it("does not leave a double space", () => {
    expect(appendToolMarkers("write  ", [pick("write_file")])).toBe(
      "write [write_file](app://tool/write_file)",
    );
  });
});
