// Offline: no network
import assert from 'node:assert/strict';
import { test } from 'vitest';

import type { StoredConversation, StoredThread } from '../../wire/stored';
import { ThreadNotFoundError } from '../../wire/transport';
import { NO_SESSION, relativeTime, restoreSession, type SessionStorage, type ThreadApi } from './sessions';

const signal = new AbortController().signal;
const thread = (id: string): StoredThread => ({ id, title: id, last_message_at: '2026-11-05T10:00:00Z', message_count: 2 });
const conversation = (id: string): StoredConversation => ({ id, messages: [] });

function fakeApi(known: string[], listed: string[] = known): ThreadApi & { loads: string[]; lists: number; created: number } {
  const api = {
    loads: [] as string[],
    lists: 0,
    created: 0,
    async list() {
      api.lists += 1;
      return listed.map(thread);
    },
    async create() {
      api.created += 1;
      return thread('fresh');
    },
    async load(id: string) {
      api.loads.push(id);
      if (!known.includes(id)) throw new ThreadNotFoundError();
      return conversation(id);
    },
  };
  return api;
}

function memory(initial: string | null): SessionStorage & { value: string | null } {
  const store = { value: initial, read: () => store.value, write: (id: string | null) => void (store.value = id) };
  return store;
}

test('the remembered session is shown; nothing is listed or created', async () => {
  const api = fakeApi(['a', 'b'], ['b', 'a']);
  const result = await restoreSession({ api, storage: memory('a'), signal });
  assert.equal(result.id, 'a');
  assert.deepEqual([api.loads, api.lists, api.created], [['a'], 0, 0]);
});

test('with nothing remembered the newest session is shown', async () => {
  const api = fakeApi(['a', 'b'], ['b', 'a']);
  assert.equal((await restoreSession({ api, storage: memory(null), signal })).id, 'b');
});

test('a remembered session that is gone is forgotten and the newest takes over', async () => {
  const storage = memory('stranger');
  const api = fakeApi(['a'], ['a']);
  assert.equal((await restoreSession({ api, storage, signal })).id, 'a');
  assert.equal(storage.value, null);
});

test('a viewer with no session gets the blank page and nothing is created on load', async () => {
  const api = fakeApi([]);
  assert.deepEqual(await restoreSession({ api, signal }), NO_SESSION);
  assert.equal(api.created, 0);
});

test('any other failure is not swallowed', async () => {
  const api = { ...fakeApi([]), load: async () => { throw new Error('network'); } };
  await assert.rejects(restoreSession({ api, storage: memory('a'), signal }), /network/);
});

test('relative time is worded in the viewer language, "now" under a minute', () => {
  const now = Date.parse('2026-11-05T12:00:00Z');
  assert.equal(relativeTime('2026-11-05T11:55:00Z', 'en', now), '5 minutes ago');
  assert.equal(relativeTime('2026-11-05T09:00:00Z', 'en', now), '3 hours ago');
  assert.equal(relativeTime('2026-11-04T12:00:00Z', 'en', now), 'yesterday');
  assert.equal(relativeTime('2026-11-05T11:59:40Z', 'en', now), 'now');
  assert.equal(relativeTime('2026-11-05T11:55:00Z', 'ru', now), '5 минут назад');
});
