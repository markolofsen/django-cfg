import { describe, expect, it } from 'vitest';

import { mentionPresets } from './mentionPresets';

/**
 * A preset turns a mention into the TEXT that is sent, so a wrong one is not a
 * rendering bug — it is the wrong string on the wire, and the round trip back
 * into a chip fails somewhere else entirely.
 *
 * These assertions arrived as a hand-rolled script that printed PASS/FAIL and
 * called `process.exit`, written when the old ui-tools package had no runner. It had one, and
 * `vitest` reported it as a file with no suite: it had never run in CI.
 */

describe('plainAt', () => {
  it('prefixes the label', () => {
    expect(mentionPresets.plainAt({ label: 'Vps-audi', id: 'uuid' })).toBe('@Vps-audi');
  });

  it('falls back to the id when the label is empty', () => {
    expect(mentionPresets.plainAt({ label: '', id: 'uuid' })).toBe('@uuid');
  });
});

describe('plainLabel', () => {
  it('returns the label as-is', () => {
    expect(mentionPresets.plainLabel({ label: 'X', id: '1' })).toBe('X');
  });
});

describe('markdownLink', () => {
  const link = mentionPresets.markdownLink('https://x.com/u/');

  it('writes a link whose text is the label and whose href carries the id', () => {
    expect(link({ label: 'X Y', id: '1' })).toBe('[@X Y](https://x.com/u/1)');
  });

  it('escapes the markdown specials in the label', () => {
    // Unescaped, `A_B*C[D]` renders as emphasis and a broken link rather than
    // as the name someone picked.
    const out = link({ label: 'A_B*C[D]', id: 'id 2' });
    expect(out).toContain('\\_');
    expect(out).toContain('\\*');
    expect(out).toContain('\\[');
  });

  it('percent-encodes the id, which may contain a space', () => {
    expect(link({ label: 'A', id: 'id 2' })).toContain('id%202');
  });
});

describe('customUri', () => {
  it('writes the scheme the host parses back', () => {
    expect(mentionPresets.customUri('cmdop', 'machine')({ label: 'My Box', id: 'uuid' })).toBe(
      '@[My Box](cmdop://machine/uuid)',
    );
  });
});

describe('slackStyle', () => {
  it('drops the label — Slack resolves the id itself', () => {
    expect(mentionPresets.slackStyle({ label: 'X', id: 'U123' })).toBe('<@U123>');
  });
});

describe('htmlSpan', () => {
  it('carries the class and the id an app needs to re-hydrate the chip', () => {
    const out = mentionPresets.htmlSpan('m')({ label: 'X', id: '1' });
    expect(out).toContain('class="m"');
    expect(out).toContain('data-mention-id="1"');
    expect(out).toContain('@X');
  });
});
