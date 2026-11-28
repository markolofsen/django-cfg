'use client';

/**
 * Built-in `LinkRule`s shipped with `MarkdownMessage`. These are opt-in —
 * a host enables them (e.g. via `ChatConfig.linkChips`) by appending them
 * to its own `linkRules` array; they are NOT applied automatically.
 *
 * ── `urlChipRule` ──
 *
 * Renders a BARE web URL (a plain `https://…` autolink, where the markdown
 * link text === the href) as a compact `<UrlChip>` (favicon + domain +
 * middle-ellipsis path) — the same chip the composer shows while you type a
 * URL. This makes a URL read identically across the composer and the
 * rendered bubble (plan22's reuse goal).
 *
 * Deliberately CHIPS ONLY bare URLs:
 *   - `https://github.com/wailsapp/wails`  → chip (children === href)
 *   - `[the repo](https://github.com/...)` → NOT chipped — the author chose
 *     custom link text, so we honour it and render a normal styled link
 *     (fall through to the built-in anchor).
 *
 * Scope is `http(s)` only — `mailto:` / custom schemes (`cmdop://`, …) are
 * left to other rules. Because it only matches `http(s)`, it needs no extra
 * `protocols` whitelist.
 */

import type React from 'react';

import { UrlChip } from '@djangocfg/widget-editor/chips';
import { ANCHOR } from '../role-tokens';
import { extractTextFromChildren } from './plainText';
import type { LinkRule } from './types';

/** True when the link's rendered label is just the href itself (a bare
 *  autolinked URL), i.e. the author did NOT supply custom link text. We
 *  compare the flattened text label to the href, tolerating a trailing
 *  slash difference that markdown autolinkers sometimes introduce. */
function isBareUrlLink(href: string, children: React.ReactNode): boolean {
  const label = extractTextFromChildren(children).trim();
  if (!label) return true; // no visible text → treat as bare
  const strip = (s: string) => s.replace(/\/+$/, '');
  return strip(label) === strip(href);
}

/**
 * Promote bare `www.host…` tokens to `https://www.host…` BEFORE markdown
 * parsing. remark-gfm only autolinks tokens with a scheme, so a bare `www.`
 * host would otherwise reach neither this rule nor the default anchor — it
 * renders as unstyled plain text (the reported bug). Adding the scheme lets
 * gfm autolink it so the chip rule can claim it, matching the composer
 * (whose autolink whitelist also chips `www.` hosts).
 *
 * Guards against double-prefixing: only matches a `www.` that is preceded by
 * a whitespace / line-start / `(` boundary AND not already part of a
 * `://www.` or `](…www.` URL.
 */
function promoteWwwHosts(source: string): string {
  return source.replace(
    /(^|[\s(])(www\.[^\s)<>]+)/gim,
    (_m, lead: string, host: string) => `${lead}https://${host}`,
  );
}

export const urlChipRule: LinkRule = {
  name: 'url-chip',
  // Promote bare `www.` hosts so gfm autolinks them (then we chip them).
  preprocess: promoteWwwHosts,
  // Only real web URLs. Leave mailto:/custom schemes to other rules.
  match: (href) => /^https?:\/\//i.test(href),
  render: ({ href, children, isUser }) => {
    // Honour author-chosen link text: a `[label](url)` link with custom
    // text is NOT chipped — render a normal styled link so the chosen words
    // stay the link. Use the SAME anchor styling as the built-in renderer
    // (`ANCHOR`) so it reads as a link (colored + underlined), not plain
    // text — otherwise claiming the href here strips the default styling.
    if (!isBareUrlLink(href, children)) {
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className={isUser ? ANCHOR.user : ANCHOR.assistant}
        >
          {children}
        </a>
      );
    }
    return <UrlChip href={href} />;
  },
};

export default urlChipRule;
