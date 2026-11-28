import { describe, expect, it } from 'vitest';

import type { DataPart, ReasoningPart, ToolPart } from '../../chat/core';
import { readTraceData } from '../../chat/core';

import fixtures from './fixtures/events-trace.json' with { type: 'json' };
import { decodeFrame } from './frames';
import { decodeStep, stepPart, storedTraceParts } from './trace';

const raw = (over: Record<string, unknown> = {}) => ({ v: 1, step_id: 's1', seq: 1, kind: 'tool', status: 'ok', name: 'kb_search', redaction: 'none', ...over });

describe('the recorded trace fixture', () => {
  it('decodes every frame to its own type, the resume `run` included', () => {
    for (const frame of fixtures.frames) expect(decodeFrame(frame)?.type, JSON.stringify(frame)).toBe(frame.type);
  });

  it('carries the SSE id of the frame onto the step as eventSeq', () => {
    const frame = decodeFrame(fixtures.frames[0]);
    expect(frame?.type === 'trace_step' ? [frame.event_seq, frame.step.meta.eventSeq] : null).toEqual([3, 3]);
  });
});

describe('decodeStep fails closed', () => {
  // MUTANT: read `args` / `result` whatever `redaction` says -> an omitted step leaks its detail.
  it('keeps no detail on an omitted step, even when the server sent some', () => {
    const step = decodeStep(raw({ redaction: 'omitted', args: { q: 'secret' }, result: { preview: 'secret', size: 6 }, purpose: 'p', query: 'q', refs: [{ kind: 'email', id: '1' }] }));
    expect(step?.meta).toMatchObject({ redaction: 'omitted' });
    for (const key of ['argsView', 'resultView', 'purpose', 'query', 'sources']) expect(step?.meta).not.toHaveProperty(key);
  });

  it('reads an unknown or absent redaction as omitted', () => {
    expect(decodeStep(raw({ redaction: 'shiny', args: { q: 1 } }))?.meta.redaction).toBe('omitted');
    const { redaction: _drop, ...noRedaction } = raw({ args: { q: 1 } });
    expect(decodeStep(noRedaction)?.meta).toMatchObject({ redaction: 'omitted' });
    expect(decodeStep(noRedaction)?.meta).not.toHaveProperty('argsView');
  });

  it('reads an unknown status as skipped, and drops a step with no id or kind', () => {
    expect(decodeStep(raw({ status: 'exploded' }))?.meta.status).toBe('skipped');
    expect(decodeStep(raw({ step_id: undefined }))).toBeNull();
    expect(decodeStep(raw({ kind: undefined }))).toBeNull();
    expect(decodeStep('nope')).toBeNull();
  });

  it('keeps the detail the server sent for a masked or open step, bounded', () => {
    const step = decodeStep(raw({ redaction: 'masked', args: { q: 'a***' }, args_size: 12, result: { preview: 'x'.repeat(5000), size: 5000, truncated: true }, refs: Array.from({ length: 30 }, (_, i) => ({ kind: 'k', id: String(i) })) }));
    expect(step?.meta.argsView).toEqual({ q: 'a***' });
    expect(step?.meta.resultView).toHaveLength(2000);
    expect(step?.meta).toMatchObject({ argsBytes: 12, resultBytes: 5000, truncated: true });
    expect(step?.meta.sources).toHaveLength(20);
  });
});

describe('stepPart maps a step to the part the chat already draws', () => {
  it('a running tool is an open call, an ok one has its preview, a failed one is an error with no text', () => {
    const running = stepPart('m', decodeStep(raw({ status: 'running' }))!) as ToolPart;
    expect([running.id, running.toolState.state]).toEqual(['m:s1', 'input-available']);
    const ok = stepPart('m', decodeStep(raw({ result: { preview: 'found 3', size: 7 } }))!) as ToolPart;
    expect(ok.toolState).toMatchObject({ state: 'output-available', output: 'found 3' });
    for (const status of ['error', 'timeout', 'denied', 'cancelled']) {
      const part = stepPart('m', decodeStep(raw({ status }))!) as ToolPart;
      expect(part.toolState, status).toMatchObject({ state: 'output-error', error: '' });
      expect(part.meta?.status).toBe(status);
    }
  });

  it('a reasoning step is a hidden thought with its token count', () => {
    const part = stepPart('m', decodeStep(raw({ kind: 'reasoning', name: 'reasoning', tokens: { reasoning: 120 }, duration_ms: 900 }))!) as ReasoningPart;
    expect(part).toMatchObject({ type: 'reasoning', text: '', streaming: false, tokens: 120, elapsedMs: 900 });
    expect(part.meta?.hidden).toBe(true);
  });

  it('any other kind is a trace data part', () => {
    const part = stepPart('m', decodeStep(raw({ kind: 'usage', name: 'usage' }))!) as DataPart;
    expect(part.type).toBe('data');
    expect(readTraceData(part)).toMatchObject({ kind: 'usage' });
  });
});

describe('storedTraceParts', () => {
  const doc = (steps: unknown[], extra: Record<string, unknown> = {}) => ({ v: 1, steps, steps_count: steps.length, ...extra });

  it('restores the steps in the order they started and settles a running one', () => {
    const parts = storedTraceParts('m', doc([raw({ step_id: 's2', seq: 2 }), raw({ step_id: 's1', seq: 1, status: 'running' })]));
    expect(parts.map((p) => p.id)).toEqual(['m:s1', 'm:s2']);
    expect((parts[0] as ToolPart).meta?.status).toBe('cancelled');
  });

  it('notes how many steps the stored document dropped', () => {
    const parts = storedTraceParts('m', doc([raw()], { steps_count: 80 }));
    expect(readTraceData(parts[1]!)).toMatchObject({ kind: 'note', name: 'truncated', omitted: 79 });
  });

  it('restores nothing for a null, absent or malformed trace', () => {
    expect(storedTraceParts('m', null)).toEqual([]);
    expect(storedTraceParts('m', undefined)).toEqual([]);
    expect(storedTraceParts('m', { steps: 'x' } as never)).toEqual([]);
  });
});
