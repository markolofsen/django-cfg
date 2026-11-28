/**
 * Shared quota detection for the localStorage / sessionStorage hooks.
 *
 * Internal — not exported from the package entry point.
 */

/**
 * Is this thrown value the browser's "storage is full" signal?
 *
 * Boundary: a `catch` binding is `unknown`, and browsers disagree on how they
 * report a full quota — Chrome/Safari throw `QuotaExceededError`, older engines
 * use the legacy DOMException code 22, and some report it only in the message.
 * Each field is therefore probed rather than assumed to exist.
 */
export function isQuotaExceededError(error: unknown): boolean {
  if (typeof error !== 'object' || error === null) return false;

  const { name, code, message } = error as {
    name?: unknown;
    code?: unknown;
    message?: unknown;
  };

  if (name === 'QuotaExceededError') return true;
  if (code === 22) return true;
  return typeof message === 'string' && message.includes('quota');
}
