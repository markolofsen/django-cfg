'use client';

import { useEffect } from 'react';
import { Options as HotkeysOptions, useHotkeys } from 'react-hotkeys-hook';
import type { HotkeyCallback, Keys } from 'react-hotkeys-hook';

import { registerHotkey } from './useHotkeyHelp';

/** Ref type for hotkey target element */
export type HotkeyRefType<T> = T | null;

/**
 * Options for the useHotkey hook.
 *
 * Most of the time you only need `{ inInput }` or nothing — sensible
 * defaults are derived from the key combo (see below).
 */
export interface UseHotkeyOptions extends Omit<HotkeysOptions, 'enabled'> {
  /** Whether the hotkey is enabled (default: true) */
  enabled?: boolean;
  /** Scope for the hotkey — useful for context-specific shortcuts */
  scope?: string;
  /** Only trigger when focus is within a specific element */
  scopes?: string[];
  /** Prevent default browser behavior */
  preventDefault?: boolean;
  /**
   * Whether the shortcut should also fire when focus is inside an input,
   * textarea, select, or contenteditable element.
   *
   * Default policy (when not specified):
   *   - Modifier-bearing combos (`cmd+*`, `ctrl+*`, `alt+*`, `shift+*`)
   *     → `true`. Global app shortcuts (⌘K, Ctrl+S, ⌘/) must work no
   *     matter where the user is.
   *   - `escape` → `true`. Escape semantics (blur / close) are universal.
   *   - Bare single-character keys (`/`, `?`, `j`, …) → `false`. They
   *     would otherwise eat keystrokes the user is typing into inputs.
   *   - Function keys, arrows, etc. → `false`.
   *
   * Pass `true` or `false` explicitly to override.
   */
  inInput?: boolean;
  /**
   * @deprecated Use `inInput` instead. Forwarded to react-hotkeys-hook
   * when explicitly set; otherwise derived from `inInput` / policy.
   */
  enableOnFormTags?: boolean | readonly ('input' | 'textarea' | 'select')[];
  /**
   * @deprecated Use `inInput` instead. Same forwarding rules as
   * `enableOnFormTags`.
   */
  enableOnContentEditable?: boolean;
  /** Split key for multiple hotkey combinations (default: ',') */
  splitKey?: string;
  /** Key up/down events */
  keyup?: boolean;
  keydown?: boolean;
  /** Description for the hotkey (useful for help dialogs) */
  description?: string;
}

/**
 * Wrapper around react-hotkeys-hook with an opinionated `inInput` policy.
 *
 * @example
 * // ⌘K palette — works everywhere, including inside text fields
 * useHotkey('mod+k', openPalette);
 *
 * @example
 * // `/` focuses search — auto-disabled inside text fields so typing
 * // a `/` into a textarea doesn't yank focus away
 * useHotkey('/', focusSearch);
 *
 * @example
 * // Escape — defaults to fire in text fields too (blur / close pattern)
 * useHotkey('escape', closeModal);
 *
 * @example
 * // Explicit opt-in for a bare key inside inputs
 * useHotkey('?', openHelp, { inInput: true });
 */
export function useHotkey<T extends HTMLElement = HTMLElement>(
  keys: Keys,
  callback: HotkeyCallback,
  options: UseHotkeyOptions = {}
): (instance: HotkeyRefType<T>) => void {
  const {
    enabled = true,
    preventDefault: explicitPreventDefault,
    inInput,
    enableOnFormTags: explicitFormTags,
    enableOnContentEditable: explicitContentEditable,
    description,
    scope,
    ...restOptions
  } = options;

  const policyAllowsInInput = resolveInInput(keys, inInput);
  // Smart default — modifier combos preventDefault by default
  // (cmd+s, cmd+k, etc. would otherwise fall through to the browser).
  const preventDefault = explicitPreventDefault ?? hasModifier(keys);

  // Register in the cheat-sheet help registry when described.
  useEffect(() => {
    if (!description) return;
    return registerHotkey({
      combo: normalizeKeys(keys).join(','),
      description,
      scope,
    });
  }, [keys, description, scope]);

  const enableOnFormTags =
    explicitFormTags !== undefined ? explicitFormTags : policyAllowsInInput;
  const enableOnContentEditable =
    explicitContentEditable !== undefined ? explicitContentEditable : policyAllowsInInput;

  return useHotkeys<T>(
    keys,
    (event, handler) => {
      if (preventDefault) {
        event.preventDefault();
      }
      callback(event, handler);
    },
    {
      enabled,
      enableOnFormTags,
      enableOnContentEditable,
      ...restOptions,
    }
  );
}

/**
 * Decide whether a given key combo should fire when focus is inside a
 * text input. Honours the caller's explicit `inInput` first, otherwise
 * applies the policy described on `UseHotkeyOptions.inInput`.
 */
function resolveInInput(keys: Keys, explicit?: boolean): boolean {
  if (explicit !== undefined) return explicit;

  const list = normalizeKeys(keys);
  // If ANY of the listed combos qualifies as "input-safe", treat the
  // whole binding as input-safe — the caller declared them as
  // alternatives, so the more permissive policy wins.
  return list.some(isInputSafeByPolicy);
}

function normalizeKeys(keys: Keys): string[] {
  if (Array.isArray(keys)) return keys.map((k) => String(k).toLowerCase());
  return [String(keys).toLowerCase()];
}

const ESCAPE_ALIASES = new Set(['escape', 'esc']);
const MODIFIER_ALIASES = ['mod+', 'meta+', 'cmd+', 'ctrl+', 'control+', 'alt+', 'option+', 'shift+'];

function isInputSafeByPolicy(combo: string): boolean {
  if (ESCAPE_ALIASES.has(combo)) return true;
  return MODIFIER_ALIASES.some((mod) => combo.startsWith(mod));
}

/**
 * Does the combo include a modifier key? Used to default `preventDefault`
 * so global app shortcuts (⌘S, ⌘K, …) never fall through to the browser.
 */
function hasModifier(keys: Keys): boolean {
  return normalizeKeys(keys).some((combo) =>
    MODIFIER_ALIASES.some((mod) => combo.startsWith(mod)),
  );
}

// Re-export useful utilities from react-hotkeys-hook
export { useHotkeysContext, HotkeysProvider, isHotkeyPressed } from 'react-hotkeys-hook';

// Re-export types
export type { HotkeyCallback, Keys } from 'react-hotkeys-hook';
