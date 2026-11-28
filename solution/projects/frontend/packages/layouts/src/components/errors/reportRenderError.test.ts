import { beforeEach, describe, expect, it, vi } from 'vitest';

const capture = vi.fn();
const flush = vi.fn();
vi.mock('@djangocfg/devtools', () => ({
  EventLevel: { ERROR: 'error' },
  EventType: { ERROR: 'ERROR' },
  devtools: { capture: (...a: unknown[]) => capture(...a), flush: () => flush() },
}));

import { reportRenderError } from './reportRenderError';

describe('reportRenderError', () => {
  beforeEach(() => {
    capture.mockReset();
    flush.mockReset();
  });

  it('captures a render TypeError with its stack and component stack, then flushes', () => {
    const err = new TypeError("Cannot read properties of undefined (reading 'x')");
    reportRenderError('app', err, { componentStack: '\n in Page' } as never);
    expect(capture).toHaveBeenCalledTimes(1);
    const event = capture.mock.calls[0][0];
    expect(event.message).toContain('Cannot read properties');
    expect(event.stack_trace).toBe(err.stack);
    expect(event.extra).toMatchObject({ source: 'app', errorName: 'TypeError', componentStack: '\n in Page' });
    expect(flush).toHaveBeenCalledTimes(1);
  });

  it('never throws when devtools does', () => {
    capture.mockImplementation(() => {
      throw new Error('devtools down');
    });
    expect(() => reportRenderError('app', new Error('x'))).not.toThrow();
  });
});
