import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import { Markdown } from './markdown';

/**
 * What this component's CONFIGURATION does, not what the parser does.
 *
 * Every case below is a decision that would be invisible if it regressed:
 * `MarkdownMessage` used to render these two surfaces with a different engine
 * and a different threat model, so the replacement has to be pinned on the
 * points where the two disagree — not on "does markdown render".
 */

const render = (markdown: string, props: { size?: 'xs' | 'sm' | 'base' } = {}) =>
  renderToStaticMarkup(<Markdown {...props}>{markdown}</Markdown>);

describe('the markdown a reader is shown', () => {
  it('renders GFM: tables and strikethrough', () => {
    // The predecessor pulled `remark-gfm` in explicitly. Streamdown carries it,
    // which is the fact that made this replacement safe — asserted rather than
    // assumed, because a news post is mostly tables and lists.
    const html = render('| a | b |\n|---|---|\n| 1 | 2 |\n\n~~gone~~');

    expect(html).toContain('<table');
    expect(html).toContain('<del');
  });

  it('scales the body through size, defaulting to sm', () => {
    expect(render('text')).toContain('text-sm');
    expect(render('text', { size: 'xs' })).toContain('text-xs');
    expect(render('text', { size: 'base' })).toContain('text-base');
  });
});

describe('the threat model that separates this from the chat renderer', () => {
  it('keeps an ordinary link usable', () => {
    // The control. Without it, the two assertions below pass on a build where
    // every link is stripped — which is not hardening, it is breakage.
    const html = render('[docs](https://example.com/x)');

    expect(html).toContain('https://example.com/x');
  });

  it('does NOT make an app scheme followable, where the chat does', () => {
    // `Response` allows it because a host there assigns it meaning — a mention
    // chip. Nothing rendering a news post or a file preview does, so an app
    // scheme arriving in text written elsewhere has no reason to be clickable.
    //
    // Asserted on the HREF, not on the string: `harden` keeps the rejected url
    // in a `title` for the reader, so `not.toContain(url)` fails on correct
    // output. The question is whether a click can follow it.
    const html = render('[link](app://resource/abc123)');

    expect(html).not.toContain('href="app://resource/abc123"');
    expect(html).toContain('[blocked]');
  });

  it('renders raw HTML as TEXT rather than as markup', () => {
    // A deliberate difference from the predecessor, which ran `rehype-raw` and
    // then sanitized the result. Streamdown escapes instead, so `<script>`
    // cannot execute — and `<strong>` does not emphasise either.
    //
    // Pinned because it is a behaviour change on catalogue documents, whose
    // authors may have written HTML expecting it to render. Turning it back on
    // means adding `rehype-raw` AND a sanitizer, in that order — the two are
    // one decision, and this test is where that decision would be recorded.
    const html = render('Text with <strong>bold</strong> and <script>alert(1)</script>.');

    expect(html).not.toContain('<strong>');
    expect(html).not.toContain('<script>');
    expect(html).toContain('&lt;strong&gt;');
  });

  it('strips a javascript: url', () => {
    const html = render('[click](javascript:alert(1))');

    expect(html).not.toContain('href="javascript:');
  });
});

describe('a diagram in a document', () => {
  it('routes a mermaid fence to the diagram branch, not to a code block', () => {
    // The case the SCREENSHOT exposed. An agent asked to draw a diagram writes
    // a `.md` file, and the document preview is the only surface that reads it
    // — so a plugin wired into the transcript alone leaves the diagram
    // rendering as a code block exactly where it was asked for.
    //
    // Asserted on the element the fence became: streamdown draws the picture
    // from an async effect inside `Suspense`, so static markup shows the
    // skeleton whichever way the render ends.
    const html = render('```mermaid\ngraph TD;\nA-->B;\n```');

    expect(html).not.toContain('data-streamdown="code-block"');
    expect(html).not.toContain('data-language="mermaid"');
  });

  it('still renders a NON-mermaid fence as a code block', () => {
    // The control. Without it the assertions above also pass on a build where
    // the code plugin fell out entirely and every fence became a skeleton.
    const html = render('```ts\nconst x = 1;\n```');

    expect(html).toContain('data-streamdown="code-block"');
    expect(html).toContain('data-language="ts"');
  });
});
