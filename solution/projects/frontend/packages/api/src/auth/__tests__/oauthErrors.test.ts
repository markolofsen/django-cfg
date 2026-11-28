import { describe, expect, it } from 'vitest';

import { OAuthErrorCodeEnum } from '../../_api/models';
import { readOAuthFailure } from '../utils/oauthErrors';

const failure = (error: string) => readOAuthFailure({ response: { error, error_description: 'prose' } }, 'fallback');

describe('readOAuthFailure', () => {
  it.each(Object.values(OAuthErrorCodeEnum.enum))('recognises the generated code %s', (code) => {
    expect(failure(code)).toEqual({ code, message: 'prose' });
  });

  it('does not treat an unknown error string as a code', () => {
    expect(failure('teapot').code).toBeUndefined();
  });

  it('falls back when the body has no description', () => {
    expect(readOAuthFailure({ response: { error: 'invalid_state' } }, 'fallback')).toEqual({
      code: 'invalid_state',
      message: 'fallback',
    });
  });
});
