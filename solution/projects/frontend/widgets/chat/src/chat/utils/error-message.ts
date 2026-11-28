/**
 * The readable half of a thrown value.
 *
 * A `catch` binding is `unknown`, and a rejected fetch, a thrown string and a
 * real `Error` all arrive through it. Rendering one directly prints
 * `[object Object]` in the place a user reads to find out what went wrong.
 */
export function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
