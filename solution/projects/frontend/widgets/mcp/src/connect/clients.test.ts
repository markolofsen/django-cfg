import { describe, expect, it } from 'vitest';

import { BRANDS, VARIANTS, brandById, variantById } from './clients';
import { claudeConnectorUrl, type McpServer } from '../install';

const server: McpServer = { url: 'https://mcp.example.com/mcp', alias: 'example', name: 'Example' };
const KEY = 'key_1234567890abcdef';
const variants = VARIANTS;
const byId = (id: string) => {
  const variant = variants.find((v) => v.id === id);
  if (!variant) throw new Error(`no variant ${id}`);
  return variant;
};

/** A deeplink's payload as plain text: the URL decoded, and its base64 `config` opened. */
function decodeLink(href: string): string {
  const config = new URL(href.replace(/^vscode:/, 'vscode://')).searchParams.get('config');
  return decodeURIComponent(href) + (config ? atob(config) : '');
}

describe('client list', () => {
  it('has unique ids and keeps the original rows', () => {
    const ids = variants.map((v) => v.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(ids).toEqual(
      expect.arrayContaining(['claude-app', 'chatgpt', 'claude-code', 'codex', 'cursor', 'vscode']),
    );
  });

  it('adds Notion, Perplexity, Gemini CLI, LM Studio and Goose', () => {
    expect(variants.map((v) => v.id)).toEqual(
      expect.arrayContaining(['notion', 'perplexity', 'gemini-cli', 'lm-studio', 'goose']),
    );
  });

  it('declares each variant action kind truthfully', () => {
    for (const variant of variants) {
      const action = variant.auth === 'oauth' ? variant.action(server) : variant.action(server, KEY);
      expect(action.kind, variant.id).toBe(variant.actionKind);
    }
  });

  it('gives OAuth rows no key and key rows the key', () => {
    for (const variant of variants) {
      if (variant.auth === 'oauth') {
        expect(JSON.stringify(variant.action(server)), variant.id).not.toContain(KEY);
      } else {
        const action = variant.action(server, KEY);
        const text = action.kind === 'link' ? decodeLink(action.href) : JSON.stringify(action);
        expect(text, variant.id).toContain(KEY);
      }
    }
  });

  it('puts Notion and Perplexity under OAuth, by URL', () => {
    expect(byId('notion').auth).toBe('oauth');
    expect(byId('perplexity').auth).toBe('oauth');
    expect(byId('notion').action(server, KEY)).toEqual({ kind: 'copy', text: 'https://mcp.example.com/mcp/' });
    expect(byId('claude-app').action(server, KEY)).toEqual({ kind: 'link', href: claudeConnectorUrl(server), newTab: true });
  });

  it('keeps every key-carrying link on a local scheme', () => {
    for (const id of ['cursor', 'vscode', 'lm-studio']) {
      const action = byId(id).auth === 'key' ? byId(id).action(server, KEY) : null;
      expect(action?.kind, id).toBe('link');
      if (action?.kind === 'link') expect(action.href.startsWith('https://'), id).toBe(false);
    }
  });

  it('marks terminal and editor rows desktop only', () => {
    for (const id of ['claude-code', 'codex', 'gemini-cli', 'cursor', 'vscode', 'lm-studio', 'goose']) {
      expect(byId(id).desktopOnly, id).toBe(true);
    }
  });

  it('gives every client a flow, and a place to paste for the URL flow', () => {
    for (const variant of variants) {
      expect(variant.flow, variant.id).toBeTruthy();
      if (variant.flow === 'url') expect(variant.where, variant.id).toBeTruthy();
    }
  });

  it('groups the ways by brand: one tile per app, every variant under exactly one brand', () => {
    expect(BRANDS.map((b) => b.id)).toEqual([
      'claude', 'chatgpt', 'codex', 'gemini', 'notion', 'perplexity', 'cursor', 'vscode', 'lm-studio', 'goose',
    ]);
    expect(new Set(BRANDS.map((b) => b.id)).size).toBe(BRANDS.length);
    expect(BRANDS.flatMap((b) => b.variants.map((v) => v.id)).sort()).toEqual(variants.map((v) => v.id).sort());
    for (const brand of BRANDS) expect(brand.variants.length, brand.id).toBeGreaterThan(0);
    expect(brandById('claude')?.variants.map((v) => v.id)).toEqual(['claude-app', 'claude-code']);
    expect(brandById('gemini')?.variants.map((v) => v.id)).toEqual(['gemini-cli']);
    expect(variantById('claude-code')).toBeDefined();
  });

  it('lists Codex once, as a brand, not also as a terminal row', () => {
    expect(variants.filter((v) => v.id.startsWith('codex'))).toHaveLength(1);
    expect(BRANDS.filter((b) => b.name === 'Codex')).toHaveLength(1);
  });

  it('never shows a key on an OAuth-only brand', () => {
    for (const id of ['chatgpt', 'notion', 'perplexity', 'goose']) {
      for (const v of brandById(id)?.variants ?? []) expect(v.auth, id).toBe('oauth');
    }
  });
});
