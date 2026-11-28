/** Built-in Settings strings. English is the schema of record; `{{name}}` is filled by `fill`. */
export interface SettingsCopy {
  nav: {
    title: string;
    platform: string;
    account: string;
    preferences: string;
    apiKeys: string;
    apiKeysDescription: string;
    debug: string;
  };
  debug: {
    description: string;
    hud: string;
    hudHint: string;
    remeasureNow: string;
    readout: string;
  };
  prefs: {
    general: string;
    other: string;
    language: string;
    timeZone: string;
    theme: string;
  };
  account: {
    dangerZone: string;
    deleteAccountDescription: string;
    changeAvatar: string;
  };
  search: {
    clear: string;
  };
  security: {
    title: string;
    twoFactor: string;
    on: string;
    off: string;
    checking: string;
    unavailable: string;
    turnOn: string;
    turnOff: string;
    setupTitle: string;
    setupHint: string;
    cancel: string;
    deviceAdded: string;
    devicePrimary: string;
    disableTitle: string;
    disableHint: string;
    disabling: string;
    disable: string;
  };
  apiKey: {
    title: string;
    description: string;
    created: string;
    reissued: string;
    neverReissued: string;
    regenerate: string;
    confirmRegenerate: string;
    regenerating: string;
    regenerated: string;
    failedToRegenerate: string;
    done: string;
    test: string;
    testing: string;
    testSuccess: string;
    testFailed: string;
    keyRow: string;
    active: string;
    freshKey: string;
  };
}
