'use client';

import type { Action, State } from './types';

/**
 * Pure reducer for `<TreeProvider>`. Intentionally small — most domain
 * logic (Finder selection rules, async cache, persistence) lives in
 * dedicated hooks under `context/<feature>/` and only dispatches one of
 * these actions when the result needs to land in React state.
 */
export function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'expand': {
      if (state.expanded.has(action.id)) return state;
      const next = new Set(state.expanded);
      next.add(action.id);
      return { ...state, expanded: next };
    }
    case 'collapse': {
      if (!state.expanded.has(action.id)) return state;
      const next = new Set(state.expanded);
      next.delete(action.id);
      return { ...state, expanded: next };
    }
    case 'toggle': {
      const next = new Set(state.expanded);
      if (next.has(action.id)) next.delete(action.id);
      else next.add(action.id);
      return { ...state, expanded: next };
    }
    case 'set-expanded':
      return { ...state, expanded: new Set(action.ids) };
    case 'select': {
      if (action.mode === 'none') return state;
      if (action.mode === 'single') {
        return {
          ...state,
          selected: new Set([action.id]),
          anchor: action.id,
          focused: action.id,
        };
      }
      const next = new Set(state.selected);
      if (next.has(action.id)) next.delete(action.id);
      else next.add(action.id);
      return { ...state, selected: next, anchor: action.id, focused: action.id };
    }
    case 'select-many':
      return { ...state, selected: new Set(action.ids) };
    case 'clear-selection':
      return { ...state, selected: new Set(), anchor: null };
    case 'selection-replace':
      return {
        ...state,
        selected: new Set(action.selected),
        anchor: action.anchor,
        focused: action.focused,
      };
    case 'set-anchor':
      return { ...state, anchor: action.id };
    case 'focus':
      return { ...state, focused: action.id };
    case 'set-query':
      return { ...state, query: action.q };
    case 'start-rename':
      return { ...state, renaming: action.id };
    case 'stop-rename':
      return state.renaming === null ? state : { ...state, renaming: null };
    case 'clipboard-set':
      return { ...state, clipboard: action.payload };
    case 'cache-tick':
      return { ...state, cacheTick: state.cacheTick + 1 };
    default:
      return state;
  }
}
