import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, test } from 'node:test';

import { restoreVersionFiles, snapshotVersionFiles } from './workspace.mjs';

const tempDirs = [];

afterEach(() => {
  for (const dir of tempDirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

test('version snapshots restore package.json byte-for-byte', () => {
  const root = mkdtempSync(join(tmpdir(), 'djangocfg-publish-test-'));
  tempDirs.push(root);
  const first = join(root, 'first');
  const second = join(root, 'second');
  const files = [first, second].map((dir, index) => {
    const file = join(dir, 'package.json');
    const raw = `{\n  "name": "@test/${index}",\n  "version": "1.2.${index}",\n  "private": false\n}\n`;
    mkdirSync(dir, { recursive: true });
    writeFileSync(file, raw);
    return { file, raw, member: { dir } };
  });

  const snapshot = snapshotVersionFiles(files.map(({ member }) => member));
  for (const { file } of files) writeFileSync(file, readFileSync(file, 'utf8').replace('1.2.', '9.9.'));

  restoreVersionFiles(snapshot);

  for (const { file, raw } of files) assert.equal(readFileSync(file, 'utf8'), raw);
});
