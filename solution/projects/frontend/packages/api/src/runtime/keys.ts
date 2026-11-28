export type KeyStore = 'local' | 'session' | 'cookie';

export interface KeySpec {
  readonly key: string;
  readonly store: KeyStore;
  readonly personal: boolean;
}

export interface FamilySpec {
  readonly prefix: string;
  readonly store: 'local' | 'session';
  readonly personal: boolean;
}

export interface StorageOptions {
  readonly keys?: Readonly<Record<string, KeySpec>>;
  readonly families?: Readonly<Record<string, FamilySpec>>;
  readonly cookieMaxAgeSeconds?: number;
  readonly cookieDomain?: 'auto' | string | false;
}

export interface WriteOptions {
  readonly maxAgeSeconds?: number;
}

export interface GuardedStorage {
  readonly owner: string;
  key(...parts: string[]): string;
  familyKey(family: FamilySpec, id: string): string;
  isValid(key: string): boolean;
  read(key: string, store?: KeyStore): string | null;
  write(key: string, value: string, store?: KeyStore, options?: WriteOptions): boolean;
  remove(key: string, store?: KeyStore): void;
  readJSON<T>(key: string, store?: KeyStore): T | null;
  writeJSON(key: string, value: unknown, store?: KeyStore): boolean;
  keys(store?: Exclude<KeyStore, 'cookie'>): string[];
  clearAll(options?: { all?: boolean }): void;
  setCookieDomain(domain: 'auto' | string | false): void;
  cookieDomain(): string | null;
  onChange(key: string, listener: (value: string | null) => void, store?: Exclude<KeyStore, 'cookie'>): () => void;
}

const hasWindow = () => typeof window !== 'undefined';
const domainByHost = new Map<string, string | null>();

function detectCookieDomain(): string | null {
  if (!hasWindow() || typeof document === 'undefined') return null;
  const host = window.location.hostname.toLowerCase();
  if (!host || !host.includes('.') || host.includes(':') || /^[0-9.]+$/.test(host)) return null;
  const cached = domainByHost.get(host);
  if (cached !== undefined) return cached;

  const labels = host.split('.');
  const secure = window.location.protocol === 'https:' ? '; Secure' : '';
  let found: string | null = null;
  try {
    for (let i = labels.length - 2; i >= 0 && found === null; i -= 1) {
      const candidate = labels.slice(i).join('.');
      const probe = `cfg_probe_${Math.random().toString(36).slice(2)}`;
      document.cookie = `${probe}=1; Domain=${candidate}; Path=/; Max-Age=30; SameSite=Lax${secure}`;
      if (document.cookie.includes(`${probe}=1`)) found = candidate;
      document.cookie = `${probe}=; Domain=${candidate}; Path=/; Max-Age=0; SameSite=Lax${secure}`;
    }
  } catch {
    found = null;
  }
  domainByHost.set(host, found);
  return found;
}

const nativeStorage = (store: 'local' | 'session'): Storage | null => {
  if (!hasWindow()) return null;
  try {
    return store === 'local' ? window.localStorage : window.sessionStorage;
  } catch {
    return null;
  }
};

export function normalizeSegment(value: string): string {
  return value.trim().toLowerCase().replace(/[^a-z0-9_]+/g, '_').replace(/^_+|_+$/g, '');
}

const readCookie = (key: string): string | null => {
  if (!hasWindow() || typeof document === 'undefined') return null;
  const encoded = encodeURIComponent(key);
  const match = document.cookie.split('; ').find((part) => part.startsWith(`${encoded}=`));
  return match ? decodeURIComponent(match.slice(encoded.length + 1)) : null;
};

export function createStorage(owner: string, options: StorageOptions = {}): GuardedStorage {
  if (!/^[a-z][a-z0-9_]*$/.test(owner)) throw new TypeError(`invalid storage owner: ${owner}`);
  const prefix = `${owner}.`;
  const pattern = owner === 'cfg' ? /^cfg(\.[a-z0-9_]+)+$/ : new RegExp(`^(cfg|${owner})(\\.[a-z0-9_]+)+$`);
  const specs = Object.values(options.keys ?? {});
  const families = Object.values(options.families ?? {});
  const memory = new Map<string, string>();
  let cookiePolicy: 'auto' | string | false = options.cookieDomain ?? 'auto';
  const resolveCookieDomain = (): string | null =>
    cookiePolicy === false ? null : cookiePolicy === 'auto' ? detectCookieDomain() : cookiePolicy;

  const storeFor = (key: string, requested?: KeyStore): KeyStore =>
    requested ?? specs.find((spec) => spec.key === key)?.store ?? 'local';
  const assertValid = (key: string) => {
    if (!pattern.test(key)) throw new TypeError(`invalid storage key: ${key}`);
  };
  const assertOwned = (key: string) => {
    assertValid(key);
    if (!key.startsWith(prefix)) throw new TypeError(`storage key is not owned by ${owner}: ${key}`);
  };
  const read = (key: string, requested?: KeyStore): string | null => {
    assertValid(key);
    const store = storeFor(key, requested);
    if (store === 'cookie') return readCookie(key) ?? memory.get(`${store}:${key}`) ?? null;
    try {
      return nativeStorage(store)?.getItem(key) ?? memory.get(`${store}:${key}`) ?? null;
    } catch {
      return memory.get(`${store}:${key}`) ?? null;
    }
  };
  const write = (key: string, value: string, requested?: KeyStore, writeOptions?: WriteOptions): boolean => {
    assertOwned(key);
    const store = storeFor(key, requested);
    if (!hasWindow()) return false;
    try {
      if (store === 'cookie') {
        const domain = resolveCookieDomain();
        const domainPart = domain ? `; Domain=${domain}` : '';
        document.cookie = `${encodeURIComponent(key)}=${encodeURIComponent(value)}; Path=/; Max-Age=${writeOptions?.maxAgeSeconds ?? options.cookieMaxAgeSeconds ?? 2_592_000}; SameSite=Lax${domainPart}`;
        if (domain) {
          document.cookie = `${encodeURIComponent(key)}=; Path=/; Max-Age=0; SameSite=Lax`;
        }
        if (readCookie(key) !== value) throw new Error('cookie write was rejected');
      } else {
        const storage = nativeStorage(store);
        if (!storage) throw new Error('storage unavailable');
        storage.setItem(key, value);
      }
      memory.delete(`${store}:${key}`);
      return true;
    } catch {
      memory.set(`${store}:${key}`, value);
      return false;
    }
  };
  const remove = (key: string, requested?: KeyStore): void => {
    assertOwned(key);
    const store = storeFor(key, requested);
    memory.delete(`${store}:${key}`);
    try {
      if (!hasWindow()) return;
      if (store === 'cookie') {
        document.cookie = `${encodeURIComponent(key)}=; Path=/; Max-Age=0; SameSite=Lax`;
        const domain = resolveCookieDomain();
        if (domain) document.cookie = `${encodeURIComponent(key)}=; Path=/; Max-Age=0; SameSite=Lax; Domain=${domain}`;
      } else nativeStorage(store)?.removeItem(key);
    } catch {
      /* Storage can be unavailable in private/SSR contexts. */
    }
  };

  const api: GuardedStorage = {
    owner,
    key(...parts) {
      const normalized = parts.map(normalizeSegment);
      if (!normalized.length || normalized.some((part) => !part)) throw new TypeError('storage key parts cannot be empty');
      return `${prefix}${normalized.join('.')}`;
    },
    familyKey(family, id) {
      const normalized = normalizeSegment(id);
      if (!normalized) throw new TypeError('storage family id cannot be empty');
      return `${family.prefix}${normalized}`;
    },
    isValid: (key) => pattern.test(key),
    read,
    write,
    remove,
    readJSON<T>(key: string, store?: KeyStore) {
      const value = read(key, store);
      if (value === null) return null;
      try { return JSON.parse(value) as T; } catch { return null; }
    },
    writeJSON(key: string, value: unknown, store?: KeyStore) {
      return write(key, JSON.stringify(value), store);
    },
    keys(store = 'local') {
      const values: string[] = [];
      const native = nativeStorage(store);
      if (native) for (let i = 0; i < native.length; i += 1) {
        const key = native.key(i);
        if (key?.startsWith(prefix)) values.push(key);
      }
      for (const key of memory.keys()) {
        const [, name] = key.split(':', 2);
        if (key.startsWith(`${store}:`) && name?.startsWith(prefix) && !values.includes(name)) values.push(name);
      }
      return values;
    },
    clearAll({ all = false } = {}) {
      for (const spec of specs) if (all || spec.personal) remove(spec.key, spec.store);
      for (const family of families) {
        if (!all && !family.personal) continue;
        for (const key of api.keys(family.store)) {
          if (key.startsWith(family.prefix)) remove(key, family.store);
        }
      }
      if (all) {
        for (const store of ['local', 'session'] as const) {
          for (const key of api.keys(store)) remove(key, store);
        }
        if (hasWindow()) {
          for (const part of document.cookie.split('; ')) {
            const key = decodeURIComponent(part.split('=')[0] ?? '');
            if (key.startsWith(prefix)) remove(key, 'cookie');
          }
        }
      }
    },
    setCookieDomain(domain) { cookiePolicy = domain; },
    cookieDomain: resolveCookieDomain,
    onChange(key, listener, store = 'local') {
      if (!hasWindow()) return () => undefined;
      const handler = (event: StorageEvent) => {
        if (event.storageArea === nativeStorage(store) && event.key === key) listener(event.newValue);
      };
      window.addEventListener('storage', handler);
      return () => window.removeEventListener('storage', handler);
    },
  };
  return api;
}

export const CFG_KEYS = {
  accessToken: { key: 'cfg.auth.access_token', store: 'cookie', personal: true },
  refreshToken: { key: 'cfg.auth.refresh_token', store: 'cookie', personal: true },
  apiKey: { key: 'cfg.auth.api_key', store: 'local', personal: true },
  /** Bumped on every session write so other tabs re-read the token cookies (cookies raise no `storage` event). No token in it. */
  sessionSignal: { key: 'cfg.auth.session_signal', store: 'local', personal: false },
  email: { key: 'cfg.auth.email', store: 'local', personal: false },
  emailTs: { key: 'cfg.auth.email_ts', store: 'local', personal: false },
  redirectUrl: { key: 'cfg.auth.redirect_url', store: 'session', personal: true },
  redirectUrlTs: { key: 'cfg.auth.redirect_url_ts', store: 'session', personal: true },
  oauthState: { key: 'cfg.auth.oauth_state', store: 'session', personal: true },
  oauthProvider: { key: 'cfg.auth.oauth_provider', store: 'session', personal: true },
  oauthProviders: { key: 'cfg.auth.oauth_providers', store: 'session', personal: false },
  profileCache: { key: 'cfg.profile.cache', store: 'local', personal: true },
  monitorSessionId: { key: 'cfg.monitor.session_id', store: 'local', personal: false },
  monitorSessionCookie: { key: 'cfg.monitor.session_id', store: 'cookie', personal: false },
  monitorDebug: { key: 'cfg.monitor.debug', store: 'local', personal: false },
  clientId: { key: 'cfg.client.id', store: 'local', personal: false },
  uiTabId: { key: 'cfg.ui.tab_id', store: 'session', personal: false },
  uiRouterSerial: { key: 'cfg.ui.router_serial', store: 'session', personal: false },
  uiState: { key: 'cfg.ui.state', store: 'local', personal: false },
  uiLocaleHint: { key: 'cfg.ui.locale_hint', store: 'local', personal: false },
  chatSpeechLanguage: { key: 'cfg.chat.speech_language', store: 'local', personal: false },
  chatRecentTools: { key: 'cfg.chat.recent_tools', store: 'local', personal: false },
  formsSpeechDebug: { key: 'cfg.forms.speech_debug', store: 'local', personal: false },
  formsSpeechPrefs: { key: 'cfg.forms.speech_prefs', store: 'local', personal: false },
  agentPlaygroundApiKeyId: { key: 'cfg.agent.playground_api_key_id', store: 'session', personal: true },
  agentPlaygroundBearer: { key: 'cfg.agent.playground_bearer', store: 'session', personal: true },
  agentEndpointDoc: { key: 'cfg.agent.endpoint_doc', store: 'session', personal: false },
} as const satisfies Record<string, KeySpec>;

export const CFG_FAMILIES = {
  chatDraft: { prefix: 'cfg.chat.draft.', store: 'session', personal: true },
  dataTree: { prefix: 'cfg.data.tree.', store: 'local', personal: false },
  agentEndpointDraft: { prefix: 'cfg.agent.endpoint_draft.', store: 'local', personal: false },
} as const satisfies Record<string, FamilySpec>;

export const cfgStorage = createStorage('cfg', { keys: CFG_KEYS, families: CFG_FAMILIES });

