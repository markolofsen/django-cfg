/**
 * Identifier/email validation tests.
 *
 * Two copies of the email regex exist (utils/validation.validateEmail and
 * hooks/useAuthValidation.validateIdentifier) and gate whether the login form
 * lets a submit through. They must agree and must reject the usual malformed
 * inputs (spaces, double-@, missing TLD) without being so strict they reject
 * valid addresses (plus-tags, subdomains).
 */

import { describe, expect, it } from 'vitest';

import { validateEmail } from '../utils/validation';
import { validateIdentifier } from '../hooks/useAuthValidation';

const VALID = [
  'a@b.co',
  'user@example.com',
  'user.name@example.com',
  'user+tag@example.com',
  'user@sub.example.co.uk',
  'USER@EXAMPLE.COM',
  '123@numbers.io',
];

const INVALID = [
  '',
  'plainstring',
  'no-at-sign.com',
  '@no-local.com',
  'no-domain@',
  'no-tld@example',
  'two@@example.com',
  'spaces in@example.com',
  'trailing@space.com ',
  ' leading@space.com',
  'new\nline@example.com',
  'a@b@c.com',
];

describe('validateEmail (utils/validation)', () => {
  it.each(VALID)('accepts %s', (email) => {
    expect(validateEmail(email)).toBe(true);
  });
  it.each(INVALID)('rejects %j', (email) => {
    expect(validateEmail(email)).toBe(false);
  });
});

describe('validateIdentifier (useAuthValidation) matches validateEmail', () => {
  it.each([...VALID, ...INVALID])('agrees on %j', (input) => {
    expect(validateIdentifier(input)).toBe(validateEmail(input));
  });
});
