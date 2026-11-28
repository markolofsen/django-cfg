import { useEffect, useRef } from "react";

import { registerLayer } from "./layer-registry";

export interface UseLayerOptions {
  /** Back closes the layer (a history entry per open layer). Default true. */
  readonly back?: boolean;
  /** Make the page behind inert while open. Default true. */
  readonly inert?: boolean;
  /**
   * The page's root, when the host can name it; absent, every direct child of `<body>` that does not
   * contain `layer` is made inert. A selector, an element, or a function returning elements.
   */
  readonly appRoot?: string | Element | (() => Iterable<Element>);
  /** Lock page scroll without shifting the layout while open. Default true. */
  readonly lockScroll?: boolean;
  /** The layer's own element. It, and anything holding it, is never made inert. */
  readonly layer?: () => Element | null;
}

let open = 0;
const inerted = new Map<Element, boolean>();
let saved: { html: string; body: string; gutter: string } | null = null;

/**
 * Never inert: scripts, the dialog's own portal (it is mounted a tick after the effect runs, so the layer ref can
 * still be empty), focus guards, and toast regions the reader must still be able to dismiss.
 */
function isLayerHost(el: Element): boolean {
  return (
    el.tagName === "SCRIPT" ||
    el.hasAttribute("data-radix-portal") ||
    el.hasAttribute("data-radix-focus-guard") ||
    el.hasAttribute("data-sonner-toaster") ||
    el.matches('[role="dialog"], [aria-modal="true"]') ||
    el.querySelector('[role="dialog"][data-state="open"], [aria-modal="true"]') !== null
  );
}

function targets(options: UseLayerOptions): Element[] {
  const layer = options.layer?.() ?? null;
  const root = options.appRoot;
  let list: Element[];
  if (typeof root === "function") list = [...root()];
  else if (root instanceof Element) list = [root];
  else if (typeof root === "string") list = [...document.querySelectorAll(root)];
  else {
    const marked = [...document.querySelectorAll("[data-app-root]")];
    list = marked.length > 0 ? marked : [...document.body.children];
  }
  return list.filter((el) => !(layer && (el === layer || el.contains(layer))) && !isLayerHost(el));
}

/**
 * No layout shift on lock: `overflow: hidden` on `<html>` removes a desktop scrollbar, so its width is replaced by
 * padding; on a phone the scrollbar overlays and nothing moves. The body is never `position: fixed` (that resets the
 * scroll position and jumps the page on close).
 */
function lock(on: boolean, options: UseLayerOptions) {
  const html = document.documentElement;
  if (on) {
    if (open === 0) {
      saved = { html: html.style.overflow, body: document.body.style.paddingRight, gutter: html.style.overscrollBehaviorY };
      if (options.lockScroll !== false) {
        const bar = window.innerWidth - html.clientWidth;
        html.style.overflow = "hidden";
        if (bar > 0) document.body.style.paddingRight = `${bar}px`;
      }
      html.style.overscrollBehaviorY = "contain";
    }
    open += 1;
    if (options.inert !== false) {
      for (const el of targets(options)) {
        if (!inerted.has(el)) inerted.set(el, el.hasAttribute("inert"));
        el.setAttribute("inert", "");
      }
    }
    return;
  }
  open -= 1;
  if (open > 0) return;
  for (const [el, was] of inerted) if (!was) el.removeAttribute("inert");
  inerted.clear();
  if (saved) {
    html.style.overflow = saved.html;
    document.body.style.paddingRight = saved.body;
    html.style.overscrollBehaviorY = saved.gutter;
    saved = null;
  }
}

/**
 * What an open full-screen layer needs besides the dialog itself: the page behind inert (no focus, no taps, no screen
 * reader, no keyboard accessory fields), page scroll locked without a shift, no pull-to-refresh behind it, and the
 * phone's Back closing it. Escape is the dialog's own.
 */
export function useLayer(isOpen: boolean, close: () => void, options: UseLayerOptions = {}): void {
  const id = useRef(`layer-${Math.random().toString(36).slice(2)}`);
  const closeRef = useRef(close);
  closeRef.current = close;
  const optionsRef = useRef(options);
  optionsRef.current = options;
  useEffect(() => {
    if (!isOpen) return;
    const opts = optionsRef.current;
    lock(true, opts);
    const release = opts.back === false ? () => {} : registerLayer(id.current, () => closeRef.current());
    return () => {
      release();
      lock(false, opts);
    };
  }, [isOpen]);
}
