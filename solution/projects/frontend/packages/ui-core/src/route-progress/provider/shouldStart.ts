import type { RouteProgressContextValue } from './context';

/**
 * Whether a navigation from `from` to `to` shows the bar. In order:
 * the call's explicit option; the app switch; a mounted page that said `progress: false`;
 * the app's `shouldShow`; the default, "the pathname changes" (query and hash do not).
 */
export function shouldStartProgress(
  ctx: RouteProgressContextValue | null,
  from: URL,
  to: URL,
  explicit?: boolean,
): boolean {
  if (!ctx || !ctx.enabled) return false;
  if (explicit !== undefined) return explicit;
  if (ctx.behavior.get().progress === false) return false;
  if (ctx.shouldShow) return ctx.shouldShow(from, to);
  return from.pathname !== to.pathname;
}
