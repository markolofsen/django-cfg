import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Response } from "./response";

/**
 * `markdown.test.tsx` pins what the DEPENDENCY does. This pins what OUR
 * configuration of it does — the three decisions in `response.tsx` that a
 * future edit could quietly undo: one block, math on, mermaid on our renderer.
 *
 * Static markup, no DOM: the questions are "what did the parser decide" and
 * "did it throw", and neither needs a renderer.
 */

const render = (markdown: string) => renderToStaticMarkup(<Response>{markdown}</Response>);

describe("one block, not many", () => {
  it("resolves a reference definition, which splitting makes impossible", () => {
    // THE defect that chose this configuration. Split on the blank line, the
    // definition lands in a different parse and the reader sees a literal "[1]".
    // Measured on streamdown itself, not only on our old splitter.
    const html = render("see [the docs][1]\n\n[1]: https://example.com/x\n");

    expect(html).toContain('data-streamdown="link"');
    expect(html).not.toContain("[1]");
  });

  it("keeps a loose ordered list in ONE list", () => {
    // Two <ol> means the second item restarts at "1." — a wrong number is a lie
    // about the answer, not a cosmetic slip.
    const html = render("1. first\n\n2. second");

    expect(html.match(/<ol/g) ?? []).toHaveLength(1);
  });
});

describe("math", () => {
  it("typesets a CLOSED block formula", () => {
    // The control for every `not.toContain("katex")` below. Without it, those
    // pass on a build where math is not wired at all — which is exactly what
    // this suite measured before the plugin was installed.
    const html = render("$$\na^2 + b^2 = c^2\n$$");

    expect(html).toContain("katex");
  });

  it("typesets inline math written with $$", () => {
    const html = render("complexity is $$O(n \\log n)$$ here");

    expect(html).toContain("katex");
  });

  it("leaves a LONE dollar alone, because a shell transcript is full of them", () => {
    // `singleDollarTextMath` stays false on purpose. Turning it on is a one-word
    // edit that looks like an improvement and silently typesets the text between
    // any two lone dollars — and this transcript carries `$PATH` and `$50` all
    // day. With the default, both lines below stay literal.
    const shell = render("run `echo $PATH` then set $HOME");
    const price = render("it costs $50 or $80 per seat");

    expect(shell).not.toContain("katex");
    expect(price).not.toContain("katex");
    expect(price).toContain("$50");
  });

  it("leaves an UNTERMINATED formula as literal text", () => {
    // The rendered consequence of `maskIncompleteMath`, asserted where the
    // parser exists to prove it. Without the mask this FAILS: streamdown's
    // completion typesets the prefix as a finished `O(n log`, a different
    // expression from the one being written.
    const html = render("complexity is $$O(n \\log");

    expect(html).not.toContain("katex");
    expect(html).toContain("O(n");
  });

  it("still shows the delimiter the model actually emitted", () => {
    // Masking ESCAPES rather than deletes: the honest mid-stream state is the
    // characters that have arrived. Hiding them would make the formula appear
    // out of nowhere when it closes.
    const html = render("complexity is $$O(n");

    expect(html).toContain("$$O(n");
  });

  it("does not mask a $$ that is shell syntax inside a fence", () => {
    // The mask counts delimiters; a fenced `$$` is a PID. Rewriting inside a
    // fence would put a stray backslash into a command the user copies.
    const html = render("```sh\necho $$\n```");

    expect(html).toContain("echo $$");
    expect(html).not.toContain("\\$\\$");
  });
});

describe("code", () => {
  it("renders a closed fence through the shared PrettyCode", () => {
    // The kit's block, not streamdown's: its `data-slot` is the contract, the
    // header carries the fence's language as a readable label, and Prism's
    // tokens arrive as inline `color:` (not shiki's custom properties).
    const html = render("```ts\nconst x: number = 1;\n```");

    expect(html).toContain('data-slot="pretty-code"');
    expect(html).toContain("TypeScript");
    expect(html).toContain("color:");
    expect(html).toContain("const");
    expect(html).not.toContain('data-streamdown="code-block"');
  });

  it("carries the source verbatim, with no closing blank row", () => {
    const html = render("```sh\necho $$\n```");

    expect(html).toContain("echo");
    expect(html).toContain("$$");
    // One <div> per line of code, and the fence's trailing newline is not one.
    expect(html.match(/class="token-line"/g)).toHaveLength(1);
  });

  it("does not throw on an unterminated fence", () => {
    expect(() => render("```ts\nconst x = 1;")).not.toThrow();
  });

  it("draws an open fence that has no body yet as a block, not as an empty listing", () => {
    const html = render("text\n\n```ts\n");

    expect(html).toContain('data-slot="pretty-code"');
    expect(html).not.toContain("No content available");
  });

  it("survives a fence with an unknown language and one with none", () => {
    expect(render("```klingon\nnuqneH\n```")).toContain("Klingon");
    expect(render("```\nplain\n```")).toContain("plain");
  });

  it("keeps inline code inline", () => {
    const html = render("call `foo()` now");

    expect(html).toContain('data-streamdown="inline-code"');
    expect(html).not.toContain('data-slot="pretty-code"');
  });
});

describe("mermaid", () => {
  it("routes a mermaid fence to the diagram branch, not to a code block", () => {
    // The inverse of what this suite asserted while mermaid was out. It stays
    // for the same reason it was written: the routing is a DECISION, and this
    // is what fails if a dependency bump or a plugin-list edit undoes it.
    //
    // Asserted on the element the fence became, not on `<svg>`. Streamdown
    // draws the diagram from an async effect inside `Suspense`, so static
    // markup shows the skeleton no matter how the render would end — and the
    // code block's own copy icons are SVGs, so `toContain("<svg")` cannot tell
    // the two branches apart in either direction. The DOM rung below owns the
    // question of whether a picture actually arrives.
    const html = render("```mermaid\ngraph TD;\nA-->B;\n```");

    expect(html).not.toContain('data-slot="pretty-code"');
    expect(html).not.toContain('data-language="mermaid"');
  });

  it("still renders a NON-mermaid fence as a code block", () => {
    // The control. Without it the assertions above also pass on a build where
    // the code override fell out entirely, or where every fence renders a
    // skeleton — neither of which is the thing being pinned.
    const html = render("```ts\nconst x = 1;\n```");

    expect(html).toContain('data-slot="pretty-code"');
  });
});

describe("half-arrived input does not throw", () => {
  // Each is a real mid-stream state. A renderer that throws here takes the whole
  // transcript row down, which is the failure this dependency exists to prevent.
  const partials = [
    ["an unterminated inline code span", "call `foo("],
    ["an unterminated bold run", "this is **important"],
    ["a half-written link", "see [the docs]("],
    ["a table with no body yet", "| a | b |\n|---|"],
    ["an unterminated block formula", "$$\n\\sum_{i=0}^{n}"],
    ["a lone backslash at the end", "a \\"],
    ["a half-written heading", "#"],
    ["nothing at all", ""],
  ] as const;

  for (const [name, markdown] of partials) {
    it(`survives ${name}`, () => {
      expect(() => render(markdown)).not.toThrow();
    });
  }
});

describe("a bare URL is still a link", () => {
  // An agent citing documentation often writes the address as plain text
  // ("Install options: https://docs.example.com/cli/install#macos") rather than
  // as markdown link syntax, and that text has to stay clickable.
  //
  // Two independent things have to hold, and each failed once.
  //
  // GFM autolinking makes the text a link at all, and it survives only because
  // `plugins` and `remarkPlugins` are different props: the defaults of the
  // second carry gfm, and passing the first does not replace them.
  //
  // `href` is the second: an enabled `linkSafety` renders a `<button>` with no
  // href, which still carries `data-streamdown="link"` — so asserting the
  // marker alone passes on a link nothing can open.
  it("autolinks an address written as plain text", () => {
    const html = render("Install options: https://docs.example.com/cli/install#macos-and-linux");

    expect(html).toContain("<a ");
    expect(html).toContain('href="https://docs.example.com/cli/install#macos-and-linux"');
  });

  it("keeps an explicit markdown link, the shape the docs tool hands over", () => {
    const html = render("[Install the CLI](https://docs.example.com/cli/install#macos-and-linux)");

    expect(html).toContain("<a ");
    expect(html).toContain('href="https://docs.example.com/cli/install#macos-and-linux"');
    expect(html).toContain("Install the CLI");
  });

  it("opens in a new tab without handing the opener over", () => {
    // Leaving linkSafety on renders a <button> with no href at all, so these
    // attributes are also the control that it is still off.
    const html = render("https://docs.example.com/cli/install");

    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
  });

  it("still refuses a scheme the protocol gate rejects", () => {
    // The reason a domain allowlist is unnecessary: the class of threat is the
    // SCHEME, and that gate is untouched by disabling the modal.
    const html = render("[click](javascript:alert(1))");

    // The scheme survives as inert TEXT — harden renders `click [blocked]` with
    // the rejected URL in a `title` for the reader. What must not exist is an
    // href that a click could follow.
    expect(html).not.toContain('href="javascript:');
    expect(html).toContain("[blocked]");
  });
});

describe("the control", () => {
  it("renders real content, so the not.toContain assertions are not reading an empty string", () => {
    const html = render("# Title\n\nA paragraph with **bold** text.\n");

    expect(html).toContain("Title");
    expect(html).toContain('data-streamdown="strong"');
    expect(html.length).toBeGreaterThan(40);
  });
});

describe("links in a reply", () => {
  const NOTION =
    "https://app.notion.com/p/bridgetowncompanies/352004e89e0a80cb8a1fc1e3a7a96d4f?source=copy_link&p=1a2b3c&pm=s";

  it("draws a bare address short, with the whole address as href and title", () => {
    const html = render(`open ${NOTION} now`);
    expect(html).toContain('class="chat-chip chat-link-chip');
    expect(html).toContain(`href="${NOTION.replace(/&/g, "&amp;")}"`);
    expect(html).toContain(`title="${NOTION.replace(/&/g, "&amp;")}"`);
    expect(html).toContain("app.notion.com/");
    expect(html).not.toContain(">https://app.notion.com");
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
  });

  it("keeps the author's label and adds the copy control", () => {
    const html = render("[the docs](https://example.com/a)");
    expect(html).toContain("the docs");
    expect(html).toContain('class="chat-link');
    expect(html).toContain("chat-link-copy");
  });

  it("does not make an anchor of a script or app scheme", () => {
    const html = render("[x](javascript:alert(1)) [y](data:text/html,hi)");
    expect(html).not.toContain("<a ");
    expect(html).not.toContain("href=");
  });
});
