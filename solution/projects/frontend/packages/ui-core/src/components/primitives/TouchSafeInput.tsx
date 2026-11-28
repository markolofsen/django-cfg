import { forwardRef, type ComponentPropsWithoutRef, type ElementRef } from 'react';
import { touchSafeStyle } from '../../utils/touch-safe';

/**
 * Touch-safe input wrapper that automatically prevents iOS WebKit auto-zoom.
 *
 * Drop-in replacement for <input> with automatic iOS protection.
 * No device detection needed, no hooks, no manual styling.
 *
 * **How it works**:
 * - Uses CSS custom property `--touch-safe-font-size`
 * - iOS: Automatically gets max(16px, 1em) via @supports
 * - Android/Desktop: Uses provided fontSize or 1rem default
 *
 * **WCAG Compliant**: No viewport restrictions, text zoom works.
 *
 * @example Basic usage
 * ```tsx
 * import { TouchSafeInput } from '@djangocfg/ui-core/components';
 *
 * <TouchSafeInput type="email" placeholder="Email" />
 * // iOS: font-size max(16px, 1em) → no zoom
 * // Android/Desktop: font-size 1rem → design's default
 * ```
 *
 * @example Custom design font-size
 * ```tsx
 * <TouchSafeInput
 *   type="search"
 *   designFontSize="0.875rem"  // 14px on Android/Desktop
 * />
 * // iOS: max(16px, 1em)
 * // Android/Desktop: 0.875rem (14px)
 * ```
 *
 * @example With existing styles
 * ```tsx
 * <TouchSafeInput
 *   style={{ padding: '8px', border: '1px solid gray' }}
 *   designFontSize="14px"
 * />
 * // fontSize automatically added, other styles preserved
 * ```
 *
 * @see {@link ../../utils/touch-safe.ts} Utility functions
 * @see {@link ../../hooks/device/useTouchSafeStyle.ts} Hook alternative
 */
export interface TouchSafeInputProps extends ComponentPropsWithoutRef<'input'> {
  /**
   * Design's intended font-size for Android/Desktop.
   * iOS will use max(16px, 1em) regardless.
   *
   * @default '1rem'
   */
  designFontSize?: string;
}

export const TouchSafeInput = forwardRef<
  ElementRef<'input'>,
  TouchSafeInputProps
>(({ designFontSize = '1rem', style, ...props }, ref) => {
  return (
    <input
      ref={ref}
      {...props}
      style={{
        ...style,
        ...touchSafeStyle(designFontSize),
      }}
    />
  );
});

TouchSafeInput.displayName = 'TouchSafeInput';

/**
 * Touch-safe textarea wrapper that automatically prevents iOS WebKit auto-zoom.
 *
 * Drop-in replacement for <textarea> with automatic iOS protection.
 *
 * @example
 * ```tsx
 * import { TouchSafeTextarea } from '@djangocfg/ui-core/components';
 *
 * <TouchSafeTextarea
 *   placeholder="Type a message..."
 *   designFontSize="14px"
 * />
 * ```
 */
export interface TouchSafeTextareaProps extends ComponentPropsWithoutRef<'textarea'> {
  /**
   * Design's intended font-size for Android/Desktop.
   * iOS will use max(16px, 1em) regardless.
   *
   * @default '1rem'
   */
  designFontSize?: string;
}

export const TouchSafeTextarea = forwardRef<
  ElementRef<'textarea'>,
  TouchSafeTextareaProps
>(({ designFontSize = '1rem', style, ...props }, ref) => {
  return (
    <textarea
      ref={ref}
      {...props}
      style={{
        ...style,
        ...touchSafeStyle(designFontSize),
      }}
    />
  );
});

TouchSafeTextarea.displayName = 'TouchSafeTextarea';

/**
 * Touch-safe select wrapper that automatically prevents iOS WebKit auto-zoom.
 *
 * Drop-in replacement for <select> with automatic iOS protection.
 *
 * @example
 * ```tsx
 * import { TouchSafeSelect } from '@djangocfg/ui-core/components';
 *
 * <TouchSafeSelect designFontSize="14px">
 *   <option value="1">Option 1</option>
 *   <option value="2">Option 2</option>
 * </TouchSafeSelect>
 * ```
 */
export interface TouchSafeSelectProps extends ComponentPropsWithoutRef<'select'> {
  /**
   * Design's intended font-size for Android/Desktop.
   * iOS will use max(16px, 1em) regardless.
   *
   * @default '1rem'
   */
  designFontSize?: string;
}

export const TouchSafeSelect = forwardRef<
  ElementRef<'select'>,
  TouchSafeSelectProps
>(({ designFontSize = '1rem', style, ...props }, ref) => {
  return (
    <select
      ref={ref}
      {...props}
      style={{
        ...style,
        ...touchSafeStyle(designFontSize),
      }}
    />
  );
});

TouchSafeSelect.displayName = 'TouchSafeSelect';
