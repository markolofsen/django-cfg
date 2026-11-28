export const SITEVERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify';

export interface SiteverifyResponse {
  success: boolean;
  hostname?: string;
  action?: string;
  'error-codes'?: string[];
}

export type VerifyResult = { ok: true } | { ok: false; reason: string; retry: boolean };

/**
 * Server-side Turnstile check. `success` alone is not enough: the token must
 * have been issued for this host and this action, or a token minted on any
 * other site that shares the key would clear the gate.
 */
export async function verifyTurnstile(args: {
  secret: string;
  token: string;
  remoteIp?: string | null;
  expectedHostnames: string[];
  expectedAction: string;
  fetch?: typeof fetch;
}): Promise<VerifyResult> {
  const body = new URLSearchParams({ secret: args.secret, response: args.token });
  if (args.remoteIp) body.set('remoteip', args.remoteIp);
  let data: SiteverifyResponse;
  try {
    const res = await (args.fetch ?? fetch)(SITEVERIFY_URL, { method: 'POST', body, signal: AbortSignal.timeout(5000) });
    data = (await res.json()) as SiteverifyResponse;
  } catch {
    return { ok: false, reason: 'siteverify-unreachable', retry: true };
  }
  if (!data.success) {
    const codes = data['error-codes'] ?? [];
    // An expired or reused token is fixed by a new widget run.
    const retry = codes.includes('timeout-or-duplicate') || codes.includes('invalid-input-response');
    return { ok: false, reason: codes[0] ?? 'rejected', retry };
  }
  if (!data.hostname || !args.expectedHostnames.some((h) => h.toLowerCase() === data.hostname!.toLowerCase())) {
    return { ok: false, reason: 'hostname-mismatch', retry: false };
  }
  if (data.action !== args.expectedAction) return { ok: false, reason: 'action-mismatch', retry: false };
  return { ok: true };
}
