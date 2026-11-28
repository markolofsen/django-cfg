import { describe, expect, it } from 'vitest';

import { readSignedRequest, safeRedirect } from './signedRequest';

describe('safeRedirect', () => {
  it('lets the web and desktop-client schemes through', () => {
    expect(safeRedirect('https://claude.ai/api/mcp/auth_callback?code=c')).toBe('https://claude.ai/api/mcp/auth_callback?code=c');
    expect(safeRedirect('http://localhost:33418/callback?error=access_denied')).toBe('http://localhost:33418/callback?error=access_denied');
    expect(safeRedirect('cursor://anysphere.cursor-mcp/oauth/callback?code=c')).toBe('cursor://anysphere.cursor-mcp/oauth/callback?code=c');
  });

  it('refuses script, data and relative targets', () => {
    for (const bad of ['javascript:alert(1)', 'data:text/html,x', '/relative', undefined, 42, 'x'.repeat(5000)]) {
      expect(safeRedirect(bad)).toBeUndefined();
    }
  });
});

const seal = (data: object) =>
  `${btoa(JSON.stringify(data)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')}:1abc:sig`;

describe('readSignedRequest', () => {
  it('reads the client and where the result goes', () => {
    expect(readSignedRequest(seal({ name: 'Friendly', dest: 'claude.ai', uri: 'https://claude.ai/x' }))).toEqual({ client: 'Friendly', host: 'claude.ai' });
    expect(readSignedRequest(seal({ name: 'Cursor', dest: 'cursor://anysphere.cursor-mcp' }))?.host).toBe('cursor://anysphere.cursor-mcp');
  });

  it('cuts an overlong name', () => {
    expect(readSignedRequest(seal({ name: 'x'.repeat(200), dest: 'a.b' }))?.client).toHaveLength(80);
  });

  it('returns null for anything else, so the query fallback applies', () => {
    for (const bad of ['', 'signed-request', '.eJxLzs', seal({ name: 'x' }), seal({ name: 1, dest: 'a' }), seal({ name: 'x', dest: '' })]) {
      expect(readSignedRequest(bad)).toBeNull();
    }
  });
});
