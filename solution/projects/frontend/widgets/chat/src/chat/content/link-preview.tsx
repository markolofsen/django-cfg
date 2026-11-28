import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { previewable, type LinkPreview, type ResolveLinkPreview } from "../core/links";

/**
 * The host's lookup, handed down to every link chip below it.
 *
 * A context of its own, not the chat's: `content` may not import the store, and a chip drawn outside any chat (a markdown preview) must
 * still render, with no lookup. The `ui` layer fills it from the `links` capability.
 */
const Resolver = createContext<ResolveLinkPreview | undefined>(undefined);

export function LinkPreviewProvider({ resolve, children }: { resolve: ResolveLinkPreview | undefined; children: ReactNode }) {
  return <Resolver.Provider value={resolve}>{children}</Resolver.Provider>;
}

const AT_ONCE = 3;
const KEEP = 400;
/** A failure is forgotten after this, so a limit that has passed is tried again; a found title is kept for the session. */
const FORGET_MISS_MS = 60_000;

interface Entry {
  readonly value: LinkPreview | undefined;
  readonly at: number;
}

const settled = new Map<string, Entry>();
const flying = new Map<string, Promise<LinkPreview | undefined>>();
const waiting: Array<() => void> = [];
let running = 0;

function current(href: string): Entry | undefined {
  const entry = settled.get(href);
  if (entry && entry.value === undefined && Date.now() - entry.at > FORGET_MISS_MS) {
    settled.delete(href);
    return undefined;
  }
  return entry;
}

function pump(): void {
  while (running < AT_ONCE && waiting.length > 0) waiting.shift()?.();
}

/**
 * One lookup per address for the whole page, whoever asks and however often a message re-renders: the answer is remembered by address,
 * a second asker joins the one in flight, and only a few go out at a time so a long history does not spend the server's budget at once.
 */
export function loadLinkPreview(href: string, resolve: ResolveLinkPreview): Promise<LinkPreview | undefined> {
  const known = current(href);
  if (known) return Promise.resolve(known.value);
  const joined = flying.get(href);
  if (joined) return joined;
  const promise = new Promise<LinkPreview | undefined>((done) => {
    waiting.push(() => {
      running += 1;
      resolve(href)
        .catch(() => undefined)
        .then((value) => {
          if (settled.size >= KEEP) settled.delete(settled.keys().next().value as string);
          settled.set(href, { value, at: Date.now() });
          flying.delete(href);
          running -= 1;
          done(value);
          pump();
        });
    });
    pump();
  });
  flying.set(href, promise);
  return promise;
}

/** For tests: forget everything remembered. */
export function resetLinkPreviews(): void {
  settled.clear();
  flying.clear();
  waiting.length = 0;
  running = 0;
}

/**
 * The preview of `href`, once its chip is on screen. `ref` goes on the chip's wrapper: nothing is asked for a link nobody has scrolled to.
 * Without a lookup from the host, for an address that is not https, or while `enabled` is false, it stays `undefined` and asks for nothing.
 */
export function useLinkPreview(href: string, enabled: boolean): { ref: (node: HTMLElement | null) => void; preview: LinkPreview | undefined } {
  const resolve = useContext(Resolver);
  const active = enabled && resolve !== undefined && previewable(href);
  const [preview, setPreview] = useState<LinkPreview | undefined>(() => (active ? current(href)?.value : undefined));
  const [node, setNode] = useState<HTMLElement | null>(null);

  useEffect(() => {
    if (!active || !resolve || !node) return;
    const known = current(href);
    if (known) {
      setPreview(known.value);
      return;
    }
    let live = true;
    const ask = () => void loadLinkPreview(href, resolve).then((value) => live && setPreview(value));
    if (typeof IntersectionObserver === "undefined") {
      ask();
      return () => {
        live = false;
      };
    }
    const watch = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        watch.disconnect();
        ask();
      }
    });
    watch.observe(node);
    return () => {
      live = false;
      watch.disconnect();
    };
  }, [active, href, resolve, node]);

  return { ref: setNode, preview: active ? preview : undefined };
}
