import assert from 'node:assert/strict';
import { test } from 'node:test';

import { parseSecrets, signClearance, verifyClearance } from './cookie';

const UA = 'Mozilla/5.0 test';

test('a signed cookie verifies for the same UA', async () => {
  const c = await signClearance('s1', UA, 60, 1_000_000);
  assert.ok(await verifyClearance(['s1'], c, UA, 1_000_000 + 30_000));
});

test('tampered payload, other UA, expiry, wrong secret and junk are rejected', async () => {
  const c = await signClearance('s1', UA, 60, 1_000_000);
  const [v = '', body = '', sig = ''] = c.split('.');
  const forged = `${v}.${body.slice(0, -2)}AA.${sig}`;
  assert.ok(!(await verifyClearance(['s1'], forged, UA, 1_000_000)));
  assert.ok(!(await verifyClearance(['s1'], c, 'curl/8', 1_000_000)));
  assert.ok(!(await verifyClearance(['s1'], c, UA, 1_000_000 + 61_000)));
  assert.ok(!(await verifyClearance(['other'], c, UA, 1_000_000)));
  for (const junk of [undefined, '', 'v1.x', 'v2.a.b', 'a.b.c']) assert.ok(!(await verifyClearance(['s1'], junk, UA, 1_000_000)));
  assert.ok(!(await verifyClearance([], c, UA, 1_000_000)), 'no secret never passes');
});

test('secret rotation: old cookies verify while the first secret signs', async () => {
  const old = await signClearance('old', UA, 60, 1_000_000);
  assert.ok(await verifyClearance(parseSecrets('new, old'), old, UA, 1_000_000));
  assert.deepEqual(parseSecrets(' a ,b,, '), ['a', 'b']);
});
