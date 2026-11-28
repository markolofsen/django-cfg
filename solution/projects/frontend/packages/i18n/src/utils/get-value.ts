/**
 * Get a nested value from an object using dot notation
 *
 * @example
 * getNestedValue({ ui: { select: { placeholder: 'Select...' } } }, 'ui.select.placeholder')
 * // => 'Select...'
 */
export function getNestedValue(
  obj: Record<string, unknown>,
  path: string
): string | undefined {
  const keys = path.split('.')
  let current: unknown = obj

  for (const key of keys) {
    if (current === null || current === undefined) {
      return undefined
    }
    if (typeof current !== 'object') {
      return undefined
    }
    current = (current as Record<string, unknown>)[key]
  }

  if (typeof current === 'string') {
    return current
  }

  return undefined
}
