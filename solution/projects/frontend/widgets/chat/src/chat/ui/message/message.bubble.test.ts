import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * A source ratchet over the bubble decision.
 *
 * This package has no jsdom, so the alternative to reading the source is not a
 * better test — it is no test. What is guarded here is not styling taste but
 * four decisions that are each one careless edit away from silently reverting,
 * and none of which any type or runtime check can see:
 *
 *   - the bubble belongs to the USER only,
 *   - the row never widens on an unbreakable token,
 *   - the readable measure sits on prose, not on the row,
 *   - role is declared once and read through `group-[.is-*]:`.
 *
 * Comments are stripped first, because every one of these strings also appears
 * in the prose above the code — a ratchet satisfied by its own documentation
 * would pass on a file with the implementation deleted. The stripper has its
 * own control test below, since a broken stripper fails open.
 */

const SOURCE = readFileSync(new URL("./message.tsx", import.meta.url), "utf8");
const CODE = SOURCE.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

describe("comment stripper (control)", () => {
  it("removes block and line comments but keeps code", () => {
    const stripped = "/* a */ const x = 1; // b\nconst y = 2;"
      .replace(/\/\*[\s\S]*?\*\//g, "")
      .replace(/\/\/.*$/gm, "");
    expect(stripped).toContain("const x = 1;");
    expect(stripped).toContain("const y = 2;");
    expect(stripped).not.toContain("a");
    expect(stripped).not.toContain("b");
  });

  it("leaves real code in message.tsx after stripping", () => {
    expect(CODE).toContain("group-[.is-user]:");
  });
});

describe("the bubble is the user's", () => {
  it("gives the user turn a background and radius", () => {
    expect(CODE).toContain("group-[.is-user]:rounded-2xl");
    expect(CODE).toContain("group-[.is-user]:bg-secondary");
  });

  /**
   * THE decision. Vercel bubbles `is-user` only; a bubble around a reply
   * containing code, a diff and a plan frames the product against itself.
   */
  it("never gives the assistant a bubble", () => {
    expect(CODE).not.toContain("group-[.is-assistant]:bg-");
    expect(CODE).not.toContain("group-[.is-assistant]:rounded");
  });

  /**
   * The action row is `h-7` in flow and gives MOST of that height back, so the
   * toolbar does not air out the transcript to serve a mostly-faint control.
   *
   * Not all of it: giving back the full 28px ended the row's box above the
   * toolbar, so the transcript measured its gap from there and the toolbar
   * overlapped the NEXT message wherever no speaker line separated them. 8px is
   * the largest give-back that keeps every toolbar nearer its own text.
   */
  it("gives most of the footer's height back, but never overlaps the next row", () => {
    expect(CODE).toContain("-mb-2");
    expect(CODE).not.toContain("-mb-7");
  });

  it("declares the role once, on the wrapper", () => {
    expect(CODE).toContain('"is-user items-end"');
    expect(CODE).toContain('"is-assistant"');
    expect(CODE).toContain('"is-other"');
    expect(CODE).toContain('"items-start"');
  });
});

describe("the toolbar has two ends, and one end still aligns to its speaker", () => {
  /**
   * The toolbar row spans the frame so a second control can sit at the far end.
   * That width is what makes `justify-between` mean anything — without it both
   * ends collapse together and the position is decorative.
   */
  it("spans the frame, so the far end is reachable", () => {
    expect(CODE).toContain("flex w-full items-center");
  });

  /**
   * MUTANT: make `justify-between` unconditional → this dies.
   */
  it("only justifies between when BOTH ends are filled", () => {
    expect(CODE).toContain("const bothEnds = footer !== undefined && footerEnd !== undefined");
    expect(CODE).toContain('bothEnds\n    ? "justify-between"');
  });

  /**
   * MUTANT: leave the single-end case unset → this dies. It WAS unset, and that
   * is the defect: a lone copy control sat at the left edge of the transcript
   * under a right-aligned user bubble.
   *
   * The reason it is not enough for the footer to align itself — which it does,
   * with its own `justify-end` — is that the footer is a 28px box. Justifying
   * inside 28px moves nothing. The 768px toolbar ROW is what places it, and an
   * unset `justify-content` resolves to `normal`, i.e. the left edge.
   */
  it("sends a single-end toolbar to the speaker's side", () => {
    expect(CODE).toContain('isUser\n      ? "justify-end"\n      : "justify-start"');
  });

  /**
   * The row must not appear for a message with no chrome at all: an empty `h-7`
   * strip would take back the height `-mb-7` returns and space the transcript
   * out for nothing.
   */
  it("renders no toolbar when neither end is supplied", () => {
    expect(CODE).toContain("footer !== undefined || footerEnd !== undefined");
    expect(CODE).toContain("{hasToolbar && (");
  });
});

describe("the bubble is narrower than the reply's measure", () => {
  /**
   * `w-fit` bounds only the short end. Without a cap a long paste reaches the
   * full column, giving the two speakers different measures with a background
   * on the wider one — the reverse of the intended asymmetry.
   */
  it("caps the bubble, and in ch so it survives a text-size change", () => {
    expect(CODE).toContain("group-[.is-user]:max-w-[52ch]");
  });

  it("keeps w-fit, so a short turn is still short", () => {
    expect(CODE).toContain("group-[.is-user]:w-fit");
  });

  /** A cap on the row would bound the gap the bubble is aligned within. */
  it("puts the cap on the bubble, never on the row", () => {
    const wrapper = CODE.slice(CODE.indexOf("data-role={message.role}"), CODE.indexOf("min-w-0"));
    expect(wrapper).not.toContain("max-w-[52ch]");
  });
});

describe("a pasted path must not widen the transcript", () => {
  it("keeps min-w-0 on the content column", () => {
    expect(CODE).toContain("min-w-0");
  });

  it("wraps unbreakable tokens inside the bubble", () => {
    expect(CODE).toContain("group-[.is-user]:[overflow-wrap:anywhere]");
  });
});

describe("the readable measure sits on prose, not on the row", () => {
  it("caps MessageProse at a line length", () => {
    expect(CODE).toContain("max-w-[72ch]");
  });

  /**
   * The cap must not reach the row: capping there would cap the widgets too,
   * and a diff or a table truncated to prose width is unreadable in a way that
   * looks deliberate.
   */
  it("leaves the assistant row at full column width", () => {
    expect(CODE).toContain("group-[.is-assistant]:w-full");
    const frame = CODE.slice(CODE.indexOf("ChatMessageFrame({"), CODE.indexOf("MessageProse"));
    expect(frame).not.toContain("max-w-[72ch]");
  });

  it("does not cap prose a second time inside the bubble", () => {
    expect(CODE).toContain("group-[.is-user]:max-w-none");
  });
});

/**
 * Both halves of the selection rule. Neither is visible to a type or a runtime
 * check, so losing the second half goes unnoticed.
 */
describe("a drag must not bridge two messages", () => {
  it("kills selection on the frame, including its padding and gaps", () => {
    expect(CODE).toContain("select-none");
  });

  /**
   * The regression they paid for: only markdown opted back in, so tool calls,
   * their output and attachments could not be copied at all. `*:` is required
   * rather than a branch list — a registry's parts are not ours to enumerate.
   */
  it("opts every rendered part back in, not a list of known branches", () => {
    expect(CODE).toContain("[&>*]:select-text");
  });
});

describe("a failed turn is visibly not an ordinary reply", () => {
  it("marks the failed state", () => {
    expect(CODE).toContain('message.status.state === "failed"');
    expect(CODE).toContain("border-destructive/40");
  });
});
