/**
 * Wait until an element is actually visible in the viewport.
 *
 * The highlight overlay scrolls an off-screen target into view before
 * drawing its spotlight — but `scrollIntoView({ behavior: 'smooth' })`
 * settles asynchronously, so measuring the rect right after the call
 * yields a stale (mid-scroll or still off-screen) position. This waits
 * for the browser to confirm the element is on screen.
 */

/**
 * Is the element within the viewport right now, by geometry alone?
 *
 * The fallback for when no observer callback arrives. Coarser than
 * IntersectionObserver — it cannot see an element covered by another — but it
 * answers the question that matters here: does this occupy space on screen.
 */
function isOnScreen(element: Element, threshold: number): boolean {
  const rect = element.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) return false;

  const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;

  const visibleWidth = Math.min(rect.right, viewportWidth) - Math.max(rect.left, 0);
  const visibleHeight = Math.min(rect.bottom, viewportHeight) - Math.max(rect.top, 0);
  if (visibleWidth <= 0 || visibleHeight <= 0) return false;

  return (visibleWidth * visibleHeight) / (rect.width * rect.height) >= threshold;
}

/** Options for {@link waitForVisible}. */
export interface WaitForVisibleOptions {
  /**
   * Fraction of the element that must be inside the viewport before it
   * counts as visible (IntersectionObserver threshold).
   */
  threshold?: number;
  /**
   * Safety cap (ms). If the element never reaches the threshold — e.g.
   * it is larger than the viewport, or hidden — the promise resolves
   * anyway so the overlay never hangs. Fail soft.
   */
  timeoutMs?: number;
}

/**
 * Resolve once `element` is at least `threshold` visible in the
 * viewport, or once `timeoutMs` elapses — whichever comes first.
 *
 * Always resolves (never rejects): a never-intersecting element must
 * not stall the overlay. The boolean result reports whether the
 * element became visible (`true`) or the timeout fired (`false`), for
 * callers that want to log it.
 */
export function waitForVisible(
  element: Element,
  { threshold = 0.5, timeoutMs = 800 }: WaitForVisibleOptions = {}
): Promise<boolean> {
  return new Promise((resolve) => {
    // No IntersectionObserver — measure instead of declaring it hidden.
    if (typeof IntersectionObserver === "undefined") {
      resolve(isOnScreen(element, threshold));
      return;
    }

    let settled = false;
    const finish = (visible: boolean) => {
      if (settled) return;
      settled = true;
      window.clearTimeout(timer);
      observer.disconnect();
      resolve(visible);
    };

    // On timeout, MEASURE rather than assume. An observer that never fires is
    // not evidence the element is hidden: a throttled or unpainted frame — a
    // background tab, an embedded preview — delivers no callback at all, and
    // an approved action would then fail on an element plainly on screen.
    const timer = window.setTimeout(() => finish(isOnScreen(element, threshold)), timeoutMs);
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting && entry.intersectionRatio >= threshold) {
            finish(true);
            return;
          }
        }
      },
      { threshold }
    );
    observer.observe(element);
  });
}
