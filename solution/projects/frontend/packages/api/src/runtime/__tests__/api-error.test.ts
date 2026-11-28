/**
 * H1.4 `APIError.errorMessage` and `fieldErrors` for DRF bodies; H1.5 `isPermissionError` is 403 only.
 */
import { describe, expect, it } from 'vitest';

import { formatAuthError } from '../../auth/utils/errors';
import { APIError } from '../errors';

const URL = 'https://api.example.test/cfg/accounts/profile/';
const error = (status: number, body: unknown, statusText = '') => new APIError(status, body, URL, undefined, statusText);

describe('errorMessage', () => {
  it.each<[string, unknown, string]>([
    ['a DRF detail string', { detail: 'Not found.' }, 'Not found.'],
    ['a DRF detail array', { detail: ['First problem.', 'Second problem.'] }, 'First problem., Second problem.'],
    ['django-cfg error', { error: 'Code expired' }, 'Code expired'],
    ['non_field_errors', { non_field_errors: ['Passwords do not match.'] }, 'Passwords do not match.'],
    ['detail ahead of non_field_errors', { detail: 'Throttled.', non_field_errors: ['x'] }, 'Throttled.'],
    ['non_field_errors ahead of a field', { email: ['Taken.'], non_field_errors: ['Try again.'] }, 'Try again.'],
    ['the first field error', { email: ['Enter a valid email address.'], phone: ['Required.'] }, 'email: Enter a valid email address.'],
    ['several messages of one field', { password: ['Too short.', 'Too common.'] }, 'password: Too short., Too common.'],
    ['field_errors nested by django-cfg', { field_errors: { code: ['Invalid code.'] } }, 'code: Invalid code.'],
    ['items that are objects with a message', { detail: [{ message: 'Bad token', code: 'token_not_valid' }] }, 'Bad token'],
  ])('reads %s', (_label, body, expected) => {
    expect(error(400, body).errorMessage).toBe(expected);
  });

  it.each<[string, unknown]>([
    ['an empty body', {}],
    ['no body', undefined],
    ['an HTML page', '<html>bad gateway</html>'],
    ['a detail object with no text', { detail: { nested: true } }],
  ])('falls back to the generic status line for %s', (_label, body) => {
    expect(error(502, body, 'Bad Gateway').errorMessage).toBe('HTTP 502: Bad Gateway');
    expect(error(502, body).errorMessage).toBe('HTTP 502:');
  });

  it('keeps an explicit message when the body has no text', () => {
    expect(new APIError(200, '<html>', URL, 'Expected a JSON response').errorMessage).toBe('Expected a JSON response');
  });

  it('puts whole-request server text into message, never a field name', () => {
    expect(error(400, { detail: ['A', 'B'] }).message).toBe('A, B');
    expect(error(400, { email: ['Taken.'] }).message).toBe('HTTP 400:');
  });

  it('lets formatAuthError show its own copy for the generic message', () => {
    expect(formatAuthError(error(503, {}))).toBe('Server is unavailable');
    expect(formatAuthError(error(400, { detail: 'This code has expired' }))).toBe('This code has expired');
  });
});

describe('fieldErrors', () => {
  it('maps each field to its messages, non_field_errors included, detail excluded', () => {
    expect(error(400, {
      detail: ['not a field'],
      email: ['Taken.', { message: 'Also bad.' }],
      non_field_errors: ['Try again.'],
      ignored: 'a string, not a DRF list',
      empty: [],
    }).fieldErrors).toEqual({
      email: ['Taken.', 'Also bad.'],
      non_field_errors: ['Try again.'],
    });
  });

  it('reads django-cfg field_errors when the body nests them', () => {
    expect(error(400, { error: 'Invalid', field_errors: { code: ['Invalid code.'] } }).fieldErrors)
      .toEqual({ code: ['Invalid code.'] });
  });

  it('is empty for a body without field errors', () => {
    expect(error(500, 'oops').fieldErrors).toEqual({});
  });
});

describe('status predicates (H1.5)', () => {
  it('isPermissionError is 403 only; isAuthError is 401', () => {
    expect([error(401, {}).isPermissionError, error(403, {}).isPermissionError]).toEqual([false, true]);
    expect([error(401, {}).isAuthError, error(403, {}).isAuthError]).toEqual([true, false]);
  });

  it('keeps the constructor order (status, response, url, message, statusText)', () => {
    const failure = new APIError(404, { detail: 'Missing' }, URL, 'explicit', 'Not Found');
    expect(failure).toMatchObject({ statusCode: 404, url: URL, message: 'explicit', statusText: 'Not Found' });
    expect(failure.response).toEqual({ detail: 'Missing' });
  });
});
