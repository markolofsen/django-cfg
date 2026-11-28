import type { ComponentProps, ReactNode } from "react";

import { isBareUrlLink, safeHref } from "../core/links";
import { ChatLink } from "./chat-link";

/** The text of an anchor's children when they are a lone string. */
function loneText(children: ReactNode): string | undefined {
  if (typeof children === "string") return children;
  if (Array.isArray(children) && children.length === 1 && typeof children[0] === "string") return children[0];
  return undefined;
}

/**
 * The markdown renderer's `a`: every link in a reply, and every link a user
 * typed in the cabinet's bubble.
 *
 * Only `http`, `https` and `mailto` become links (`safeHref`); any other href,
 * including an app scheme the host did not claim with its own `components.a`,
 * is its label as plain text. A bare address is drawn short, a labelled one
 * keeps its label.
 */
export function ChatAnchor({ href, children, node: _node, ...rest }: ComponentProps<"a"> & { node?: unknown }) {
  const safe = safeHref(href);
  if (safe === undefined) return <span>{children}</span>;
  const bare = isBareUrlLink(href, loneText(children));
  return (
    <ChatLink href={safe} data-streamdown="link" {...rest}>
      {bare ? undefined : children}
    </ChatLink>
  );
}
