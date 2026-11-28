/**
 * Interpolate variables in a translation string
 *
 * @example
 * interpolate("Hello, {name}!", { name: "World" })
 * // => "Hello, World!"
 *
 * interpolate("+{count} more", { count: 5 })
 * // => "+5 more"
 */
export function interpolate(
  template: string,
  params?: Record<string, string | number>
): string {
  if (!params) return template

  return template.replace(/\{(\w+)\}/g, (match, key) => {
    if (key in params) {
      return String(params[key])
    }
    return match
  })
}
