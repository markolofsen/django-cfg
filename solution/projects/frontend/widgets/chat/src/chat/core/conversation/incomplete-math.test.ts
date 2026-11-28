import { describe, expect, it } from "vitest";

import { maskIncompleteMath } from "./incomplete-math";

/**
 * Pure, so it runs in microseconds and needs no renderer. The RENDERED
 * consequence — that a masked formula produces no katex — is asserted in
 * `content/response.test.tsx`, where the parser is present to prove it.
 */

describe("a closed formula is untouched", () => {
  const closed = [
    ["inline", "complexity is $$O(n \\log n)$$ here"],
    ["block", "$$\na^2 + b^2 = c^2\n$$"],
    ["two in a row", "$$a$$ and $$b$$"],
    ["none at all", "just prose with no math"],
    ["empty", ""],
  ] as const;

  for (const [name, source] of closed) {
    it(`${name}: returns the SAME string, not an equal one`, () => {
      // Identity, not equality: an untouched input must not be rebuilt, because
      // `Response` is memoised on `children` and a new string defeats the memo
      // on every token.
      expect(maskIncompleteMath(source)).toBe(source);
    });
  }
});

describe("an unclosed formula is masked", () => {
  it("escapes the opening delimiter", () => {
    expect(maskIncompleteMath("complexity is $$O(n \\log")).toBe(
      "complexity is \\$\\$O(n \\log",
    );
  });

  it("masks only the LAST opener, leaving the closed pair alone", () => {
    // The mid-stream state after a complete formula: one is an answer, one is
    // still being written.
    expect(maskIncompleteMath("$$a$$ then $$b")).toBe("$$a$$ then \\$\\$b");
  });

  it("handles the delimiter arriving with nothing after it yet", () => {
    expect(maskIncompleteMath("here it comes $$")).toBe("here it comes \\$\\$");
  });
});

describe("fenced code is not math", () => {
  it("ignores a lone $$ inside a closed fence", () => {
    // `$$` is the shell's PID. Counting it would mask a delimiter in prose that
    // is actually balanced — and rewriting inside the fence would corrupt code
    // the user copies.
    const source = "```sh\necho $$\n```\n\nplain prose";

    expect(maskIncompleteMath(source)).toBe(source);
  });

  it("ignores $$ inside an UNCLOSED fence, which owns the rest of the string", () => {
    // Mid-stream: the fence is open, so everything after it is code.
    const source = "```sh\necho $$ && echo $$$";

    expect(maskIncompleteMath(source)).toBe(source);
  });

  it("still masks a real opener that appears BEFORE a fence", () => {
    const source = "$$x = 1\n\n```sh\necho hi\n```\n";

    expect(maskIncompleteMath(source)).toBe("\\$\\$x = 1\n\n```sh\necho hi\n```\n");
  });

  it("masks the opener in the LAST prose segment, not the first", () => {
    // Needs TWO prose segments split by a fence, or the loop direction cannot be
    // observed: with one segment `lastIndexOf` already picks the right delimiter
    // and a mutant that scans forwards produces identical output. That mutant
    // survives a gap in the INPUTS, not a blind assertion.
    const source = "$$a$$ before\n\n```sh\necho hi\n```\n\nand $$b = 2";

    expect(maskIncompleteMath(source)).toBe(
      "$$a$$ before\n\n```sh\necho hi\n```\n\nand \\$\\$b = 2",
    );
  });

  it("leaves a $$ inside a LATER unclosed fence alone", () => {
    // The other half of the same gap: the trailing segment must be recognised as
    // fenced. A mutant marking it prose masks a shell PID inside code — visible
    // to the user as a stray backslash in a command they are about to copy.
    const source = "$$a$$ done\n\n```sh\necho $$";

    expect(maskIncompleteMath(source)).toBe(source);
  });

  it("counts a fence's $$ as neutral rather than as a closer", () => {
    // THE trap this splitting exists for: without it, the fenced `$$` pairs with
    // the prose one, the count reads even, and the genuinely-open formula at the
    // end is typeset from its prefix.
    const source = "$$open\n\n```sh\necho $$\n```\n";

    expect(maskIncompleteMath(source)).toBe("\\$\\$open\n\n```sh\necho $$\n```\n");
  });
});

describe("the control", () => {
  it("the function can return something OTHER than its input", () => {
    // Every assertion above except three is `toBe(source)`. If the function were
    // the identity, those would all pass while measuring nothing.
    expect(maskIncompleteMath("$$x")).not.toBe("$$x");
  });
});
