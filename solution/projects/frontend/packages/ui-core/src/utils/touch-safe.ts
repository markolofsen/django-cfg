/**
 * Touch-safe font-size utilities for universal iOS auto-zoom prevention.
 *
 * Provides CSS and JavaScript helpers that automatically protect against
 * iOS WebKit viewport zoom on input focus, without requiring explicit
 * device detection in every component.
 *
 * @see {@link ../styles/css/utilities/touch-safe.css} CSS implementation
 * @see {@link ../hooks/device/useTouchSafeStyle.ts} React hook alternative
 * @see {@link @dev/research/ios-webkit-auto-zoom} Research
 */

/**
 * Returns touch-safe font-size value that works universally.
 *
 * Uses CSS custom property `--touch-safe-font-size` which is automatically
 * set to `max(16px, 1em)` on iOS via @supports detection.
 *
 * **Automatic behavior**:
 * - iOS: `max(16px, 1em)` (prevents auto-zoom)
 * - Android/Desktop: fallback value (design's intended size)
 *
 * @param fallback - Fallback font-size for Android/Desktop (default: '1rem')
 * @returns CSS font-size value string
 *
 * @example Inline style
 * ```tsx
 * import { touchSafeFontSize } from '@djangocfg/ui-core/utils';
 *
 * <input style={{ fontSize: touchSafeFontSize('0.875rem') }} />
 * // iOS: max(16px, 1em)
 * // Android/Desktop: 0.875rem (14px)
 * ```
 *
 * @example CSS-in-JS
 * ```tsx
 * const inputStyles = {
 *   fontSize: touchSafeFontSize('14px'),
 * };
 * ```
 *
 * @example Tailwind arbitrary value
 * ```tsx
 * <input className={`text-[${touchSafeFontSize('14px')}]`} />
 * ```
 */
export function touchSafeFontSize(fallback: string = '1rem'): string {
  return `var(--touch-safe-font-size, ${fallback})`;
}

/**
 * Returns touch-safe style object for inline styles.
 *
 * Convenience wrapper around touchSafeFontSize() that returns
 * a complete style object ready for React inline styles.
 *
 * @param fallback - Fallback font-size for Android/Desktop
 * @returns Style object with fontSize property
 *
 * @example
 * ```tsx
 * import { touchSafeStyle } from '@djangocfg/ui-core/utils';
 *
 * <textarea style={touchSafeStyle('14px')} />
 * // iOS: { fontSize: 'max(16px, 1em)' }
 * // Android/Desktop: { fontSize: '14px' }
 * ```
 *
 * @example Merge with existing styles
 * ```tsx
 * <input
 *   style={{
 *     ...myStyles,
 *     ...touchSafeStyle('0.875rem'),
 *   }}
 * />
 * ```
 */
export function touchSafeStyle(fallback: string = '1rem'): { fontSize: string } {
  return {
    fontSize: touchSafeFontSize(fallback),
  };
}

/**
 * CSS class name for touch-safe inputs (opt-in).
 *
 * Apply to a container to make all child inputs/textareas touch-safe
 * on mobile devices.
 *
 * @example
 * import { TOUCH_SAFE_INPUT_CLASS } from '@djangocfg/ui-core/utils';
 * // className={TOUCH_SAFE_INPUT_CLASS}
 */
export const TOUCH_SAFE_INPUT_CLASS = 'touch-safe-input';

/**
 * CSS class name for mobile touch-safe inputs (iOS + Android).
 *
 * Apply when you want consistent 16px minimum across all mobile
 * platforms, not just iOS.
 *
 * @example
 * import { TOUCH_SAFE_MOBILE_CLASS } from '@djangocfg/ui-core/utils';
 * // className={TOUCH_SAFE_MOBILE_CLASS}
 */
export const TOUCH_SAFE_MOBILE_CLASS = 'touch-safe-mobile';

/**
 * CSS class name for minimum 44px touch targets (WCAG AAA).
 *
 * @example
 * import { TOUCH_TARGET_CLASS } from '@djangocfg/ui-core/utils';
 * // className={TOUCH_TARGET_CLASS}
 */
export const TOUCH_TARGET_CLASS = 'touch-target';
