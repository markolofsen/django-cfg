import { describe, expect, it } from 'vitest';

import { fillText, nextStep, type Step } from './model';

describe('text', () => {
  it('fills {placeholders} and leaves unknown ones', () => {
    expect(fillText('Last renewed {when} {x}', { when: 'today' })).toBe('Last renewed today {x}');
  });
});

describe('the confirm step', () => {
  const run = (events: Parameters<typeof nextStep>[1][]): Step => events.reduce<Step>(nextStep, 'idle');
  it('asks, confirms, finishes', () => expect(run(['ask', 'start', 'done'])).toBe('idle'));
  it('keeps: back to the button with nothing sent', () => expect(run(['ask', 'keep'])).toBe('idle'));
  it('cannot confirm without asking first', () => expect(run(['start'])).toBe('idle'));
  it('a failure shows once and the action can be asked again', () => {
    expect(run(['ask', 'start', 'fail'])).toBe('failed');
    expect(run(['ask', 'start', 'fail', 'ask'])).toBe('asking');
  });
  it('ignores a second press while busy', () => expect(run(['ask', 'start', 'start', 'ask'])).toBe('busy'));
});
