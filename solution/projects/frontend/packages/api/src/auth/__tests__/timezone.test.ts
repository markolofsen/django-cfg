import { beforeEach, describe, expect, it } from 'vitest';

import { auth } from '../../runtime/auth';

describe('auth time zone override', () => {
  beforeEach(() => auth.setTimezone(null));

  it('follows the browser until overridden', () => {
    expect(auth.getTimezone()).toBe(Intl.DateTimeFormat().resolvedOptions().timeZone);
  });

  it('returns the override and clears back to the browser zone', () => {
    auth.setTimezone('Asia/Seoul');
    expect(auth.getTimezone()).toBe('Asia/Seoul');
    auth.setTimezone(null);
    expect(auth.getTimezone()).toBe(Intl.DateTimeFormat().resolvedOptions().timeZone);
  });
});
