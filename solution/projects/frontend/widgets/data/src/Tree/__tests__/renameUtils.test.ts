import { describe, expect, it } from 'vitest';

import { autoSelectRange, splitFileName } from '../data/renameUtils';

describe('splitFileName', () => {
  it('splits a regular file name into base + ext', () => {
    expect(splitFileName('foo.txt')).toEqual({ base: 'foo', ext: '.txt' });
  });

  it('returns whole name as base when there is no dot', () => {
    expect(splitFileName('readme')).toEqual({ base: 'readme', ext: '' });
  });

  it('treats dotfiles as base-only', () => {
    expect(splitFileName('.env')).toEqual({ base: '.env', ext: '' });
    expect(splitFileName('.gitignore')).toEqual({ base: '.gitignore', ext: '' });
  });

  it('splits a dotfile with an extension', () => {
    expect(splitFileName('.env.local')).toEqual({ base: '.env', ext: '.local' });
  });

  it('uses the last dot for multi-dot names', () => {
    expect(splitFileName('foo.bar.baz')).toEqual({ base: 'foo.bar', ext: '.baz' });
  });

  it('handles the empty string', () => {
    expect(splitFileName('')).toEqual({ base: '', ext: '' });
  });
});

describe('autoSelectRange', () => {
  it('selects only the base for a regular file', () => {
    expect(autoSelectRange('foo.txt', false)).toEqual([0, 3]);
  });

  it('selects the entire name for a folder', () => {
    expect(autoSelectRange('foo.txt', true)).toEqual([0, 7]);
  });

  it('selects the full dotfile name (no extension)', () => {
    expect(autoSelectRange('.env', false)).toEqual([0, 4]);
  });

  it('selects only base for a dotfile with extension', () => {
    expect(autoSelectRange('.env.local', false)).toEqual([0, 4]);
  });

  it('selects [0, 0] for empty name', () => {
    expect(autoSelectRange('', false)).toEqual([0, 0]);
  });
});
