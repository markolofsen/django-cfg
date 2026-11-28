/**
 * Resolves the default sidebar open/closed state.
 *
 * Priority:
 *   1. Cookie written by shadcn-sidebar (user's last explicit choice)
 *   2. Viewport width — collapse by default on tablet and below (< 1024px lg)
 *   3. Expanded (large desktop, no cookie)
 *
 * Must run on the client — returns `true` during SSR.
 */

const SIDEBAR_COOKIE_NAME = 'sidebar_state';
const COLLAPSE_BELOW_PX = 1024; // Tailwind lg

export function useSidebarDefaultOpen(): boolean {
  if (typeof document === 'undefined') return true;

  const match = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${SIDEBAR_COOKIE_NAME}=`));

  if (match) {
    return match.split('=')[1] === 'true';
  }

  // No cookie — first visit. Collapse on smaller screens.
  if (typeof window !== 'undefined') {
    return window.innerWidth >= COLLAPSE_BELOW_PX;
  }

  return true;
}
