import { describe, expect, it } from 'vitest';

import { CFG_KEYS, cfgStorage } from '../storage';

describe('storage on the server', () => {
  it('never throws and never holds state', () => {
    expect(typeof window).toBe('undefined');
    expect(cfgStorage.read(CFG_KEYS.accessToken.key)).toBeNull();
    expect(cfgStorage.write(CFG_KEYS.accessToken.key, 'x')).toBe(false);
    expect(cfgStorage.read(CFG_KEYS.accessToken.key)).toBeNull();
    expect(() => cfgStorage.clearAll({ all: true })).not.toThrow();
    expect(cfgStorage.onChange(CFG_KEYS.accessToken.key, () => {})).toBeTypeOf('function');
  });
});
