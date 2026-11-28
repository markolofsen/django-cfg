import React from 'react';

/** Recursively concatenate the text content of a React.ReactNode tree.
 *  Used by the markdown renderers (e.g. `<pre>` extracting code) and
 *  by consumers that need a plain-string label out of link children. */
export function extractTextFromChildren(children: React.ReactNode): string {
  if (typeof children === 'string') return children;
  if (typeof children === 'number') return String(children);
  if (React.isValidElement(children)) {
    const props = children.props as { children?: React.ReactNode };
    return extractTextFromChildren(props.children);
  }
  if (Array.isArray(children)) {
    return children.map(extractTextFromChildren).join('');
  }
  return '';
}

/**
 * Auto-detect whether `text` should bypass ReactMarkdown and render as
 * a flat `<div whitespace-pre-wrap>`. Used as the *fallback* when the
 * caller doesn't pass `plainText` explicitly to `MarkdownMessage`.
 *
 * The signal we trust: short, single-paragraph, no markdown markers.
 * Anything longer / multi-paragraph / structurally suggestive falls
 * through to the markdown pipeline — false negatives there are cheap
 * (markdown renders prose correctly), false positives in the prose
 * branch surface as escaped `*` / `#` / etc. so we err markdown-ward.
 *
 * Thresholds were picked from chat-bubble UX research (see ChatGPT,
 * Claude.ai, WhatsApp): roughly "would a person have written this in
 * one keystroke without thinking about formatting?". If you find them
 * too tight or too loose, tune here — every consumer goes through
 * `MarkdownMessage` so the change is universal.
 */
export function looksLikePlainProse(text: string): boolean {
  const trimmed = text.trim();
  // Empty / whitespace-only — render as plain (cheap path, nothing to parse).
  if (trimmed.length === 0) return true;
  // Long enough that it's likely a structured assistant reply.
  if (trimmed.length > 500) return false;
  // Paragraph break → almost certainly markdown territory.
  if (/\n\s*\n/.test(trimmed)) return false;
  // Many single-line breaks → probably a list or stanza.
  const newlineCount = (trimmed.match(/\n/g) || []).length;
  if (newlineCount > 4) return false;
  // Any markdown marker → defer to ReactMarkdown.
  if (hasMarkdownSyntax(trimmed)) return false;
  return true;
}

/** Affordance test: does this string look like markdown? Used to skip
 *  the (heavier) ReactMarkdown pipeline when the content is pure
 *  prose. NOT a validator — false negatives are fine; false positives
 *  cost a render but render correctly. */
export function hasMarkdownSyntax(text: string): boolean {
  // Newlines after trim → render as markdown so paragraphs work.
  if (text.trim().includes('\n')) return true;

  // Inline HTML tags (`<br>`, `<b>`, `<code>`, …) — common in OpenAPI
  // descriptions. Without this branch the fast path would escape them
  // and the user sees literal angle brackets.
  if (/<\/?[a-zA-Z][a-zA-Z0-9-]*(\s[^>]*)?\/?>/.test(text)) return true;

  const patterns = [
    /^#{1,6}\s/m,           // Headers
    /\*\*[^*]+\*\*/,        // Bold
    /\*[^*]+\*/,            // Italic
    /__[^_]+__/,            // Bold (underscore)
    /_[^_]+_/,              // Italic (underscore)
    /\[.+\]\(.+\)/,         // Links
    /!\[.*\]\(.+\)/,        // Images
    /```[\s\S]*```/,        // Code blocks
    /`[^`]+`/,              // Inline code
    /^\s*[-*+]\s/m,         // Unordered lists
    /^\s*\d+\.\s/m,         // Ordered lists
    /^\s*>/m,               // Blockquotes
    /\|.+\|/,               // Tables
    /^---+$/m,              // Horizontal rules
    /~~[^~]+~~/,            // Strikethrough
  ];
  return patterns.some((p) => p.test(text));
}
