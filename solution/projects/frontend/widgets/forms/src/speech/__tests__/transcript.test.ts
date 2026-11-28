import { describe, expect, it } from 'vitest';

import {
  EMPTY_TRANSCRIPT,
  buildTranscript,
  joinFinal,
  normaliseFinal,
} from '../core/transcript';
import type { Segment } from '../types';

function seg(text: string, isFinal: boolean, id = text): Segment {
  return { id, text, isFinal, startedAt: 0 };
}

describe('transcript helpers', () => {
  it('joinFinal skips interim and trims whitespace', () => {
    const out = joinFinal([
      seg('Hello.', true, 'a'),
      seg('  world  ', true, 'b'),
      seg('partial', false, 'c'),
    ]);
    expect(out).toBe('Hello. world');
  });

  it('buildTranscript exposes trailing interim text', () => {
    const t = buildTranscript([
      seg('Hi.', true, 'a'),
      seg('there', false, 'b'),
    ]);
    expect(t.final).toBe('Hi.');
    expect(t.interim).toBe('there');
    expect(t.segments).toHaveLength(2);
  });

  it('buildTranscript with only finals leaves interim empty', () => {
    const t = buildTranscript([seg('Done.', true)]);
    expect(t.interim).toBe('');
    expect(t.final).toBe('Done.');
  });

  it('EMPTY_TRANSCRIPT is the zero value', () => {
    expect(EMPTY_TRANSCRIPT.interim).toBe('');
    expect(EMPTY_TRANSCRIPT.final).toBe('');
    expect(EMPTY_TRANSCRIPT.segments).toEqual([]);
  });

  it('normaliseFinal collapses whitespace and fixes punctuation spacing', () => {
    expect(normaliseFinal('  hello   world  ')).toBe('hello world');
    expect(normaliseFinal('Hi , there !')).toBe('Hi, there!');
    expect(normaliseFinal('one\ntwo\tthree')).toBe('one two three');
  });
});
