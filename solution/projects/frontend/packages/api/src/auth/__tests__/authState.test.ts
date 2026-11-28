import { describe, expect, it } from 'vitest';

import { resolveAuthStatus, type AuthStateInput } from '../utils/authState';

const base: AuthStateInput = {
  clientReady: true,
  snapshotAuthenticated: false,
  storeAuthenticated: false,
  profileSettled: false,
  timedOut: false,
};
const at = (over: Partial<AuthStateInput>) => resolveAuthStatus({ ...base, ...over });

describe('resolveAuthStatus', () => {
  it('is resolving until the client has read the session (hydration commit)', () => {
    expect(at({ clientReady: false })).toBe('resolving');
    expect(at({ clientReady: false, snapshotAuthenticated: true, storeAuthenticated: true, profileSettled: true })).toBe('resolving');
  });

  it('is anonymous when store and snapshot both say signed out', () => {
    expect(at({})).toBe('anonymous');
  });

  it('is authenticated once the profile settled', () => {
    expect(at({ snapshotAuthenticated: true, storeAuthenticated: true, profileSettled: true })).toBe('authenticated');
  });

  it('is resolving while a live session loads its profile', () => {
    expect(at({ snapshotAuthenticated: true, storeAuthenticated: true })).toBe('resolving');
  });

  it('waits while the snapshot lags behind the store', () => {
    expect(at({ snapshotAuthenticated: false, storeAuthenticated: true })).toBe('resolving');
  });

  it('never stays resolving once the timer fired', () => {
    expect(at({ snapshotAuthenticated: true, storeAuthenticated: true, timedOut: true })).toBe('authenticated');
    expect(at({ snapshotAuthenticated: false, storeAuthenticated: true, timedOut: true })).toBe('anonymous');
  });

  it('terminates for every input once clientReady and timedOut', () => {
    for (const snap of [true, false]) for (const store of [true, false]) for (const prof of [true, false]) {
      expect(at({ snapshotAuthenticated: snap, storeAuthenticated: store, profileSettled: prof, timedOut: true })).not.toBe('resolving');
    }
  });
});
