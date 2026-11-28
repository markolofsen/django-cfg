// What the consent flow reads from a link and a redirect, without React: testable headless.

/** Addresses the browser may be sent to: the web and the custom schemes of desktop clients, never script or data URLs. */
export function safeRedirect(target: unknown): string | undefined {
  if (typeof target !== 'string' || target.length > 4096) return undefined;
  try {
    const url = new URL(target);
    return ['javascript:', 'data:', 'vbscript:', 'file:', 'blob:', 'about:'].includes(url.protocol) ? undefined : url.toString();
  } catch {
    return undefined;
  }
}

/**
 * What the signed `request` says about who is asking and where the result goes, for DISPLAY only.
 * django-cfg seals the request uncompressed: `base64url(json):timestamp:signature`. Reading the
 * JSON here is safe because the page never acts on it: Allow posts the whole token to
 * `oauth/approve/`, which verifies the signature and uses its own copy. An edited display
 * breaks the signature, so it cannot be combined with a genuine grant. Absent or unreadable
 * (compressed, older server): `null`, and the page falls back to the query as before.
 */
export function readSignedRequest(request: string): { client: string; host: string } | null {
  try {
    const part = request.split(':')[0] ?? '';
    const b64 = part.replace(/-/g, '+').replace(/_/g, '/');
    const bytes = Uint8Array.from(atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4)), (c) => c.charCodeAt(0));
    const data = JSON.parse(new TextDecoder().decode(bytes)) as { name?: unknown; dest?: unknown };
    if (typeof data.name !== 'string' || typeof data.dest !== 'string' || !data.dest) return null;
    return { client: data.name.slice(0, 80), host: data.dest.slice(0, 200) };
  } catch {
    return null;
  }
}
