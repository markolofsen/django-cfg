import { describe, expect, it } from 'vitest';

import { validateLuhn } from './luhn';

describe('validateLuhn', () => {
  it('accepts known-valid card numbers', () => {
    expect(validateLuhn('4242424242424242')).toBe(true); // Visa test
    expect(validateLuhn('4111111111111111')).toBe(true); // Visa test
    expect(validateLuhn('5555555555554444')).toBe(true); // Mastercard test
  });

  it('accepts valid numbers with separators', () => {
    expect(validateLuhn('4242 4242 4242 4242')).toBe(true);
    expect(validateLuhn('4242-4242-4242-4242')).toBe(true);
  });

  it('rejects checksum-invalid numbers', () => {
    expect(validateLuhn('4242424242424243')).toBe(false);
    expect(validateLuhn('1234567812345678')).toBe(false);
  });

  it('rejects too-short / too-long digit runs', () => {
    expect(validateLuhn('1234')).toBe(false);
    expect(validateLuhn('12345678901234567890')).toBe(false);
  });
});
