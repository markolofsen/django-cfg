'use client';

import { useDeviceDetect } from './useDeviceDetect';

export interface TouchSafeStyleOptions {
  /**
   * Target iOS specifically (default: true)
   *
   * When enabled, returns font-size only for iOS devices.
   * Android and other platforms return undefined.
   */
  ios?: boolean;

  /**
   * Target all mobile devices (default: false)
   *
   * When enabled, returns font-size for all mobile devices,
   * not just iOS. Overrides `ios` option.
   */
  mobile?: boolean;

  /**
   * Minimum font size to prevent zoom (default: '16px')
   *
   * iOS WebKit zooms when font-size < 16px, but you can set
   * a higher threshold if needed (e.g., '18px').
   */
  minSize?: string;
}

/**
 * Returns touch-safe font-size style for iOS WebKit auto-zoom prevention.
 *
 * **Problem**: iOS Safari/Chrome zooms viewport when font-size < 16px on input focus,
 * causing UI elements to "fly away" (especially critical in chat/conversation interfaces).
 *
 * **Solution**: Use max(16px, 1em) to maintain relative sizing while preventing zoom.
 *
 * **WCAG Compliance**: ✅ WCAG 2.1 AA compliant (SC 1.4.4, 1.4.10)
 * - Text zoom still works (no viewport user-scalable=no)
 * - No reflow issues
 * - Maintains 200% text zoom capability
 *
 * **Default Behavior**: iOS-only targeting (Android keeps optimal font-size)
 *
 * @param options - Configuration options
 * @returns Font-size CSS value string or undefined if not applicable
 *
 * @example
 * ```tsx
 * // iOS-only (default) — Android keeps 14px, iOS gets 16px
 * function ChatInput() {
 *   const fontSize = useTouchSafeStyle();
 *   return <textarea style={{ fontSize }} placeholder="Type a message..." />;
 * }
 * ```
 *
 * @example
 * ```tsx
 * // All mobile devices
 * const fontSize = useTouchSafeStyle({ mobile: true, ios: false });
 * ```
 *
 * @example
 * ```tsx
 * // Custom minimum size
 * const fontSize = useTouchSafeStyle({ minSize: '18px' });
 * ```
 *
 * @example
 * ```tsx
 * // Conditional application
 * function SearchInput() {
 *   const fontSize = useTouchSafeStyle();
 *
 *   return (
 *     <input
 *       type="search"
 *       style={{
 *         fontSize: fontSize || '14px', // Fallback for desktop
 *       }}
 *     />
 *   );
 * }
 * ```
 *
 * @see {@link https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/AdjustingtheTextSize/AdjustingtheTextSize.html}
 * @see {@link @dev/research/ios-webkit-auto-zoom} Research documentation
 * @see {@link ../../styles/css/utilities/touch-safe.css} CSS utilities
 */
export function useTouchSafeStyle(options: TouchSafeStyleOptions = {}): string | undefined {
  const { isIOS, isMobile } = useDeviceDetect();

  const minSize = options.minSize || '16px';

  // Default: iOS-only targeting
  const targetIOS = options.ios !== false;
  const targetMobile = options.mobile === true;

  // Mobile override (all mobile devices)
  if (targetMobile && isMobile) {
    return `max(${minSize}, 1em)`;
  }

  // iOS-specific targeting (default)
  if (targetIOS && isIOS) {
    return `max(${minSize}, 1em)`;
  }

  // Desktop or non-targeted mobile (Android when ios: true)
  return undefined;
}
