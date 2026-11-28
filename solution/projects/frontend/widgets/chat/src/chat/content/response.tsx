import { math } from "@streamdown/math";
import { DiagramSource, diagramPlugin } from "@djangocfg/widget-media/diagram";
import { memo, useMemo, type ComponentProps } from "react";
import { harden } from "rehype-harden";
import { Streamdown } from "streamdown";

import { maskIncompleteMath } from "../core/conversation/incomplete-math";
import { mentionScheme } from "../core/links";
import { safeImageUrl, ZoomableImage } from "./zoomable-image";
import { ChatAnchor } from "./anchor";
import { ChatCode } from "./code-block";

/**
 * The ONE place a model's markdown becomes DOM.
 *
 * Everything below is a decision that was measured rather than assumed, because
 * each one is invisible when wrong: a half-arrived fence that throws takes the
 * transcript row down, and a formula typeset from a prefix renders a DIFFERENT
 * expression than the one being written.
 *
 * ## Why the whole string is one block
 *
 * `parseMarkdownIntoBlocksFn={(s) => [s]}` disables streamdown's own splitting.
 * Splitting on blank lines is what breaks reference definitions — `see [x][1]`
 * and `[1]: https://…` land in different parses, so the link never resolves and
 * the reader sees a literal `[1]`. Our previous splitter had the same defect
 * plus a second one (loose ordered lists renumbering from 1), and both follow
 * from splitting AT ALL, not from how it was done.
 *
 * The cost is real and accepted: a token now re-renders the whole message
 * instead of its last block. `memo` below keeps that to the one message that
 * changed, and a message is bounded — a transcript is not.
 *
 * ## Why these plugins, and why code is not one
 *
 * streamdown's core carries no math, no highlighting, no diagrams; each is an
 * opt-in package — streamdown does NOT drag KaTeX in on its own.
 *
 * - `math` (katex, ~1 dep tree) — IN. Agent answers carry complexity bounds and
 *   formulas; rendering them as `$O(n \log n)$` is a worse answer.
 * - code — IN, but NOT as a plugin. A transcript of an agent that edits files is
 *   mostly code, and it is the kit's `PrettyCode` (Prism, header, copy button,
 *   theme tokens) wired as the `code` element override in `./code-block`: the
 *   same block every other code surface mounts. `@streamdown/code` (shiki)
 *   would have been a second highlighter with its own theme and its own chrome
 *   beside every other code block in the host.
 * - `mermaid` — IN, on OUR renderer rather than the upstream plugin. The cost
 *   objection stands against `@streamdown/mermaid`, which pulls an 84 MB
 *   runtime needing a DOM; `@djangocfg/widget-media` draws the same diagrams from a
 *   2.5 MB parser needing none. The `show_media` tool declares `mermaid` among
 *   its kinds, so diagrams are produced whether or not this renders them — the
 *   alternative was not "no diagrams", it was a code block where one belongs.
 * - `cjk` — OUT until a CJK locale ships. Its job is strikethrough/emphasis
 *   boundaries in CJK text; nothing today reads those.
 *
 * ## Inline math needs `$$`, and that default is KEPT
 *
 * `@streamdown/math` ships `singleDollarTextMath: false`. That reads like a
 * missing feature and is not: a transcript from an agent that runs shells and
 * quotes prices is FULL of lone dollars — `$PATH`, `$HOME`, `$50/month`, `cd
 * $DIR` — and enabling single-dollar math turns the text between any two of
 * them into a formula. The failure is silent and it corrupts the answer, which
 * is strictly worse than `$x$` staying literal.
 *
 * So inline math is written `$$E = mc^2$$` and block math is a fenced `$$` on
 * its own lines. Pinned by a test, because "turn it on" is a one-word edit that
 * looks like an improvement.
 *
 * ## KaTeX needs its stylesheet
 *
 * The plugin emits `<span class="katex">`; without `katex/dist/katex.min.css`
 * that renders as unstyled fallback glyphs. `math.getStyles()` returns the path
 * — the HOST imports it, because this package ships no CSS of its own.
 *
 * ## Completion stays ON, and math is exempted from it
 *
 * streamdown completes half-arrived markdown, which is what makes a bold run
 * style itself as it is typed. For math that same behaviour typesets a PREFIX —
 * `$$O(n \log` renders a finished-looking `O(n log` that becomes a different
 * formula on the next token:
 *
 * | unclosed | completion on | off |
 * |---|---|---|
 * | `**important` | bold | plain |
 * | `` `foo( `` | code | plain |
 * | `[docs](` | link | plain |
 * | `$$O(n \log` | KATEX ← the defect | plain |
 *
 * `parseIncompleteMarkdown: false` fixes the last row by breaking the other
 * three, so the flag stays on and the one harmful case is neutralised on the
 * INPUT by `maskIncompleteMath` — see `core/conversation/incomplete-math.ts`.
 */

const PLUGINS = { math, mermaid: diagramPlugin };

/**
 * What a fenced diagram shows before it can be drawn.
 *
 * Streamdown recomputes the mermaid branch on every token and does NOT pass it
 * the `isIncomplete` flag it hands the code-block branch, so a diagram arriving
 * a token at a time reaches the renderer dozens of times unfinished. The plugin
 * rejects those, and this is what a rejection looks like: the source, not
 * streamdown's default red error box, which would otherwise flash through the
 * whole of a streamed diagram before the picture replaced it.
 */
const MERMAID_OPTIONS = { errorComponent: DiagramSource } as const;

/**
 * Link hardening, re-declared so an app scheme survives it.
 *
 * The renderer hardens links through `rehype-harden`, whose `allowedProtocols`
 * defaults to EMPTY. A scheme it does not recognise loses its `href` and the
 * anchor is replaced by grey text reading `<label> [blocked]`, carrying
 * `title="Blocked URL: undefined"`. Correct for `javascript:`; wrong for an app
 * scheme the HOST assigns meaning to — a `<scheme>://user/<id>` mention
 * rendered as `name [blocked]` mid-sentence, which is what shipped.
 *
 * `urlTransform` does NOT fix it: that runs earlier, and harden re-checks the
 * href afterwards. The plugin is the only place the decision is made.
 *
 * Declared here rather than passed by the host because `components` is already
 * the seam for "this href means something to me" — a host that supplies a link
 * renderer must not also have to know that a plugin would strip the href before
 * its renderer ever sees it.
 */
/**
 * Built on FIRST RENDER, not at module load, and cached per scheme.
 *
 * A host configures the scheme at startup, which may run after this module is
 * evaluated. Baking the protocol list in at load time would therefore block
 * every one of that host's own mentions, with `[blocked]` in the transcript as
 * the only symptom.
 */
let cachedScheme: string | undefined;
let cachedPlugins: readonly unknown[] | undefined;

function rehypePlugins(): readonly unknown[] {
  const scheme = mentionScheme();
  if (cachedPlugins === undefined || cachedScheme !== scheme) {
    cachedScheme = scheme;
    cachedPlugins = [
      [
        harden,
        {
          // `*` for prefixes keeps the default reach; the PROTOCOL list is the
          // part that was empty, and it is what blocked the app scheme.
          allowedLinkPrefixes: ["*"],
          allowedImagePrefixes: ["*"],
          allowedProtocols: ["http:", "https:", "mailto:", "tel:", `${scheme}:`],
          allowDataImages: true,
        },
      ],
    ];
  }
  return cachedPlugins;
}

/**
 * Links are anchors, not confirm buttons.
 *
 * `linkSafety` defaults to ON, and an enabled one renders every link as a
 * `<button>` carrying no `href` — clicking opens an "are you sure" modal first.
 * That is built for a chat where a STRANGER writes the link. Here the author is
 * the agent the host put behind this room, and the two threats the modal
 * guards are already answered upstream: a dangerous scheme cannot survive
 * the hardened protocol list, and content the agent did not author is
 * datamarked before it ever reaches a model. What was left was a second click
 * on every citation.
 *
 * Deliberately NOT a domain allowlist of "our" hosts: that is a second source
 * of truth about which addresses are ours, needing an edit for every new one,
 * and it is the same thing `allowedLinkPrefixes: ["*"]` above already declined.
 * The protocol is the class of threat; the domain is not.
 */
const LINK_SAFETY = { enabled: false } as const;

/** One block: see the reference-definition rationale above. */
const wholeString = (source: string) => [source];

export interface ResponseProps {
  /** Markdown, possibly mid-stream. */
  readonly children: string;
  readonly className?: string;
  /**
   * Element overrides, passed through to the markdown renderer.
   *
   * The seam exists for links whose HREF the host owns a meaning for.
   * `[@Dana Reyes](<scheme>://user/<id>)` is a MENTION here, and this
   * package must not learn what a mentionable thing is — so the host overrides `a`,
   * recognises its own scheme, and renders a chip. An unrecognised href falls
   * through to the default anchor.
   *
   * Without it a mention paints as an ordinary link to a scheme no browser can
   * follow: visibly a link, inert on click.
   *
   * MUST be referentially stable — an inline object is a new reference on every
   * render, and the comparator below would then re-parse the markdown of every
   * message on every parent render, which is the cost that comparator exists to
   * avoid.
   */
  readonly components?: ComponentProps<typeof Streamdown>["components"];
}

/**
 * Our anchor is the default `a`; a host's `components.a` wins over it. Merged
 * once per `components` identity, because a new object here would re-parse the
 * message.
 */
/** A markdown `![alt](src)`: the same click-to-enlarge picture as every other image in the chat; an unsafe address leaves the alt text. */
function ChatImage({ src, alt }: { src?: string | Blob; alt?: string }) {
  const safe = typeof src === "string" ? safeImageUrl(src) : null;
  return safe === null ? <span>{alt}</span> : <ZoomableImage src={safe} name={alt ?? ""} className="max-h-96 max-w-full rounded-md object-contain" />;
}

const DEFAULT_COMPONENTS = { a: ChatAnchor, img: ChatImage, code: ChatCode } as unknown as NonNullable<ResponseProps["components"]>;

export const Response = memo(
  ({ children, className, components }: ResponseProps) => {
    const merged = useMemo(
      () => (components === undefined ? DEFAULT_COMPONENTS : { ...DEFAULT_COMPONENTS, ...components }),
      [components],
    );
    return (
      <Streamdown
        className={className}
        parseMarkdownIntoBlocksFn={wholeString}
        plugins={PLUGINS}
        mermaid={MERMAID_OPTIONS}
        components={merged}
        linkSafety={LINK_SAFETY}
        rehypePlugins={rehypePlugins() as never}
      >
        {maskIncompleteMath(children)}
      </Streamdown>
    );
  },
  // Vercel's own comparator, and for the same reason: `Streamdown` is the most
  // expensive node in the transcript, and a parent re-rendering for an unrelated
  // reason (a scroll flag, a new sibling message) must not re-parse markdown.
  (prev, next) =>
    prev.children === next.children &&
    prev.className === next.className &&
    prev.components === next.components,
);

Response.displayName = "Response";
