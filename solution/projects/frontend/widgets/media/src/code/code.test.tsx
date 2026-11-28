import { code } from '@streamdown/code';
import { renderToStaticMarkup } from 'react-dom/server';
import { Streamdown } from 'streamdown';
import { describe, expect, it } from 'vitest';

import { Code } from './code';

const render = (
  data: string | object,
  props: { language?: string; variant?: 'card' | 'plain' } = {},
) =>
  renderToStaticMarkup(
    <Code data={data} language={props.language ?? 'typescript'} variant={props.variant} />,
  );

describe('a code listing', () => {
  it('highlights the source', () => {
    const html = render('const x: number = 1;');

    expect(html).toContain('data-streamdown="code-block"');
    expect(html).toContain('data-language="typescript"');
    expect(html).toContain('const');
  });

  it.each(['bash', 'python', 'typescript', 'markdown', 'json'])(
    'supports %s, which a call site passes today',
    (language) => {
      expect(render('x', { language })).toContain(`data-language="${language}"`);
    },
  );

  it('serialises an object, as the predecessor accepted one', () => {
    // `&quot;` rather than `"`: the key is rendered as HTML text, so the quotes
    // arrive escaped. Asserting the raw character fails on correct output.
    expect(render({ a: 1 }, { language: 'json' })).toContain('&quot;a&quot;: 1');
  });
});

describe('the fence cannot be broken by the source', () => {
  it('survives a source containing its own triple-backtick fence', () => {
    // The defect this escaping exists to prevent. A README or an agent's
    // answer routinely contains a fenced block; wrapping it in three backticks
    // ends the outer block at the inner fence, so the tail renders as PROSE —
    // silently, and looking like a rendering bug rather than a quoting one.
    const source = 'before\n```\ninner\n```\nafter';
    const html = render(source, { language: 'markdown' });

    expect(html).toContain('data-streamdown="code-block"');
    expect(html).toContain('after');
    // One block, not two: a broken fence would open a second one.
    expect(html.match(/data-streamdown="code-block"/g)).toHaveLength(1);
  });

  it('detects the break a NAIVE three-backtick fence would cause', () => {
    // The control, and it has to bypass `Code` to be one: rendering the same
    // source through the component again would exercise the very escaping
    // under test. This wraps it the naive way and asserts the damage is real —
    // without it, the case above passes on a parser that never splits at all.
    const naive = renderToStaticMarkup(
      <Streamdown mode="static" parseIncompleteMarkdown={false} plugins={{ code }}>
        {'```markdown\nbefore\n```\ninner\n```\nafter\n```'}
      </Streamdown>,
    );

    expect(naive.match(/data-streamdown="code-block"/g)?.length ?? 0).toBeGreaterThan(1);
  });
});

describe('the two variants differ', () => {
  it('gives card its own copy control and plain none', () => {
    // `plain` embeds inside a container that already scrolls and already owns
    // the copy affordance; a second one there is chrome the variant exists to
    // remove.
    const card = render('const x = 1;', { variant: 'card' });
    const plain = render('const x = 1;', { variant: 'plain' });

    expect(card).toContain('data-variant="card"');
    expect(plain).toContain('data-variant="plain"');
    expect(card.length).toBeGreaterThan(plain.length);
  });
});
