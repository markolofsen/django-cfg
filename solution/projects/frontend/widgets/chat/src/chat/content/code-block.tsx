import { PrettyCode } from "@djangocfg/widget-kit/pretty-code";
import { isValidElement, useMemo, type ComponentProps, type ReactNode } from "react";
import { defaultComponents, useIsCodeFenceIncomplete } from "streamdown";

import { useChatCopy } from "../../i18n";

/**
 * A fenced block is the kit's `PrettyCode`, the same component every other
 * code surface in the repo mounts: one highlighter (Prism), one header, one
 * copy button, one theme.
 *
 * It is wired as streamdown's `code` override rather than as a highlighter
 * plugin, because a plugin only recolours tokens inside streamdown's own
 * chrome. This replaces the chrome too.
 *
 * Only the BLOCK is ours. Everything else goes to streamdown's default `code`,
 * which still owns:
 *
 * - inline code (no `data-block`),
 * - the mermaid branch — it is routed inside that default, and the diagram
 *   plugin is only reachable through it. A mermaid fence therefore never
 *   reaches `PrettyCode`.
 *
 * ## Streaming
 *
 * The block is re-rendered with every token. That is safe by construction: an
 * unterminated fence arrives as a block whose text is a prefix, Prism tokenizes
 * any string, an unregistered grammar renders as plain text, and an empty body
 * while the fence is open, or after an empty closed one, is a block that has not
 * started (`pending`), not an "empty listing" line flashing before the first token.
 */

const LANGUAGE = /language-(\S+)/;

/** The source of a fence: streamdown hands it over as a string, or as one element wrapping it. */
function sourceOf(children: ReactNode): string {
  if (typeof children === "string") return children;
  if (isValidElement<{ children?: unknown }>(children) && typeof children.props.children === "string") {
    return children.props.children;
  }
  return "";
}

type CodeProps = ComponentProps<NonNullable<typeof defaultComponents.code>>;

const InlineOrDiagram = defaultComponents.code as NonNullable<typeof defaultComponents.code>;

/** The `code` element override: a fenced block is `PrettyCode`, anything else is streamdown's default. */
export function ChatCode(props: CodeProps) {
  const incomplete = useIsCodeFenceIncomplete();
  const copy = useChatCopy().message;
  const labels = useMemo(() => ({ copyCode: copy.copy }), [copy.copy]);

  const language = LANGUAGE.exec(props.className ?? "")?.[1] ?? "";
  const isBlock = "data-block" in props;
  if (!isBlock || language === "mermaid") return <InlineOrDiagram {...props} />;

  // The fence's closing newline is not a line of code: left in, Prism paints an empty last row and a copy carries it.
  const source = sourceOf(props.children).replace(/\n$/, "");
  // `Response` does not pass `isAnimating`, so streamdown's own flag is false
  // here; an empty body is the one state we can tell for ourselves, and it is
  // the one that matters (the fence line has arrived, the first token has not).
  const pending = incomplete || source.trim() === "";
  return <PrettyCode data={source} language={language || "text"} isCompact pending={pending} labels={labels} />;
}
