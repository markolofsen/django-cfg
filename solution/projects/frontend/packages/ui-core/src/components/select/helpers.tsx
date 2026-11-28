/**
 * Helper utilities for MultiSelectPro components
 */

import type { MultiSelectProOption } from './multi-select-pro'
import type { MultiSelectProAsyncOption } from './multi-select-pro-async'

// ==================== TYPES ====================

/**
 * Generic option builder config
 */
export interface OptionBuilderConfig<T = unknown> {
  /** Extract unique ID/value from item */
  getValue: (item: T) => string
  /** Extract main label text */
  getLabel: (item: T) => string
  /** Optional: Extract description/subtitle text */
  getDescription?: (item: T) => string | undefined
  /** Optional: Check if item is disabled */
  isDisabled?: (item: T) => boolean
  /** Optional: Custom icon component */
  getIcon?: (item: T) => React.ComponentType<{ className?: string }> | undefined
  /** Optional: Custom styling */
  getStyle?: (item: T) => {
    badgeColor?: string
    iconColor?: string
    gradient?: string
  } | undefined
}

// ==================== HELPERS ====================

/**
 * Generic option builder for MultiSelectPro components
 *
 * @example
 * ```tsx
 * // Simple usage
 * const options = items.map(createOption({
 *   getValue: (item) => item.id,
 *   getLabel: (item) => item.name,
 * }))
 *
 * // With description
 * const options = channels.map(createOption({
 *   getValue: (ch) => ch.id,
 *   getLabel: (ch) => ch.title,
 *   getDescription: (ch) => `📱 ${ch.phone}`,
 * }))
 * ```
 */
export function createOption<T>(
  config: OptionBuilderConfig<T>
): (item: T) => MultiSelectProOption | MultiSelectProAsyncOption {
  return (item: T) => ({
    value: config.getValue(item),
    label: config.getLabel(item),
    description: config.getDescription?.(item),
    disabled: config.isDisabled?.(item) ?? false,
    icon: config.getIcon?.(item),
    style: config.getStyle?.(item),
  })
}

/**
 * Batch create options from array
 *
 * @example
 * ```tsx
 * const options = createOptions(channels, {
 *   getValue: (ch) => ch.id,
 *   getLabel: (ch) => ch.title,
 *   getDescription: (ch) => ch.phone,
 * })
 * ```
 */
export function createOptions<T>(
  items: T[],
  config: OptionBuilderConfig<T>
): (MultiSelectProOption | MultiSelectProAsyncOption)[] {
  const builder = createOption(config)
  return items.map(builder)
}
