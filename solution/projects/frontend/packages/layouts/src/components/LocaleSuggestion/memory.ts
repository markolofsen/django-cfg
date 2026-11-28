import { CFG_KEYS, cfgStorage } from '@djangocfg/api/storage';

import { emptyMemory, type SuggestionMemory } from './decide';

const SPEC = CFG_KEYS.uiLocaleHint;

/** The stored memory; anything malformed reads as empty and is overwritten on the next write. */
export function readMemory(): SuggestionMemory {
  const raw = cfgStorage.readJSON<unknown>(SPEC.key, SPEC.store);
  if (!raw || typeof raw !== 'object') return emptyMemory();
  const { seen, dismissed } = raw as { seen?: unknown; dismissed?: unknown };
  const pairs: Record<string, number> = {};
  if (dismissed && typeof dismissed === 'object') {
    for (const [key, at] of Object.entries(dismissed)) {
      if (typeof at === 'number' && Number.isFinite(at)) pairs[key] = at;
    }
  }
  return { v: 1, seen: typeof seen === 'string' ? seen : undefined, dismissed: pairs };
}

export function writeMemory(memory: SuggestionMemory): void {
  cfgStorage.writeJSON(SPEC.key, memory, SPEC.store);
}
