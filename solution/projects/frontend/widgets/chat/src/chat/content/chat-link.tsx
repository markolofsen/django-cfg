import { Check, Copy, Globe } from "lucide-react";
import { useEffect, useRef, useState, type ComponentProps, type ReactNode } from "react";

import { linkHost, linkLabel, opensInNewTab, safeIcon, usableTitle } from "../core/links";
import { useRoomCopy } from "../../i18n";
import { useLinkPreview } from "./link-preview";

export interface ChatLinkProps extends Omit<ComponentProps<"a">, "href" | "children"> {
  /** Already checked with `safeHref`: the caller never passes an unsafe one. */
  href: string;
  /**
   * The author's own label (`[the docs](…)`). Absent for a bare address, which
   * is drawn as a chip with the short form of the url.
   */
  children?: ReactNode;
}

/**
 * A link in a message, in any bubble.
 *
 * - A bare address becomes a chip: the globe, then host and the start and end of
 *   the path (`linkLabel`). The whole address is the `title`, the click target
 *   and what the copy control writes.
 * - A labelled link keeps its label and gets the same behaviour.
 * - Web links open in a new tab with `noopener noreferrer`; a mail link does not.
 * - The copy control sits beside the link, revealed on hover or focus and always
 *   present on touch (see `.chat-link-copy` in markdown.css).
 *
 * The wrapper is `inline-flex` with a width ceiling of its container, so a long
 * chip truncates inside the bubble instead of widening it.
 */
export function ChatLink({ href, children, className, ...rest }: ChatLinkProps) {
  const bare = children === undefined;
  const web = opensInNewTab(href);
  const copy = useRoomCopy();
  const { ref, preview } = useLinkPreview(href, bare);
  const title = usableTitle(preview);
  const icon = preview ? safeIcon(preview.favicon) : undefined;
  return (
    <span className="chat-link-wrap" ref={ref}>
      <a
        {...rest}
        href={href}
        className={
          bare
            ? "chat-chip chat-link-chip inline-flex h-auto min-w-0 gap-1 align-baseline whitespace-nowrap"
            : `chat-link${className ? ` ${className}` : ""}`
        }
        title={rest.title ?? (title ? `${title}\n${href}\n${copy.opensInNewTab}` : href)}
        {...(web ? { target: "_blank", rel: "noopener noreferrer" } : {})}
      >
        {bare ? (
          <>
            <ChipIcon src={icon} />
            {title ? (
              <>
                <span className="chat-link-title truncate">{title}</span>
                <span className="chat-link-host truncate">{linkHost(href)}</span>
              </>
            ) : (
              <span className="truncate">{linkLabel(href)}</span>
            )}
          </>
        ) : (
          children
        )}
      </a>
      <CopyLinkButton href={href} />
    </span>
  );
}

/** The site's own icon when the server sent a usable one; the globe when not, or when the image fails to decode. */
function ChipIcon({ src }: { src: string | undefined }) {
  const [broken, setBroken] = useState(false);
  if (!src || broken) return <Globe aria-hidden />;
  return <img src={src} alt="" aria-hidden onError={() => setBroken(true)} />;
}

function CopyLinkButton({ href }: { href: string }) {
  const copy = useRoomCopy();
  const [done, setDone] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);

  const label = done ? copy.linkCopied : copy.copyLink;
  return (
    <button
      type="button"
      className="chat-link-copy"
      aria-label={label}
      title={label}
      onClick={(event) => {
        event.preventDefault();
        event.stopPropagation();
        void navigator.clipboard?.writeText(href).then(
          () => {
            setDone(true);
            clearTimeout(timer.current);
            timer.current = setTimeout(() => setDone(false), 1500);
          },
          () => undefined,
        );
      }}
    >
      {done ? <Check aria-hidden /> : <Copy aria-hidden />}
    </button>
  );
}
