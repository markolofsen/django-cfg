/**
 * Find the nearest ancestor that actually scrolls vertically, or
 * ``window`` when none exists. Handles the common embed scenarios:
 *
 * - Standalone page: nothing in the chain scrolls → caller scrolls
 *   ``window`` and listens to ``window.scroll``.
 * - Dev playground / modal shell: an intermediate ``overflow-auto``
 *   container scrolls → caller scrolls that element and listens to
 *   *its* ``scroll`` events (which do NOT bubble to window).
 *
 * A "scrollable" ancestor is one whose computed ``overflow-y`` is
 * ``auto`` or ``scroll`` AND whose content actually overflows. We bail
 * before ``document.body`` — ``documentElement`` is represented by
 * ``window`` in the caller's hot path, so returning the body itself
 * would double-count the scroll surface.
 */
export type ScrollTarget = HTMLElement | Window;

export function getScrollParent(el: HTMLElement | null): ScrollTarget {
    if (typeof window === 'undefined') return (null as unknown) as Window;
    if (!el) return window;

    let cur: HTMLElement | null = el.parentElement;
    while (cur && cur !== document.body && cur !== document.documentElement) {
        const style = getComputedStyle(cur);
        const overflowY = style.overflowY;
        const canScroll =
            (overflowY === 'auto' || overflowY === 'scroll' || overflowY === 'overlay') &&
            cur.scrollHeight > cur.clientHeight;
        if (canScroll) return cur;
        cur = cur.parentElement;
    }
    return window;
}

/** Top-relative scroll position of the target. */
export function getScrollTop(target: ScrollTarget): number {
    return target === window ? window.scrollY : (target as HTMLElement).scrollTop;
}

/** Visible viewport height of the target. */
export function getViewportHeight(target: ScrollTarget): number {
    return target === window ? window.innerHeight : (target as HTMLElement).clientHeight;
}

/** Y coordinate of the target's top edge, in viewport space. Used to
 *  translate ``getBoundingClientRect().top`` into target-relative
 *  coordinates. For ``window`` this is always ``0``. */
export function getTargetTop(target: ScrollTarget): number {
    return target === window ? 0 : (target as HTMLElement).getBoundingClientRect().top;
}

/** Scroll the target so that the given absolute Y lands at its top.
 *
 *  For ``window`` we ask the browser to animate smoothly — every engine
 *  honours that path. Nested ``overflow-auto`` elements are a different
 *  story: some layouts (e.g. dev-playground shells with flex parents)
 *  silently drop the animation, leaving the user stuck. Direct
 *  ``scrollTop`` writes always work, so we use them there — loss of
 *  animation beats broken navigation. Consumers who want animated
 *  scrolling inside a custom shell can wrap this function themselves. */
export function scrollTargetTo(target: ScrollTarget, top: number) {
    if (target === window) {
        window.scrollTo({ top, behavior: 'smooth' });
        return;
    }
    (target as HTMLElement).scrollTop = top;
}
