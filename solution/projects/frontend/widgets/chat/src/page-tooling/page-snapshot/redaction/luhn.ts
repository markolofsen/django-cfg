/**
 * Luhn checksum — validates credit-card-shaped digit runs so order
 * numbers and IDs are not falsely redacted as cards.
 *
 */

/** Validate a digit string with the Luhn algorithm. */
export function validateLuhn(digits: string): boolean {
  const normalized = digits.replace(/\D/g, '');
  if (normalized.length < 13 || normalized.length > 19) return false;

  let sum = 0;
  let double = false;
  for (let i = normalized.length - 1; i >= 0; i--) {
    let digit = normalized.charCodeAt(i) - 48; // '0' === 48
    if (digit < 0 || digit > 9) return false;
    if (double) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }
    sum += digit;
    double = !double;
  }
  return sum % 10 === 0;
}
