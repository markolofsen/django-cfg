import assert from 'node:assert/strict';
import { test } from 'node:test';

// @ts-expect-error — Next's vendored copy ships no types; it is the matcher rewrites use.
import { pathToRegexp } from 'next/dist/compiled/path-to-regexp';

import { indexNowKeyRewrite } from './indexnow';

test('the rewrite matches a key at the root and nothing deeper', () => {
  const { source } = indexNowKeyRewrite('https://api.example.com');
  const re: RegExp = pathToRegexp(source, []);
  assert.ok(re.test('/865178f53dba1db23f3fc4fe95e9b64a.txt'));
  assert.ok(!re.test('/robots.txt'), 'under 8 chars is not a key');
  assert.ok(!re.test('/a/865178f53dba1db23f3fc4fe95e9b64a.txt'));
  assert.ok(!re.test('/has_underscore_.txt'));
});

test('the destination is Django, without a doubled slash', () => {
  assert.equal(
    indexNowKeyRewrite('https://api.example.com/').destination,
    'https://api.example.com/cfg/sitemap/indexnow/:key.txt',
  );
});
