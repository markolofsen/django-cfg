import assert from 'node:assert/strict';
import { renderToStaticMarkup } from 'react-dom/server';
import { test } from 'vitest';

import type { PartRenderProps } from '../../chat/primitives';

import { KB_PAYLOAD_KINDS, KB_RENDERERS } from './kb-assistant';

const props = {} as PartRenderProps;

test('the example host draws a non-film payload and declares its kinds', () => {
  assert.deepEqual(KB_PAYLOAD_KINDS, ['citations']);
  const drawn = KB_RENDERERS.citations?.({ items: [{ n: 1, title: 'Refund policy', heading_path: ['Refund policy', 'Eligibility'] }] }, props);
  const html = renderToStaticMarkup(<>{drawn}</>);
  assert.match(html, /\[1\] Refund policy/);
  assert.match(html, /Eligibility/);
});

test('a malformed payload falls through to the widget (nothing drawn)', () => {
  assert.equal(KB_RENDERERS.citations?.({ nope: true }, props), undefined);
  assert.equal(KB_RENDERERS.citations?.({ items: [] }, props), undefined);
});
