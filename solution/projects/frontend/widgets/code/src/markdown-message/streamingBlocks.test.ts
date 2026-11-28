import { describe, expect, it } from 'vitest';

import { renderableTail, splitStreamingBlocks } from './streamingBlocks';

/**
 * This splitter is what lets a streaming reply render live without re-parsing
 * the whole document per token. Two contracts hold the product up:
 *
 *   - `blocks` must be STABLE — a block, once emitted, must keep the same `raw`
 *     text forever as more tokens arrive, or the consumer's memo key changes and
 *     every block re-parses (the O(n^2) this module exists to avoid).
 *   - a blank line INSIDE a fence must not cut a block, and an unclosed fence
 *     must be reported, or the rest of the message renders as code.
 */

describe('splitStreamingBlocks — boundaries', () => {
  it('returns nothing for empty content', () => {
    expect(splitStreamingBlocks('')).toEqual({ blocks: [], tail: '', tailInOpenFence: false });
  });

  it('holds a partial first block back as the tail', () => {
    // The whole point of boundary buffering: `**bol` must not reach the
    // markdown parser, or the reader sees the asterisks flash.
    expect(splitStreamingBlocks('**bol')).toEqual({
      blocks: [],
      tail: '**bol',
      tailInOpenFence: false,
    });
  });

  it('splits at a blank line', () => {
    const r = splitStreamingBlocks('one\n\ntwo');
    expect(r.blocks).toEqual(['one']);
    expect(r.tail).toBe('two');
  });

  it('promotes the tail to a block once the content ends on a newline', () => {
    const r = splitStreamingBlocks('one\n\ntwo\n');
    expect(r.blocks).toEqual(['one', 'two']);
    expect(r.tail).toBe('');
  });

  it('collapses runs of blank lines rather than emitting empty blocks', () => {
    const r = splitStreamingBlocks('one\n\n\n\ntwo\n');
    expect(r.blocks).toEqual(['one', 'two']);
  });

  it('ignores leading blank lines', () => {
    expect(splitStreamingBlocks('\n\none\n').blocks).toEqual(['one']);
  });

  it('keeps single newlines inside one block', () => {
    // A markdown list is one block; splitting per line would parse each item
    // as its own document and lose the list.
    const r = splitStreamingBlocks('- a\n- b\n- c\n');
    expect(r.blocks).toEqual(['- a\n- b\n- c']);
  });
});

describe('splitStreamingBlocks — stability under streaming', () => {
  it('never rewrites a block that was already emitted', () => {
    // The memoization contract. Feed the same document one character at a
    // time and assert each prefix's blocks are a prefix of the final blocks.
    const full = '# Title\n\nSome prose here.\n\n```ts\nconst x = 1;\n```\n\nTrailing words.\n';
    const final = splitStreamingBlocks(full).blocks;
    for (let i = 1; i <= full.length; i++) {
      const { blocks } = splitStreamingBlocks(full.slice(0, i));
      expect(final.slice(0, blocks.length)).toEqual(blocks);
    }
  });

  it('emits blocks monotonically — the count never goes down', () => {
    const full = 'a\n\nb\n\nc\n\nd\n';
    let previous = 0;
    for (let i = 1; i <= full.length; i++) {
      const { blocks } = splitStreamingBlocks(full.slice(0, i));
      expect(blocks.length).toBeGreaterThanOrEqual(previous);
      previous = blocks.length;
    }
  });
});

describe('splitStreamingBlocks — fences', () => {
  it('does not cut a block at a blank line inside a fence', () => {
    const r = splitStreamingBlocks('```ts\na\n\nb\n```\n');
    expect(r.blocks).toEqual(['```ts\na\n\nb\n```']);
    expect(r.tailInOpenFence).toBe(false);
  });

  it('reports an unterminated fence so the tail renders as code, not prose', () => {
    const r = splitStreamingBlocks('```ts\nconst x = 1;');
    expect(r.blocks).toEqual([]);
    expect(r.tail).toBe('```ts\nconst x = 1;');
    expect(r.tailInOpenFence).toBe(true);
  });

  it('keeps a trailing newline inside an open fence, because there it is content', () => {
    // Outside a fence a trailing newline promotes the tail to a block; inside
    // one it is a blank line of the code being streamed and must survive.
    const r = splitStreamingBlocks('```ts\nconst x = 1;\n');
    expect(r.tail).toBe('```ts\nconst x = 1;\n');
    expect(r.tailInOpenFence).toBe(true);
  });

  it('does not promote the tail to a block while the fence is open, even on a newline', () => {
    // Promoting would hand ReactMarkdown a half-open fence, which swallows
    // whatever streams in next.
    expect(splitStreamingBlocks('```\nx\n').tailInOpenFence).toBe(true);
    expect(splitStreamingBlocks('```\nx\n').blocks).toEqual([]);
  });

  it('closes only on a matching fence char of at least the opening length', () => {
    // A ``` line inside a ```` block is code, not a close.
    const r = splitStreamingBlocks('````\n```\nstill code\n````\n');
    expect(r.tailInOpenFence).toBe(false);
    expect(r.blocks).toEqual(['````\n```\nstill code\n````']);
  });

  it('does not let a tilde fence close a backtick fence', () => {
    expect(splitStreamingBlocks('```\nx\n~~~\ny\n').tailInOpenFence).toBe(true);
  });

  it('supports tilde fences', () => {
    const r = splitStreamingBlocks('~~~py\nx = 1\n~~~\n');
    expect(r.tailInOpenFence).toBe(false);
    expect(r.blocks).toEqual(['~~~py\nx = 1\n~~~']);
  });

  it('does not treat a fence line carrying an info string as a close', () => {
    expect(splitStreamingBlocks('```\nx\n``` js\ny\n').tailInOpenFence).toBe(true);
  });

  it('allows the fence to be indented up to 3 spaces', () => {
    const r = splitStreamingBlocks('   ```\n   x\n   ```\n');
    expect(r.tailInOpenFence).toBe(false);
  });
});

describe('renderableTail', () => {
  it('passes a prose tail through untouched — no syntax repair', () => {
    expect(renderableTail('**half bo', false)).toEqual({ source: '**half bo', asCode: false });
  });

  it('virtually closes an open fence with a matching marker', () => {
    expect(renderableTail('```ts\nconst x = 1;', true)).toEqual({
      source: '```ts\nconst x = 1;\n```',
      asCode: true,
    });
  });

  it('re-uses the opening marker\'s char and length', () => {
    expect(renderableTail('````\nx', true).source).toBe('````\nx\n````');
    expect(renderableTail('~~~py\nx', true).source).toBe('~~~py\nx\n~~~');
  });

  it('does not add a second newline when the tail already ends with one', () => {
    expect(renderableTail('```\nx\n', true).source).toBe('```\nx\n```');
  });

  it('falls back to ``` when the first line is not a recognisable fence', () => {
    expect(renderableTail('not a fence', true).source).toBe('not a fence\n```');
  });

  it('does not mutate the tail it was given', () => {
    const tail = '```\nx';
    renderableTail(tail, true);
    expect(tail).toBe('```\nx');
  });
});
