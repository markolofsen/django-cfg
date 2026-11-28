'use client';

// Everything that remembers a value between renders, visits or tabs:
//   useLocalStorage / useSessionStorage — one key, validated on read, healed when broken
//   useStoredValue                       — the `storageKey` prop of form components
//   storage-namespace                    — the key scheme (`<owner>.<area>.<name>`) and its cleanup
//   storage-quota                        — recovery when the browser's quota is full
// The decoding rule shared with `@djangocfg/api` lives in `@djangocfg/api/storage` (`decodeStored`).

export { useLocalStorage } from './useLocalStorage';
export type { UseLocalStorageOptions, UseLocalStorageReturn } from './useLocalStorage';
export { useSessionStorage } from './useSessionStorage';
export type {
  UseSessionStorageOptions,
  UseSessionStorageReturn,
} from './useSessionStorage';
export { useStoredValue } from './useStoredValue';
export type {
  UseStoredValueOptions,
  UseStoredValueReturn,
  StorageType,
} from './useStoredValue';
export {
  DEFAULT_STORAGE_NAMESPACE,
  StorageNamespaceProvider,
  useStorageNamespace,
  resolveStorageKey,
  isSchemeKey,
  listStorageKeys,
  clearStorageNamespace,
  createStorageNamespace,
} from './storage-namespace';
export type {
  StorageNamespace,
  StorageNamespaceProviderProps,
  StorageArea,
  ClearStorageOptions,
} from './storage-namespace';
