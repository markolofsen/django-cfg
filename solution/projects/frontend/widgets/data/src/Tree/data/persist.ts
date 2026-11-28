'use client';

import { CFG_FAMILIES, cfgStorage } from '@djangocfg/api/storage';

import type { TreeItemId } from '../types';

const VERSION = 1;

export interface PersistedTreeState {
  expandedItems: TreeItemId[];
  selectedItems: TreeItemId[];
}

interface PersistedShape extends PersistedTreeState {
  version: number;
}

function safeStorage(): Storage | null {
  if (typeof window === 'undefined') return null;
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export function loadTreeState(key: string): PersistedTreeState | null {
  const storage = safeStorage();
  if (!storage) return null;
  try {
    const raw = storage.getItem(cfgStorage.familyKey(CFG_FAMILIES.dataTree, key));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<PersistedShape>;
    if (parsed.version !== VERSION) return null;
    return {
      expandedItems: Array.isArray(parsed.expandedItems) ? parsed.expandedItems : [],
      selectedItems: Array.isArray(parsed.selectedItems) ? parsed.selectedItems : [],
    };
  } catch {
    return null;
  }
}

export function saveTreeState(key: string, state: PersistedTreeState): void {
  const storage = safeStorage();
  if (!storage) return;
  try {
    const payload: PersistedShape = { ...state, version: VERSION };
    storage.setItem(cfgStorage.familyKey(CFG_FAMILIES.dataTree, key), JSON.stringify(payload));
  } catch {
    /* quota / serialization — best-effort persistence */
  }
}

export function clearTreeState(key: string): void {
  const storage = safeStorage();
  if (!storage) return;
  try {
    storage.removeItem(cfgStorage.familyKey(CFG_FAMILIES.dataTree, key));
  } catch {
    /* ignore */
  }
}
