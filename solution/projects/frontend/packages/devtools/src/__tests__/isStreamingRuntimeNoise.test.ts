import { describe, expect, it } from 'vitest';

import { isStreamingRuntimeNoise } from '../capture';

/**
 * React's inline streaming scripts fail only when something outside the app
 * removed the hidden segment first. The stacks below are verbatim from
 * carapis.com's monitor log, 2026-09-23.
 */
describe('isStreamingRuntimeNoise', () => {
  it('drops a $RS failure', () => {
    const stack =
      "TypeError: Cannot read properties of null (reading 'parentNode')\n" +
      '    at $RS (https://carapis.com/catalog/genesis/eq900/c2d25771/:2:3330)\n' +
      '    at https://carapis.com/catalog/genesis/eq900/c2d25771/:3:77605';
    expect(isStreamingRuntimeNoise(stack)).toBe(true);
  });

  it('drops a $RC failure', () => {
    expect(
      isStreamingRuntimeNoise("TypeError: x\n    at $RC (https://a.test/:2:10)\n    at https://a.test/:9:1"),
    ).toBe(true);
  });

  it('keeps an app error whose top frame is the app', () => {
    const stack =
      "TypeError: Cannot read properties of null (reading 'parentNode')\n" +
      '    at Gallery (https://carapis.com/_next/static/chunks/abc.js:1:200)\n' +
      '    at $RS (https://carapis.com/x/:2:3330)';
    expect(isStreamingRuntimeNoise(stack)).toBe(false);
  });

  it('keeps an app function that merely starts with $R', () => {
    expect(isStreamingRuntimeNoise('Error\n    at $Router (https://a.test/app.js:1:1)')).toBe(false);
  });

  it('keeps an event with no stack', () => {
    expect(isStreamingRuntimeNoise(undefined)).toBe(false);
    expect(isStreamingRuntimeNoise('')).toBe(false);
  });
});
