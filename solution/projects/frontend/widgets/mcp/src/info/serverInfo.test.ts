import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';

import { fetchServerInfo } from './serverInfo';

describe('fetchServerInfo', () => {
  const server = { url: 'https://mcp.example.com/mcp/' };

  it('sends the key to /info/ and parses the body', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ tools: [{ name: 'a', description: 'b' }] }) });
    vi.stubGlobal('fetch', fetchMock);
    const info = await fetchServerInfo(server, 'k1');
    expect(fetchMock.mock.calls[0]![0]).toBe('https://mcp.example.com/mcp/info/');
    expect(fetchMock.mock.calls[0]![1].headers['X-MCP-Access-Key']).toBe('k1');
    expect(info?.tools).toEqual([{ name: 'a', description: 'b' }]);
  });

  it('is null on 401, a network error and a bad body', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }));
    expect(await fetchServerInfo(server, 'k')).toBeNull();
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('cors')));
    expect(await fetchServerInfo(server, 'k')).toBeNull();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => { throw new Error('x'); } }));
    expect(await fetchServerInfo(server, 'k')).toBeNull();
  });
});
void renderToStaticMarkup;
