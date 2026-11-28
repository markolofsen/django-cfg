/**
 * Signed clearance cookie: `v1.<payload>.<signature>`, HMAC-SHA256 over the
 * payload, Web Crypto only (runs in the Edge runtime). The payload binds the
 * clearance to a hash of the User-Agent and an expiry.
 */

const enc = new TextEncoder();

export interface ClearancePayload {
  /** issued at, unix seconds */
  iat: number;
  /** expires at, unix seconds */
  exp: number;
  /** first 16 hex chars of SHA-256(User-Agent) */
  ua: string;
}

function b64u(bytes: Uint8Array): string {
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function fromB64u(s: string): Uint8Array | null {
  try {
    const bin = atob(s.replace(/-/g, '+').replace(/_/g, '/'));
    return Uint8Array.from(bin, (c) => c.charCodeAt(0));
  } catch {
    return null;
  }
}

async function hmac(secret: string, data: string): Promise<Uint8Array> {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return new Uint8Array(await crypto.subtle.sign('HMAC', key, enc.encode(data)));
}

function equal(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= (a[i] ?? 0) ^ (b[i] ?? 0);
  return d === 0;
}

export async function hashUa(ua: string | null): Promise<string> {
  const h = new Uint8Array(await crypto.subtle.digest('SHA-256', enc.encode(ua ?? '')));
  return Array.from(h.slice(0, 8), (x) => x.toString(16).padStart(2, '0')).join('');
}

/** Secrets are comma-separated: the first signs, all verify (rotation). */
export function parseSecrets(raw: string | undefined): string[] {
  return (raw ?? '').split(',').map((s) => s.trim()).filter(Boolean);
}

export async function signClearance(secret: string, ua: string | null, ttlSeconds: number, now = Date.now()): Promise<string> {
  const iat = Math.floor(now / 1000);
  const payload: ClearancePayload = { iat, exp: iat + ttlSeconds, ua: await hashUa(ua) };
  const body = b64u(enc.encode(JSON.stringify(payload)));
  const sig = b64u(await hmac(secret, `v1.${body}`));
  return `v1.${body}.${sig}`;
}

export async function verifyClearance(secrets: string[], value: string | undefined, ua: string | null, now = Date.now()): Promise<boolean> {
  if (!value || secrets.length === 0) return false;
  const parts = value.split('.');
  if (parts.length !== 3 || parts[0] !== 'v1') return false;
  const body = parts[1] ?? '';
  const sig = parts[2] ?? '';
  const given = fromB64u(sig);
  if (!given) return false;
  let ok = false;
  for (const secret of secrets) {
    if (equal(await hmac(secret, `v1.${body}`), given)) ok = true;
  }
  if (!ok) return false;
  const raw = fromB64u(body);
  if (!raw) return false;
  let p: ClearancePayload;
  try {
    p = JSON.parse(new TextDecoder().decode(raw));
  } catch {
    return false;
  }
  if (typeof p.exp !== 'number' || typeof p.ua !== 'string') return false;
  if (p.exp * 1000 <= now) return false;
  return p.ua === (await hashUa(ua));
}
