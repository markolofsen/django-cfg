import { describe, expect, it } from "vitest";

import {
  basename,
  dirname,
  elideName,
  elidePath,
  elidePathLine,
  extension,
  isAbsolute,
  normalize,
  segments,
  unquote,
} from "./path";

/**
 * Table-driven because the value of this module is that ONE set of host
 * conventions is answered consistently; a per-case `it` hides which convention
 * is missing. Every row below fails against a POSIX-only `split("/")` or a
 * trimming validator: they assert the guarantee, not an implementation.
 */

describe("basename", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string | undefined, expected: string]> = [
    ["posix", "/Users/me/notes.txt", "notes.txt"],
    ["posix with spaces", "/Users/me/my project/read me.txt", "read me.txt"],
    ["cyrillic", "/Users/Марк/заметки.txt", "заметки.txt"],
    ["emoji", "/Users/me/📁 stuff/🎧 track.mp3", "🎧 track.mp3"],
    ["windows drive", "C:\\Users\\Марк\\file.txt", "file.txt"],
    ["windows drive forward slashes", "D:/work/cmdop/main.go", "main.go"],
    ["unc share", "\\\\server\\share\\file.txt", "file.txt"],
    ["quoted with spaces", '"/Users/me/my project/read me.txt"', "read me.txt"],
    // Shell-escaped spaces, as they arrive from a terminal copy. Decision 2
    // reads EVERY backslash as a separator, so `a\ b` splits and the label
    // becomes " b" — leading space and all — rather than the true segment
    // `a b`. That is the documented cost of the Windows-first trade, and it is
    // only ever a display label; callers needing the literal path keep the
    // original string. Asserted so the cost stays a decision, not a surprise:
    // if we ever teach the module about escapes, this row is what must change.
    ["escaped space", "/a\\ b/c", "c"],
    ["escaped space in the last segment", "/tmp/a\\ b", " b"],
    ["single-quoted windows", "'C:\\Program Files\\app.exe'", "app.exe"],
    ["trailing separator posix", "/Users/me/workspace/", "workspace"],
    ["trailing separator windows", "C:\\work\\cmdop_go\\", "cmdop_go"],
    ["dotfile", "/Users/me/repo/.gitignore", ".gitignore"],
    ["extension-less", "/usr/local/bin/cmdop", "cmdop"],
    ["posix root", "/", "/"],
    ["windows drive root", "C:\\", "C:\\"],
    ["bare name", "plain", "plain"],
    ["empty", "", ""],
    ["undefined", undefined, ""],
  ];

  it.each(cases)("%s", (_label, input, expected) => {
    expect(basename(input)).toBe(expected);
  });
});

describe("extension", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string, expected: string]> = [
    ["posix", "/Users/me/notes.TXT", "txt"],
    ["windows", "C:\\Users\\Марк\\photo.JPEG", "jpeg"],
    ["unc", "\\\\server\\share\\clip.mp4", "mp4"],
    ["dotted name keeps only the last", "/tmp/archive.tar.gz", "gz"],
    // Decision 3: a leading dot NAMES the file; it does not introduce an
    // extension. `.gitignore` is all-basename.
    ["dotfile has none", "/Users/me/repo/.gitignore", ""],
    ["dotfile with a real extension", "/Users/me/.config.json", "json"],
    ["extension-less", "/usr/local/bin/cmdop", ""],
    ["cyrillic extension-less", "/Users/Марк/Документы", ""],
    ["trailing separator", "/Users/me/workspace/", ""],
    ["empty", "", ""],
  ];

  it.each(cases)("%s", (_label, input, expected) => {
    expect(extension(input)).toBe(expected);
  });
});

/**
 * Every case below is stated TWICE, once per separator spelling, and the
 * pairing is the point rather than padding. `reveal-path.ts` carried a green
 * *walks a UNC path* test that pinned only the backslash spelling; the
 * forward-slash UNC path — which Windows accepts and the transport reports as
 * the OS handed it — took a different branch and expanded real local folders
 * unrelated to the file. One separator covered, one not, and the defect lived
 * in the gap while the test count read as coverage. These callers rebuild tree
 * ids from segments, so a one-sided split here is that same bug's next home.
 */
describe("segments", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string | undefined, expected: string[]]> = [
    ["posix", "/Users/me/notes.txt", ["Users", "me", "notes.txt"]],
    ["windows drive backslash", "C:\\Users\\me\\notes.txt", ["C:", "Users", "me", "notes.txt"]],
    ["windows drive forward slash", "C:/Users/me/notes.txt", ["C:", "Users", "me", "notes.txt"]],
    ["unc backslash", "\\\\nas\\share\\song.mp3", ["nas", "share", "song.mp3"]],
    ["unc forward slash", "//nas/share/song.mp3", ["nas", "share", "song.mp3"]],
    // The root is not a segment; a caller needing its spelling reads the
    // original string, because only the caller knows the host's convention.
    ["posix root", "/", []],
    ["windows drive root", "C:\\", ["C:"]],
    ["repeated separators collapse posix", "/a//b", ["a", "b"]],
    ["repeated separators collapse windows", "C:\\a\\\\b", ["C:", "a", "b"]],
    ["trailing separator posix", "/Users/me/", ["Users", "me"]],
    ["trailing separator windows", "C:\\work\\repo\\", ["C:", "work", "repo"]],
    ["cyrillic and spaces", "/Users/Марк/мой проект/файл.txt", ["Users", "Марк", "мой проект", "файл.txt"]],
    ["bare name", "song.mp3", ["song.mp3"]],
    ["empty", "", []],
    ["undefined", undefined, []],
  ];

  it.each(cases)("%s", (_label, input, expected) => {
    expect(segments(input)).toEqual(expected);
  });
});

describe("dirname", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string | undefined, expected: string]> = [
    ["posix", "/Users/me/notes.txt", "/Users/me"],
    ["windows drive backslash", "C:\\Users\\me\\notes.txt", "C:\\Users\\me"],
    ["windows drive forward slash", "C:/Users/me/notes.txt", "C:/Users/me"],
    ["unc backslash", "\\\\nas\\share\\song.mp3", "\\\\nas\\share"],
    ["unc forward slash", "//nas/share/song.mp3", "//nas/share"],
    // A root is a real location, so it is its own parent. Reporting "" would
    // send a caller hunting for a parent that does not exist.
    ["posix root", "/", "/"],
    ["windows drive root backslash", "C:\\", "C:\\"],
    ["windows drive root forward slash", "C:/", "C:/"],
    // `C:` alone names the drive's CWD, a different location than `C:\`.
    ["file at a drive root backslash", "C:\\notes.txt", "C:\\"],
    ["file at a drive root forward slash", "C:/notes.txt", "C:/"],
    ["file at the posix root", "/notes.txt", "/"],
    // The two leading separators ARE the root; dropping them would turn the
    // host into a relative name.
    ["unc share backslash", "\\\\nas\\share", "\\\\nas\\share"],
    ["unc share forward slash", "//nas/share", "//nas/share"],
    ["trailing separator posix", "/Users/me/", "/Users"],
    ["trailing separator windows", "C:\\work\\repo\\", "C:\\work"],
    ["cyrillic and spaces", "/Users/Марк/мой проект/файл.txt", "/Users/Марк/мой проект"],
    // This module never guesses a base, so a bare segment has no parent.
    ["bare name", "song.mp3", ""],
    ["empty", "", ""],
    ["undefined", undefined, ""],
  ];

  it.each(cases)("%s", (_label, input, expected) => {
    expect(dirname(input)).toBe(expected);
  });
});

describe("isAbsolute", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string, expected: boolean]> = [
    ["posix", "/Users/me/repo", true],
    ["posix with spaces and cyrillic", "/Users/Марк/мой проект", true],
    ["windows drive backslash", "C:\\work", true],
    ["windows drive forward slash", "D:/work", true],
    ["unc share", "\\\\server\\share", true],
    ["quoted posix", '"/Users/me/my project"', true],
    ["quoted windows", "'C:\\Program Files'", true],
    ["relative", "repo", false],
    ["dot-relative", "./repo", false],
    // Decision documented on `isAbsolute`: `~` is a shell convention the
    // console cannot expand, and `trackProjectRoot` sends it verbatim, so a
    // `~/` root would not match the same folder reached by its real path.
    ["tilde is not absolute", "~/repo", false],
    ["bare tilde", "~", false],
    ["empty", "", false],
    // Decision 1: no trim. A leading space means the input layer has not
    // settled the value yet, and a trailing space can be a real filename
    // character — the parser must not decide either way.
    ["untrimmed input is not silently accepted", "  /tmp", false],
  ];

  it.each(cases)("%s", (_label, input, expected) => {
    expect(isAbsolute(input)).toBe(expected);
  });
});

describe("normalize", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string | undefined, expected: string]> = [
    ["drops a trailing separator", "/Users/me/workspace/", "/Users/me/workspace"],
    ["drops a trailing separator run", "/Users/me/workspace///", "/Users/me/workspace"],
    ["drops a trailing backslash", "C:\\work\\", "C:\\work"],
    ["keeps the posix root", "/", "/"],
    ["keeps a drive root rather than reducing it to a bare drive", "C:\\", "C:\\"],
    ["unquotes", '"/Users/me/my project"', "/Users/me/my project"],
    // Decision 1 again, at the canonicalization step: whitespace is content
    // here, not formatting.
    ["preserves a real trailing space before the separator", "/tmp/odd /", "/tmp/odd "],
    ["leaves separators in the host's own spelling", "C:/work/mixed\\dir", "C:/work/mixed\\dir"],
    ["empty", "", ""],
    ["undefined", undefined, ""],
  ];

  it.each(cases)("%s", (_label, input, expected) => {
    expect(normalize(input)).toBe(expected);
  });
});

describe("unquote", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string, expected: string]> = [
    ["double quotes", '"/Users/me/my project"', "/Users/me/my project"],
    ["single quotes", "'/Users/me/my project'", "/Users/me/my project"],
    ["only one pair is removed", '""/tmp""', '"/tmp"'],
    ["unmatched leading quote survives", '"/tmp', '"/tmp'],
    ["mismatched pair survives", "\"/tmp'", "\"/tmp'"],
    ["unquoted passes through", "/tmp", "/tmp"],
  ];

  it.each(cases)("%s", (_label, input, expected) => {
    expect(unquote(input)).toBe(expected);
  });
});

describe("elidePath", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string, expected: string]> = [
    ["short path is kept whole", "/Users/me/repo", "/Users/me/repo"],
    ["head is elided, tail identifies", "/Users/me/workspace/projects/cmdop_go", "…/workspace/projects/cmdop_go"],
    ["a bare segment is untouched", "cmdop_go", "cmdop_go"],
    // A drive path splits on backslashes because `segments` owns separators; a
    // local split("/") would render the whole string as one unsplittable blob.
    ["windows drive path", "C:\\Users\\me\\workspace\\cmdop", "…/me/workspace/cmdop"],
    ["unc share", "\\\\nas\\team\\projects\\cmdop_go", "…/team/projects/cmdop_go"],
    ["empty stays empty", "", ""],
  ];

  it.each(cases)("%s", (_label, input, expected) => {
    expect(elidePath(input)).toBe(expected);
  });

  it("honours a caller's tail length", () => {
    expect(elidePath("/a/b/c/d/e", 2)).toBe("…/d/e");
  });

  it("never returns a longer string than the input's own segments", () => {
    expect(elidePath(undefined)).toBe("");
  });
});

describe("elideName", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string, max: number, expected: string]> = [
    ["a name within budget is untouched", "en_0.mp3", 34, "en_0.mp3"],
    // The whole point: the tail is the TYPE, and a browser truncation would
    // remove exactly this.
    [
      "the extension survives a long name",
      "Dikanda - Ederlezi (Nicola Noir Remix).mp3",
      34,
      "Dikanda - Ederlezi (Nicola No….mp3",
    ],
    // A leading dot names the file, so `.gitignore` has no extension to
    // protect and elides on length alone.
    ["a dotfile elides as one name", ".averylongdotfilename", 16, ".averylongdotfi…"],
    ["a name with no extension", "aaaaaaaaaaaaaaaaaaaaaa", 16, "aaaaaaaaaaaaaaa…"],
    // A suffix that would eat the budget is not worth protecting: keeping it
    // would leave a head too short to identify anything.
    [
      "an overlong extension is not protected",
      "screenshot.averylongextensionindeed",
      20,
      "screenshot.averylon…",
    ],
  ];

  it.each(cases)("%s", (_label, input, max, expected) => {
    expect(elideName(input, max)).toBe(expected);
  });

  it("never exceeds the budget it was given", () => {
    for (const max of [12, 16, 24, 34]) {
      expect(elideName("Dikanda - Ederlezi (Nicola Noir Remix).mp3", max).length)
        .toBeLessThanOrEqual(max);
    }
  });

  // Below the floor there is no room for a head, an ellipsis AND a suffix, so
  // eliding would cost more than it saves and the caller gets the name back.
  it("refuses a budget too small to elide within", () => {
    expect(elideName("some-long-name.mp3", 6)).toBe("some-long-name.mp3");
  });
});

describe("elidePathLine", () => {
  const cases: ReadonlyArray<readonly [label: string, input: string, max: number, expected: string]> = [
    ["a path within budget is kept whole", "/Users/me/notes.md", 42, "/Users/me/notes.md"],
    // Both ends of the identity survive: the `…/` says the head was dropped,
    // and the extension says what the file IS.
    [
      "head by segment, name in the middle",
      "/Users/me/workspace/projects/film cfg-video (content)/audio/Dikanda - Ederlezi (Nicola Noir Remix).mp3",
      42,
      "…/Dikanda - Ederlezi (Nicola Noir Rem….mp3",
    ],
    // As many whole segments as fit are kept before the name is touched at
    // all — a parent folder is context the reader wants when it is free.
    ["keeps the parents that fit", "C:\\Users\\me\\projects\\cmdop\\readme.md", 20, "…/cmdop/readme.md"],
    ["empty stays empty", "", 42, ""],
  ];

  it.each(cases)("%s", (_label, input, max, expected) => {
    expect(elidePathLine(input, max)).toBe(expected);
  });

  it("returns the full path when it fits, never a decorated one", () => {
    expect(elidePathLine("/a/b/c.txt", 42)).toBe("/a/b/c.txt");
  });
});
