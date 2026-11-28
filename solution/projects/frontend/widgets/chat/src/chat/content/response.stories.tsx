import type { Meta, StoryObj } from "@storybook/react-vite";
import type { AnchorHTMLAttributes } from "react";

import { Response } from "./response";

/**
 * Model prose — and the half-arrived states that justify the parser.
 *
 * `response.test.tsx` and `markdown.test.tsx` already own the correctness: that
 * an unterminated fence does not throw, that a lone `$` in a shell transcript
 * is left alone, that a reference definition resolves because the string is
 * parsed as ONE block. Nineteen assertions, and they are the right tool — each
 * is a fact about output, checkable without an eye.
 *
 * What they cannot answer is whether a mid-stream frame looks BROKEN. Every
 * story below is a snapshot of markdown that is still arriving: the closing
 * fence has not come, the table has three of five rows, the formula is missing
 * its second `$$`. `streamdown` was adopted for exactly this property, and this
 * is where the property is visible rather than merely asserted.
 */
const meta = {
  title: "Widgets/Chat/Response",
  component: Response,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof Response>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Prose: Story = {
  args: {
    children: [
      "The server serves a committed bundle, not your source.",
      "",
      "That is why editing the frontend changes nothing a browser can see until",
      "`make gen-webui` syncs the embed **and** the process turns over.",
    ].join("\n"),
  },
};

/** Headings, lists and inline code — the ordinary shape of an answer. */
export const StructuredAnswer: Story = {
  args: {
    children: [
      "## What `make ship` does",
      "",
      "1. syncs the embed",
      "2. builds in the order that matters",
      "3. restarts so the running process serves the new bundle",
      "4. verifies by hash",
      "",
      "> Verify by hash, never by the absence of a warning.",
    ].join("\n"),
  },
};

/** A closed fence, highlighted. */
export const CodeBlock: Story = {
  args: {
    children: [
      "Check what is actually being served:",
      "",
      "```bash",
      "curl -s http://127.0.0.1:63141/web-version.txt",
      "```",
    ].join("\n"),
  },
};

/**
 * THE case the parser exists for: the fence has not closed yet.
 *
 * A parser that requires balanced markdown throws here, or — worse — renders
 * the opening ``` as literal text and then re-flows the whole block a token
 * later, which reads as flicker. This must look like code that is still
 * arriving.
 */
export const UnterminatedFence: Story = {
  args: {
    children: ["Here is the fix:", "", "```go", "func (h *Handler) ask(w http.Respons"].join("\n"),
  },
};

/** A table three rows into five. Half a table must still be a table. */
export const PartialTable: Story = {
  args: {
    children: [
      "| Gate | Result |",
      "| --- | --- |",
      "| package tests | 347/347 |",
      "| package types | 0 errors |",
      "| consumer te",
    ].join("\n"),
  },
};

/**
 * An unterminated formula stays literal.
 *
 * The masking is deliberate and narrow: a half-written `$$` must not typeset,
 * because a formula that re-renders on every token is worse than plain text.
 * The delimiter the model actually emitted stays visible — hiding it would make
 * the output disagree with the transcript.
 */
export const UnterminatedMath: Story = {
  args: { children: "The bound is $$\\sum_{i=1}^{n} x_i" },
};

/**
 * A lone `$` is money or a shell prompt, not math.
 *
 * Users paste shell transcripts constantly, and typesetting one of them is the
 * failure mode that made the rule explicit.
 */
export const DollarsInAShellTranscript: Story = {
  args: {
    children: ["```console", "$ echo $HOME", "/Users/mark", "```", "", "It costs $5 per seat."].join(
      "\n",
    ),
  },
};

/**
 * The chip renderer.
 *
 * INFERRED, not annotated against `ResponseProps["components"]`. That type is
 * streamdown's `Components`, whose slots must satisfy a strict anchor signature
 * and a `Record<string, unknown>` index signature at once — no single function
 * type meets both, so annotating it cannot compile. A host's real renderer
 * builds the same object the same way.
 */
const MENTION_COMPONENTS = { a: MentionChipStub };

/**
 * A mention inside an answer, rendered as a chip.
 *
 * This is the OTHER half of `@`-mentions, and it was the half with no story:
 * the composer's menu is what writes the token, but nothing showed what that
 * token becomes once the message is sent and read back.
 *
 * Rendering takes TWO steps, and neither belongs to this package:
 *
 * 1. the host rewrites `@<name>` into `[<name>](app://user/<id>)` BEFORE
 *    parsing — without it the token is an ordinary word and the renderer has no
 *    reason to treat it as anything
 * 2. `components.a` recognises that href and draws the chip
 *
 * `Response` supplies only the seam (`components`). It never learns what a
 * mentionable thing IS: resolving a name to an id needs the live directory,
 * which is the host's, and a chat component that reached for it would couple
 * every consumer to that directory. The stand-in below is deliberately the same
 * SHAPE so this story fails if the seam changes.
 */
export const MentionInAnAnswer: Story = {
  args: {
    children: [
      "I checked with [Dana Reyes](app://user/u-a1b2c3) and the numbers",
      "match. The stale figure came from",
      "[Sam Okafor](app://user/u-77f0e1) instead.",
    ].join("\n"),
    components: MENTION_COMPONENTS,
  },
};

/**
 * A mention the directory cannot answer for stays PLAIN TEXT.
 *
 * The account was deleted, belongs to another workspace, or the directory has
 * not loaded yet. The host's decoder only rewrites a name it resolved, so no
 * link is ever minted and this needs no branch in the renderer — the sentence
 * simply keeps its words.
 *
 * That is the deliberate degradation: a chip that opens nothing is worse than
 * the text it replaced, because it invites a click that lands on a detail screen
 * which fails to load.
 */
export const UnknownMentionStaysText: Story = {
  args: {
    children: "I could not reach @jordan-mills — they left the workspace last week.",
    components: MENTION_COMPONENTS,
  },
};

/**
 * A stand-in for a host's `MentionChip`, so the story shows the CONTRACT
 * rather than importing a feature this package must not depend on.
 *
 * An href it does not recognise falls through to a plain anchor — the rule that
 * keeps ordinary links in a model's answer working.
 */
function MentionChipStub({ href, children }: AnchorHTMLAttributes<HTMLAnchorElement>) {
  if (href === undefined || !href.startsWith("app://user/")) {
    return <a href={href}>{children}</a>;
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-md bg-muted px-1.5 py-0.5 align-baseline font-medium text-foreground text-sm">
      <span aria-hidden>@</span>
      {children}
    </span>
  );
}

/**
 * A diagram the model drew in prose.
 *
 * The fence used to render as a code block — the plugin was declined on the
 * cost of the mermaid runtime, while the `show_media` tool was already
 * declaring `mermaid` among its kinds. The renderer is `beautiful-mermaid`
 * (2.5 MB, no DOM) rather than that runtime, and the block chrome around it —
 * copy, download, fullscreen, pan/zoom — is streamdown's own.
 */
export const Diagram: Story = {
  args: {
    children: [
      "The turn takes three hops:",
      "",
      "```mermaid",
      "graph TD",
      "  A[Browser] --> B[Server]",
      "  B --> C[Agent]",
      "  C --> B",
      "  B --> A",
      "```",
    ].join("\n"),
  },
};

/**
 * The same diagram, still arriving.
 *
 * THE state that justifies the guard. `renderMermaidSVG` does not fail on a
 * half-written diagram — it draws a plausible wrong picture that changes with
 * every token, so a reader would watch it assert three different shapes before
 * settling. Streamdown re-renders the mermaid branch on every token and does
 * not forward the incompleteness flag it computes, so the source shows until
 * the shape closes.
 */
export const DiagramMidStream: Story = {
  args: {
    children: ["Here is the flow:", "", "```mermaid", "graph TD", "  A[Browser] --> "].join("\n"),
  },
};

/**
 * A diagram type the parser does not cover.
 *
 * `pie` is the measured example: flowchart, sequence, state, class and ER are
 * covered, the rest are rejected by header. The fallback shows the SOURCE
 * rather than an error box — an undrawable diagram is still the answer the
 * agent gave, and streamdown's default would paint red text instead.
 */
export const DiagramUnsupportedType: Story = {
  args: {
    children: ["```mermaid", "pie title Votes", '  "Yes" : 70', '  "No" : 30', "```"].join("\n"),
  },
};
