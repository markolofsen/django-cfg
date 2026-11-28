// @vitest-environment jsdom
import { act, renderHook } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';

import {
  beginTwoFactorChallenge,
  endTwoFactorChallenge,
  useTwoFactorChallenge,
} from '../hooks/useTwoFactorChallenge';

describe('twoFactorChallenge', () => {
  afterEach(() => act(() => endTwoFactorChallenge()));

  it('starts with no challenge', () => {
    const { result } = renderHook(() => useTwoFactorChallenge());
    expect(result.current).toBeNull();
  });

  it('publishes a begun challenge to every subscriber', () => {
    const a = renderHook(() => useTwoFactorChallenge());
    const b = renderHook(() => useTwoFactorChallenge());

    act(() => beginTwoFactorChallenge({ sessionId: 's-1' }));

    expect(a.result.current).toEqual({ sessionId: 's-1' });
    expect(b.result.current).toEqual({ sessionId: 's-1' });
  });

  it('clears the challenge when it ends', () => {
    const { result } = renderHook(() => useTwoFactorChallenge());

    act(() => beginTwoFactorChallenge({ sessionId: 's-1' }));
    act(() => endTwoFactorChallenge());

    expect(result.current).toBeNull();
  });
});
