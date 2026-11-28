import { describe, expect, it } from 'vitest';

import { formatConsoleArgs } from '../capture';

/**
 * What reaches the alert has to say what broke.
 *
 * consola styles its tag with `%c`, so one logger call arrives as
 * ["%capi:auth%c message", "<css>", "", err]. Joined on a space, the
 * stylesheet became the message and the truncation then cut the sentence that
 * mattered — the Telegram alert read "background: #c0392b; border-radius…".
 */
describe('formatConsoleArgs', () => {
  describe('the production case', () => {
    it('drops the stylesheet and keeps the sentence', () => {
      const css = '\n      background: #c0392b;\n      border-radius: 0.5em;\n      color: white;\n    ';
      const out = formatConsoleArgs([
        '%capi:auth:error%c Verify OTP failed:',
        css,
        '',
        new Error('HTTP 401: '),
      ]);
      // The trailing space is the Error's own message, not our formatting.
      expect(out).toBe('api:auth:error Verify OTP failed: HTTP 401: ');
      expect(out).not.toContain('background');
      expect(out).not.toContain('%c');
    });
  });

  describe('format specifiers', () => {
    it('substitutes %s', () => {
      expect(formatConsoleArgs(['hello %s', 'world'])).toBe('hello world');
    });

    it.each([
      ['%d', 42.9, '42'],
      ['%i', 42.9, '42'],
      ['%f', 1.5, '1.5'],
    ])('substitutes %s', (spec, input, expected) => {
      expect(formatConsoleArgs([`n=${spec}`, input])).toBe(`n=${expected}`);
    });

    it('serialises %o and %j', () => {
      expect(formatConsoleArgs(['%o', { a: 1 }])).toBe('{"a":1}');
      expect(formatConsoleArgs(['%j', { a: 1 }])).toBe('{"a":1}');
    });

    it('treats %% as a literal percent and consumes no argument', () => {
      expect(formatConsoleArgs(['100%% done %s', 'ok'])).toBe('100% done ok');
    });

    it('appends arguments the format string does not claim', () => {
      /* What the browser does with extras — dropping them would lose the
         error object, which is the only part worth reading. */
      expect(formatConsoleArgs(['%s:', 'ctx', 'detail', 42])).toBe('ctx: detail 42');
    });

    it('keeps an unmatched specifier rather than inventing a value', () => {
      expect(formatConsoleArgs(['a %s b %s', 'one'])).toBe('a one b %s');
    });
  });

  describe('when there is nothing to substitute', () => {
    it('joins plain arguments on a space, as before', () => {
      expect(formatConsoleArgs(['failed:', 'because'])).toBe('failed: because');
    });

    it('leaves a non-string first argument alone', () => {
      expect(formatConsoleArgs([{ a: 1 }, 'tail'])).toBe('{"a":1} tail');
    });

    it('uses an Error message, not its stringification', () => {
      expect(formatConsoleArgs(['boom:', new Error('the reason')])).toBe('boom: the reason');
    });

    it('survives a value JSON cannot serialise', () => {
      const cyclic: Record<string, unknown> = {};
      cyclic.self = cyclic;
      expect(() => formatConsoleArgs(['x', cyclic])).not.toThrow();
    });
  });

  describe('edge cases that must not throw', () => {
    it.each([[[]], [[undefined]], [[null]], [['%c']], [['%c', 'css']]])(
      'handles %j',
      (args) => {
        expect(() => formatConsoleArgs(args as unknown[])).not.toThrow();
      },
    );

    it('produces nothing but the tag when the message is only a style', () => {
      expect(formatConsoleArgs(['%ctag%c', 'css', ''])).toBe('tag');
    });
  });
});
