import { Fragment } from "react";

import { ChatLink } from "../../content/chat-link";
import { findLinks, type TextRange } from "../../core/links";

export interface LinkifiedTextProps {
  readonly text: string;
  /** Ranges of `text` that are something else (an `@` mention): never linked. */
  readonly skip?: readonly TextRange[];
}

/**
 * Plain text with its web links drawn as short, clickable chips.
 *
 * For a person's line, which is text and not markdown. Imports `content/chat-link`
 * directly, not the `content` barrel, so the markdown renderer (Prism, katex)
 * stays out of the first paint.
 */
export function LinkifiedText({ text, skip }: LinkifiedTextProps) {
  const links = findLinks(text, skip);
  if (links.length === 0) return <>{text}</>;
  const nodes: React.ReactNode[] = [];
  let at = 0;
  for (const link of links) {
    if (link.start > at) nodes.push(text.slice(at, link.start));
    nodes.push(<ChatLink key={link.start} href={link.href} />);
    at = link.end;
  }
  if (at < text.length) nodes.push(text.slice(at));
  return (
    <>
      {nodes.map((node, i) => (
        <Fragment key={i}>{node}</Fragment>
      ))}
    </>
  );
}
