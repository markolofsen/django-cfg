import { describe, expect, it } from 'vitest';

import { languageLabel, normalizePrismLanguage } from './languages';

describe('normalizePrismLanguage', () => {
  it.each([
    ['ts', 'typescript'],
    ['TS', 'typescript'],
    ['js', 'javascript'],
    ['py', 'python'],
    ['sh', 'bash'],
    ['shell', 'bash'],
    ['zsh', 'bash'],
    ['html', 'markup'],
    ['xml', 'markup'],
    ['yml', 'yaml'],
    ['golang', 'go'],
    ['tsx', 'tsx'],
  ])('%s -> %s', (fence, grammar) => {
    expect(normalizePrismLanguage(fence)).toBe(grammar);
  });

  it('passes an unknown name through, so Prism renders it as plain text', () => {
    expect(normalizePrismLanguage('klingon')).toBe('klingon');
  });

  it('answers text for no language at all', () => {
    expect(normalizePrismLanguage(undefined)).toBe('text');
    expect(normalizePrismLanguage('')).toBe('text');
    expect(normalizePrismLanguage('  ')).toBe('text');
  });

  it('does not highlight a mermaid fence: the diagram branch draws it', () => {
    expect(normalizePrismLanguage('mermaid')).toBe('text');
  });
});

describe('languageLabel', () => {
  it('names the known languages the way their projects do', () => {
    expect(languageLabel('ts')).toBe('TypeScript');
    expect(languageLabel('sql')).toBe('SQL');
    expect(languageLabel('golang')).toBe('Go');
  });

  it('capitalises an unknown name rather than hiding it', () => {
    expect(languageLabel('klingon')).toBe('Klingon');
  });

  it('labels a fence with no language as Text', () => {
    expect(languageLabel('')).toBe('Text');
    expect(languageLabel(undefined)).toBe('Text');
  });
});
