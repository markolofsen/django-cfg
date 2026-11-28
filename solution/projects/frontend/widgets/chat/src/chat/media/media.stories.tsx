import type { Meta, StoryObj } from "@storybook/react-vite";

import { renderMediaContent } from "../content";
import { readMediaBlock, type MediaBlock } from "../core";
import { MediaWidget } from "./media";

/**
 * The media registry: one wire event, eleven kinds.
 *
 * A registry rather than eleven props — a twelfth kind adds an entry and a
 * renderer, never a prop on `<Chat>`. The kind list mirrors the server's kind
 * vocabulary, so the discriminant has one owner on each side rather than being
 * re-spelled inside every renderer.
 *
 * Two stories below are about REFUSAL, and they matter more than the happy
 * paths: a media block carries a model-authored URL, which is untrusted input
 * arriving inside a trusted-looking frame.
 */
const meta = {
  title: "Widgets/Chat/Media",
  component: MediaWidget,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof MediaWidget>;

export default meta;
type Story = StoryObj<typeof meta>;

// Same-origin prefixes the host allows. Real shape, not a placeholder: the
// gate treats a bare "/" path as same-origin only against this list.
const PREFIXES = ["/api/media/"] as const;

// A 1×1 transparent PNG. Inline so the story renders with no network at all —
// a story that depends on a remote asset fails for reasons unrelated to itself.
const PIXEL =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";

export const Image: Story = {
  args: {
    block: { kind: "image", src: PIXEL, alt: "A screenshot of the server log" },
  },
};

/**
 * A generated image AFTER the server content-addresses it.
 *
 * The two image stories are one lifecycle, not two variants: a generation
 * arrives inline (above) and is stored as an attachment path (here), so a
 * reload renders this shape and never the payload. Both must render
 * identically — the src spelling is the only difference, and a renderer that
 * handled only one of them shipped a picture that vanished on reload.
 */
export const ImageFromAnAttachment: Story = {
  args: {
    block: {
      kind: "image",
      src: "/api/media/0b880a46dbfc669f15e661c1db46385c8d1507da93f7b815c9797c9bc00086cf",
      alt: "A generated image served from the attachment store",
    },
  },
};

/** Several images at once — the gallery is its own kind, not a repeated image. */
export const Gallery: Story = {
  args: {
    block: {
      kind: "gallery",
      items: [
        { src: PIXEL, alt: "Before" },
        { src: PIXEL, alt: "After" },
      ],
    },
  },
};

/**
 * A textual kind with no host renderer supplied.
 *
 * `json`, `code`, `markdown`, `text` and `mermaid` are routed to the CONTENT
 * renderer when the host registers one — that is the seam where `widgets/` and
 * `content/` meet. With none, the fallback is plain, which is a legitimate
 * configuration: a host that renders a read-only transcript should not have to
 * pay for a syntax highlighter to see its text.
 */
export const CodeWithoutAHostRenderer: Story = {
  args: {
    block: {
      kind: "code",
      language: "go",
      content: 'func main() {\n\tlog.Println("server up")\n}',
    },
  },
};

/** A link with its unfurl already resolved — the widget never fetches. */
export const Link: Story = {
  args: {
    block: {
      kind: "link",
      url: "https://example.dev",
      link: { title: "example.dev", description: "The public API tier." },
    },
  },
};

/**
 * REFUSAL: a hostile src never reaches the DOM.
 *
 * The gate lives in the PARSER (`readMediaBlock`), not in the renderer, so this
 * story runs the real chain: a rejected src becomes `undefined` and the widget
 * renders nothing. Putting the check in the component would leave every other
 * entry point unguarded.
 *
 * `javascript:` is the obvious one. A bare `data:` is the subtle one — it
 * allows `text/html`, which is script, so only `data:image/` is permitted.
 */
export const HostileSrcIsRefused: Story = {
  // `args` is required by the typed meta even though `render` ignores it: the
  // story owns its own parsing, because the point IS the parser's verdict.
  args: { block: { kind: "image" } },
  render: () => {
    const hostile = ["javascript:alert(1)", "data:text/html,<script>alert(1)</script>"];
    const parsed = hostile.map((src) => readMediaBlock({ kind: "image", src }, PREFIXES));

    return (
      <div className="grid gap-2">
        {parsed.map((block, index) => (
          <div key={hostile[index]} className="grid gap-1">
            <code className="text-xs opacity-60">{hostile[index]}</code>
            {block === null ? (
              <RefusalNote>Refused: the parser dropped this block entirely.</RefusalNote>
            ) : (
              <MediaWidget block={block} />
            )}
          </div>
        ))}
      </div>
    );
  },
};

/**
 * REFUSAL: a kind this build predates.
 *
 * Not an error. The server's vocabulary grows, and a transcript written by a
 * newer agent may be opened in an older client — the same degrade the server
 * itself applies. Rendering nothing beats guessing at a shape we do not know.
 */
export const UnknownKindRendersNothing: Story = {
  args: { block: { kind: "image" } },
  render: () => {
    const block = readMediaBlock({ kind: "hologram", src: PIXEL }, PREFIXES);

    return block === null ? (
      <RefusalNote>Unknown kind: nothing rendered, and that is the contract.</RefusalNote>
    ) : (
      <MediaWidget block={block as MediaBlock} />
    );
  },
};

/**
 * A diagram the agent produced through the tool, with the renderer wired.
 *
 * The pair to `CodeWithoutAHostRenderer` above, and the reason this story
 * exists: `renderContent` was declared, called, and supplied by NOBODY, so
 * every `show_media` diagram fell to the `<pre>` fallback. Nothing failed —
 * an unsupplied callback and an unsupported kind look identical from inside
 * the widget.
 *
 * The block also arrives on the wire as `chart`, not `content`; the reader
 * translates, and before it did the block was dropped at dispatch and never
 * reached this widget at all.
 */
export const MermaidWithTheContentRenderer: Story = {
  args: {
    block: readMediaBlock(
      {
        kind: "mermaid",
        chart: "graph TD\n  A[Agent] --> B{Tool call}\n  B -->|allowed| C[Run]\n  B -->|denied| D[Explain]",
      },
      PREFIXES,
    ) as MediaBlock,
    renderContent: renderMediaContent,
  },
};

/**
 * A caption naming what the parser refused, for the two refusal stories.
 *
 * Story furniture, not a shipped widget: the point of those stories is the
 * parser's verdict, and the widget under test renders nothing at all when the
 * verdict is "no".
 */
function RefusalNote({ children }: { readonly children: string }) {
  return <p className="text-xs text-muted-foreground">{children}</p>;
}
