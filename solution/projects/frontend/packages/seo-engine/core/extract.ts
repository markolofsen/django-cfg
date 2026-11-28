/**
 * MDX-aware extraction of links, images, headings, and external URLs.
 *
 * Uses mdast (remark/micromark) for correct markdown parsing, plus a small
 * JSX/HTML pass for `href=`/`src=` attributes the markdown AST exposes as raw
 * nodes. We only care about references the docs author wrote; code spans and
 * code blocks are skipped by the parser naturally for inline/link/image nodes.
 */
import { readFile } from 'node:fs/promises';
import { fromMarkdown } from 'mdast-util-from-markdown';
import { mdxFromMarkdown } from 'mdast-util-mdx';
import { mdxjs } from 'micromark-extension-mdxjs';
import { visit } from 'unist-util-visit';
import GithubSlugger from 'github-slugger';
import { toString as mdToString } from 'mdast-util-to-string';
import type { Root } from 'mdast';
import type { ExternalRef, LinkKind, LinkRef } from './types.js';

/** Split an href into pathname + anchor (keeps leading '#'). */
export function splitHref(href: string): { pathname: string; anchor: string } {
  const hashIdx = href.indexOf('#');
  if (hashIdx === -1) return { pathname: href, anchor: '' };
  return { pathname: href.slice(0, hashIdx), anchor: href.slice(hashIdx) };
}

/**
 * Strip a leading YAML/TOML frontmatter block, replacing it with blank lines so
 * downstream line numbers stay accurate. mdast-util-from-markdown has no native
 * frontmatter support without an extra extension, and would otherwise mis-parse
 * the `---` fences as thematic breaks.
 */
export function stripFrontmatter(source: string): string {
  const m = /^(---|\+\+\+)\r?\n[\s\S]*?\r?\n\1\r?\n?/.exec(source);
  if (!m || m.index !== 0) return source;
  const blanks = m[0].replace(/[^\n]/g, '');
  return blanks + source.slice(m[0].length);
}

/** True for hrefs we should never validate as internal (external, mailto, etc). */
export function isExternal(href: string): boolean {
  return (
    /^[a-z][a-z0-9+.-]*:/i.test(href) || // http:, https:, mailto:, tel:, etc.
    href.startsWith('//')
  );
}

/** True for hrefs that are http(s) URLs we can probe over the network. */
export function isHttp(href: string): boolean {
  return /^https?:\/\//i.test(href) || href.startsWith('//');
}

const HREF_ATTR_RE = /\b(href|src)\s*=\s*(?:"([^"]*)"|'([^']*)'|\{\s*['"]([^'"]*)['"]\s*\})/g;

function parseMdx(source: string): Root {
  try {
    return fromMarkdown(source, {
      extensions: [mdxjs()],
      mdastExtensions: [mdxFromMarkdown()],
    }) as Root;
  } catch {
    // If MDX parsing fails (rare authoring edge), behave as an empty tree.
    return { type: 'root', children: [] } as Root;
  }
}

/** Extract every authored link + image reference from one MDX file, with positions. */
export async function extractLinks(absFile: string): Promise<LinkRef[]> {
  const source = stripFrontmatter(await readFile(absFile, 'utf8'));
  const tree = parseMdx(source);
  const out: LinkRef[] = [];

  const seen = new Set<string>();
  const push = (
    raw: string,
    line: number,
    column: number,
    kind: LinkKind,
    inJsx: boolean,
    jsxTag?: string,
  ) => {
    if (!raw) return;
    const key = `${line}:${column}:${kind}:${raw}`;
    if (seen.has(key)) return; // same ref at same position (e.g. JSX element visited twice)
    seen.add(key);
    const { pathname, anchor } = splitHref(raw);
    out.push({ file: absFile, line, column, raw, pathname, anchor, kind, inJsx, jsxTag });
  };

  visit(tree, (node: any) => {
    // Markdown links: [text](href) and reference definitions. (Nextra rewrites relative → absolute.)
    if ((node.type === 'link' || node.type === 'definition') && typeof node.url === 'string') {
      const pos = node.position?.start ?? { line: 1, column: 1 };
      push(node.url, pos.line, pos.column, 'link', false);
    }
    // Markdown images: ![alt](src) and image reference definitions.
    if (node.type === 'image' && typeof node.url === 'string') {
      const pos = node.position?.start ?? { line: 1, column: 1 };
      push(node.url, pos.line, pos.column, 'image', false);
    }
    // JSX elements / raw HTML carrying href=/src= attributes (<a>, <img>, <Image>, <Card>). NOT rewritten.
    if (node.type === 'mdxJsxFlowElement' || node.type === 'mdxJsxTextElement') {
      const tag = typeof node.name === 'string' ? node.name.toLowerCase() : undefined;
      for (const attr of node.attributes ?? []) {
        if (attr.type !== 'mdxJsxAttribute') continue;
        if (attr.name !== 'href' && attr.name !== 'src') continue;
        const pos = node.position?.start ?? { line: 1, column: 1 };
        const val =
          typeof attr.value === 'string'
            ? attr.value
            : attr.value?.value?.replace(/^['"]|['"]$/g, '');
        if (typeof val === 'string') {
          push(val, pos.line, pos.column, attr.name === 'src' ? 'image' : 'link', true, tag);
        }
      }
    }
    if ((node.type === 'html' || node.type === 'mdxFlowExpression') && typeof node.value === 'string') {
      const baseLine = node.position?.start?.line ?? 1;
      let m: RegExpExecArray | null;
      HREF_ATTR_RE.lastIndex = 0;
      while ((m = HREF_ATTR_RE.exec(node.value))) {
        const attrName = m[1];
        const raw = m[2] ?? m[3] ?? m[4] ?? '';
        const before = node.value.slice(0, m.index);
        const lineOffset = before.split('\n').length - 1;
        // Identify the enclosing raw-HTML tag (e.g. <a>, <img>) for this attr.
        const tagM = /<\s*([a-zA-Z][\w-]*)[^>]*$/.exec(before);
        const tag = tagM ? tagM[1].toLowerCase() : undefined;
        push(raw, baseLine + lineOffset, 1, attrName === 'src' ? 'image' : 'link', true, tag);
      }
    }
  });

  return out;
}

/**
 * Extract raw `<a href="…">` references from a component/app source file
 * (`.tsx`/`.jsx`) — for basePath enforcement. DELIBERATELY conservative:
 *
 *  - Only matches literal `<a …>` opening tags (raw anchors). `next/link`
 *    `<Link>` and custom components are ignored (they handle basePath / aren't
 *    raw anchors).
 *  - Only captures STATIC string-literal hrefs: `href="/x"` or `href='/x'`.
 *    Expression hrefs (`href={…}` — helpers, template literals, variables) are
 *    skipped because they can't be statically resolved (this is also why the
 *    fixed DocCard/SiteFooter, which use `href={withDocsBase(...)}`, are NOT
 *    flagged — their hrefs are expressions, not literals).
 *  - Returns `inJsx: true` so the checker applies the raw-`<a>` basePath rule.
 */
export async function extractComponentHrefs(absFile: string): Promise<LinkRef[]> {
  const source = await readFile(absFile, 'utf8');
  const out: LinkRef[] = [];
  // Match an opening <a ...> tag (non-greedy up to the closing '>'), then pull a
  // static string-literal href from within it. `[^>]*?` never crosses tags.
  const A_TAG_RE = /<a\b([^>]*?)>/gi;
  const HREF_LITERAL_RE = /\bhref\s*=\s*(?:"([^"]*)"|'([^']*)')/;
  let am: RegExpExecArray | null;
  while ((am = A_TAG_RE.exec(source))) {
    const attrs = am[1];
    const hm = HREF_LITERAL_RE.exec(attrs);
    if (!hm) continue; // no static literal href (likely href={expr}) — skip
    const raw = hm[1] ?? hm[2] ?? '';
    if (!raw) continue;
    const line = source.slice(0, am.index).split('\n').length;
    const { pathname, anchor } = splitHref(raw);
    out.push({ file: absFile, line, column: 1, raw, pathname, anchor, kind: 'link', inJsx: true, jsxTag: 'a' });
  }
  return out;
}

/**
 * Build the set of anchor slugs a target page exposes — the same slugs Nextra
 * generates client-side via github-slugger from each heading's text. Includes
 * explicit `{#custom-id}` heading ids and `id="…"` attributes on JSX/HTML.
 */
export async function extractHeadings(absFile: string): Promise<Set<string>> {
  const source = stripFrontmatter(await readFile(absFile, 'utf8'));
  const tree = parseMdx(source);
  const slugger = new GithubSlugger();
  const slugs = new Set<string>();

  visit(tree, (node: any) => {
    if (node.type === 'heading') {
      // Heading text (code spans become their literal text — matches Nextra).
      let text = mdToString(node);
      // Honor an explicit `{#custom-id}` suffix (remark-style) if present.
      const custom = /\{#([a-z0-9._-]+)\}\s*$/i.exec(text);
      if (custom) {
        slugs.add(custom[1]);
        text = text.slice(0, custom.index).trim();
      }
      if (text) slugs.add(slugger.slug(text));
    }
    // Explicit id="…" on JSX/HTML elements is a valid anchor target too.
    if (node.type === 'mdxJsxFlowElement' || node.type === 'mdxJsxTextElement') {
      for (const attr of node.attributes ?? []) {
        if (attr.type === 'mdxJsxAttribute' && attr.name === 'id' && typeof attr.value === 'string') {
          slugs.add(attr.value);
        }
      }
    }
    if (node.type === 'html' && typeof node.value === 'string') {
      const m = /\bid\s*=\s*(?:"([^"]*)"|'([^']*)')/g;
      let r: RegExpExecArray | null;
      while ((r = m.exec(node.value))) slugs.add(r[1] ?? r[2] ?? '');
    }
  });

  slugs.delete('');
  return slugs;
}

/** Extract every external (http/https/protocol-relative) URL with its location. */
export async function extractExternalRefs(absFile: string): Promise<ExternalRef[]> {
  const source = stripFrontmatter(await readFile(absFile, 'utf8'));
  const tree = parseMdx(source);
  const out: ExternalRef[] = [];
  const seen = new Set<string>();

  const push = (url: string, line: number) => {
    if (!url || !isHttp(url)) return;
    const normalized = url.startsWith('//') ? 'https:' + url : url;
    const key = `${line}:${normalized}`;
    if (seen.has(key)) return;
    seen.add(key);
    out.push({ url: normalized, file: absFile, line });
  };

  visit(tree, (node: any) => {
    if ((node.type === 'link' || node.type === 'image' || node.type === 'definition') && typeof node.url === 'string') {
      push(node.url, node.position?.start?.line ?? 1);
    }
    if (node.type === 'mdxJsxFlowElement' || node.type === 'mdxJsxTextElement') {
      for (const attr of node.attributes ?? []) {
        if (attr.type === 'mdxJsxAttribute' && (attr.name === 'href' || attr.name === 'src')) {
          const val = typeof attr.value === 'string' ? attr.value : attr.value?.value?.replace(/^['"]|['"]$/g, '');
          if (typeof val === 'string') push(val, node.position?.start?.line ?? 1);
        }
      }
    }
    if ((node.type === 'html' || node.type === 'mdxFlowExpression') && typeof node.value === 'string') {
      const baseLine = node.position?.start?.line ?? 1;
      let m: RegExpExecArray | null;
      HREF_ATTR_RE.lastIndex = 0;
      while ((m = HREF_ATTR_RE.exec(node.value))) {
        const raw = m[2] ?? m[3] ?? m[4] ?? '';
        const lineOffset = node.value.slice(0, m.index).split('\n').length - 1;
        push(raw, baseLine + lineOffset);
      }
    }
  });

  return out;
}
