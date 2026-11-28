import { describe, it, expect } from 'vitest';
import { findFilePaths, splitPath, truncatePathLabel } from '../detect';

describe('findFilePaths', () => {
  it('detects the repro path embedded in Cyrillic prose', () => {
    const text =
      'прочти манифест /Users/example/workspace/projects/cmdop/@docs/positioning/manifest.md интересно твоё мнение';
    const matches = findFilePaths(text);
    expect(matches).toHaveLength(1);
    expect(matches[0]!.path).toBe(
      '/Users/example/workspace/projects/cmdop/@docs/positioning/manifest.md',
    );
    // The slice at [start,end) must equal the matched path exactly.
    expect(text.slice(matches[0]!.start, matches[0]!.end)).toBe(matches[0]!.path);
  });

  it('detects a Windows drive path with backslashes', () => {
    const matches = findFilePaths('see C:\\Users\\me\\notes.md please');
    expect(matches).toHaveLength(1);
    expect(matches[0]!.path).toBe('C:\\Users\\me\\notes.md');
  });

  it('detects a Windows drive path with forward slashes', () => {
    const matches = findFilePaths('open C:/Users/me/notes.md');
    expect(matches[0]!.path).toBe('C:/Users/me/notes.md');
  });

  it('detects a UNC path', () => {
    const matches = findFilePaths('on \\\\srv\\share\\x.md here');
    expect(matches).toHaveLength(1);
    expect(matches[0]!.path).toBe('\\\\srv\\share\\x.md');
  });

  it('detects a ~ home path', () => {
    const matches = findFilePaths('edit ~/dev/a.ts now');
    expect(matches).toHaveLength(1);
    expect(matches[0]!.path).toBe('~/dev/a.ts');
  });

  it('detects a file:// URI', () => {
    const matches = findFilePaths('go to file:///x/y.md ok');
    expect(matches).toHaveLength(1);
    expect(matches[0]!.path).toBe('file:///x/y.md');
  });

  it('detects a directory path ending in a folder', () => {
    const matches = findFilePaths('cd /Users/me/positioning');
    expect(matches).toHaveLength(1);
    expect(matches[0]!.path).toBe('/Users/me/positioning');
  });

  it('detects a directory path ending in a trailing separator', () => {
    const matches = findFilePaths('cd /Users/me/positioning/ then');
    expect(matches[0]!.path).toBe('/Users/me/positioning/');
  });

  it('trims trailing sentence punctuation', () => {
    const matches = findFilePaths('see /a/b/c.md. Done.');
    expect(matches).toHaveLength(1);
    expect(matches[0]!.path).toBe('/a/b/c.md');
  });

  it('trims a closing paren', () => {
    const matches = findFilePaths('(at /a/b/c.md)');
    expect(matches[0]!.path).toBe('/a/b/c.md');
  });

  // ── False positives ──

  it('does NOT match a prose slash "a / b"', () => {
    expect(findFilePaths('a / b')).toHaveLength(0);
  });

  it('does NOT match a single-segment root "/foo"', () => {
    expect(findFilePaths('just /foo here')).toHaveLength(0);
  });

  it('does NOT match an https URL as a file path', () => {
    expect(findFilePaths('visit https://x.com/y/z page')).toHaveLength(0);
  });

  it('does NOT match an http URL as a file path', () => {
    expect(findFilePaths('http://example.com/a/b')).toHaveLength(0);
  });

  it('does NOT match bare relative tokens', () => {
    expect(findFilePaths('run ./script and src/index.ts')).toHaveLength(0);
  });

  it('finds multiple paths in one string', () => {
    const matches = findFilePaths('a /x/y.ts and ~/z/w.md done');
    expect(matches.map((m) => m.path)).toEqual(['/x/y.ts', '~/z/w.md']);
  });
});

describe('splitPath', () => {
  it('splits a unix file path', () => {
    expect(splitPath('/Users/me/manifest.md')).toEqual({
      dir: 'Users/me',
      base: 'manifest.md',
      isDir: false,
    });
  });

  it('treats an extensionless basename as a dir', () => {
    const r = splitPath('/Users/me/positioning');
    expect(r.base).toBe('positioning');
    expect(r.isDir).toBe(true);
  });

  it('treats a trailing-separator path as a dir', () => {
    const r = splitPath('/Users/me/docs/');
    expect(r.base).toBe('docs');
    expect(r.isDir).toBe(true);
  });

  it('is separator-agnostic for Windows paths', () => {
    const r = splitPath('C:\\Users\\me\\notes.md');
    expect(r.base).toBe('notes.md');
    expect(r.isDir).toBe(false);
  });

  it('strips a file:// scheme', () => {
    expect(splitPath('file:///x/y.md').base).toBe('y.md');
  });

  it('treats a dotfile as a file', () => {
    expect(splitPath('/home/me/.gitignore').isDir).toBe(false);
  });
});

describe('truncatePathLabel', () => {
  it('keeps a short path unchanged', () => {
    expect(truncatePathLabel('/a/b.md')).toBe('/a/b.md');
  });

  it('middle-ellipsizes a long path but keeps the basename', () => {
    const label = truncatePathLabel(
      '/Users/example/workspace/projects/cmdop/@docs/positioning/manifest.md',
    );
    expect(label).toContain('manifest.md');
    expect(label).toContain('…');
    // Basename is never cut.
    expect(label.endsWith('manifest.md')).toBe(true);
  });

  it('respects a custom maxChars', () => {
    const label = truncatePathLabel('/very/long/path/to/some/file.md', {
      maxChars: 16,
    });
    expect(label.endsWith('file.md')).toBe(true);
    expect(label).toContain('…');
  });

  it('keeps the parent folder hint for a long path', () => {
    const label = truncatePathLabel(
      '/Users/example/workspace/projects/cmdop/@docs/positioning/manifest.md',
    );
    expect(label).toContain('positioning');
  });
});
