import assert from 'node:assert/strict';
import { renderToStaticMarkup } from 'react-dom/server';
import { test } from 'vitest';

import { columnLimit } from './panel-state';
import { headerActions, headingNode } from './header-slots';

test('the column keeps the stage: the cap, or the room the page can spare', () => {
  const base = { minWidth: 320, maxWidth: 560 };
  assert.equal(columnLimit({ ...base, viewport: 1280 }), 560, 'no floor: the cap');
  assert.equal(columnLimit({ ...base, viewport: 1024, stageMin: 480 }), 544, '1024 - 480');
  assert.equal(columnLimit({ ...base, viewport: 1440, stageMin: 480 }), 560, 'the cap wins when there is room');
  assert.equal(columnLimit({ ...base, viewport: 700, stageMin: 480 }), 320, 'never below the minimum');
  assert.equal(columnLimit({ ...base, viewport: 0, stageMin: 480 }), 560, 'width unknown (server): the cap');
});

test('the heading slot defaults to the title and yields to the host', () => {
  assert.match(renderToStaticMarkup(<>{headingNode(undefined, 'Chat')}</>), /<h2[^>]*>Chat<\/h2>/);
  assert.equal(renderToStaticMarkup(<>{headingNode(<b>People</b>, 'Chat')}</>), '<b>People</b>');
});

test('Help can be left out, and then an empty header has no controls to divide', () => {
  assert.equal(headerActions(false, null), undefined);
  assert.equal(headerActions(null, undefined), undefined);
  assert.equal(renderToStaticMarkup(<>{headerActions(false, <i>menu</i>)}</>), '<i>menu</i>');
  assert.equal(renderToStaticMarkup(<>{headerActions(<u>help</u>, <i>menu</i>)}</>), '<u>help</u><i>menu</i>');
});
