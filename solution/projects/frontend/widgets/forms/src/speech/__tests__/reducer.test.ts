import { describe, expect, it } from 'vitest';

import { INITIAL_STATE, reducer } from '../core/reducer';

describe('SpeechRecognition reducer', () => {
  it('starts and finishes a session', () => {
    const s1 = reducer(INITIAL_STATE, { type: 'START' });
    expect(s1.status).toBe('starting');
    expect(s1.startedAt).toBeTypeOf('number');
    expect(s1.error).toBeNull();

    const s2 = reducer(s1, { type: 'STARTED' });
    expect(s2.status).toBe('listening');

    const s3 = reducer(s2, { type: 'STOP' });
    expect(s3.status).toBe('stopping');

    const s4 = reducer(s3, { type: 'STOPPED' });
    expect(s4.status).toBe('idle');
  });

  it('merges PARTIAL into an interim segment, then promotes to FINAL', () => {
    let s = reducer(INITIAL_STATE, { type: 'START' });
    s = reducer(s, { type: 'STARTED' });
    s = reducer(s, { type: 'PARTIAL', text: 'hel', segmentId: 'seg-1' });
    s = reducer(s, { type: 'PARTIAL', text: 'hello', segmentId: 'seg-1' });
    expect(s.segments).toHaveLength(1);
    expect(s.segments[0]).toMatchObject({
      id: 'seg-1',
      text: 'hello',
      isFinal: false,
    });

    s = reducer(s, { type: 'FINAL', text: 'hello world', segmentId: 'seg-1', confidence: 0.91 });
    expect(s.segments).toHaveLength(1);
    expect(s.segments[0]).toMatchObject({
      id: 'seg-1',
      text: 'hello world',
      isFinal: true,
      confidence: 0.91,
    });
  });

  it('accumulates separate segments', () => {
    let s = reducer(INITIAL_STATE, { type: 'START' });
    s = reducer(s, { type: 'FINAL', text: 'one', segmentId: 'a' });
    s = reducer(s, { type: 'FINAL', text: 'two', segmentId: 'b' });
    s = reducer(s, { type: 'PARTIAL', text: 'thr', segmentId: 'c' });
    expect(s.segments.map((seg) => seg.text)).toEqual(['one', 'two', 'thr']);
    expect(s.segments.map((seg) => seg.isFinal)).toEqual([true, true, false]);
  });

  it('records errors and resets cleanly', () => {
    let s = reducer(INITIAL_STATE, { type: 'START' });
    s = reducer(s, {
      type: 'ERROR',
      error: { code: 'no-speech', message: 'no speech' },
    });
    expect(s.status).toBe('error');
    expect(s.error?.code).toBe('no-speech');

    const reset = reducer(s, { type: 'RESET' });
    expect(reset).toEqual(INITIAL_STATE);
  });

  it('ignores unknown actions', () => {
    // @ts-expect-error - intentionally invalid for the default branch
    const next = reducer(INITIAL_STATE, { type: 'NOPE' });
    expect(next).toBe(INITIAL_STATE);
  });
});
