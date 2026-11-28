import { useLocalStorage } from "@djangocfg/ui-core/hooks";
import { useCallback } from "react";

import { forgetTool, rememberTool } from "../../core";
import { CFG_KEYS } from "@djangocfg/api/storage";

const STORAGE_KEY = CFG_KEYS.chatRecentTools.key;

export interface RecentTools {
  readonly ids: readonly string[];
  readonly remember: (id: string) => void;
  readonly forget: (id: string) => void;
}

/**
 * The tools this user reaches for, newest first, across sessions.
 *
 * IDs only — names are resolved at read time, so a withdrawn tool cannot render
 * a dead row. One key across every room: the habit is the person's.
 */
export function useRecentTools(): RecentTools {
  const [ids, setIds] = useLocalStorage<readonly string[]>(STORAGE_KEY, [], {
    validate: (v): v is readonly string[] => Array.isArray(v) && v.every((id) => typeof id === 'string'),
  });

  const remember = useCallback(
    (id: string) => setIds((current) => rememberTool(current, id)),
    [setIds],
  );
  const forget = useCallback((id: string) => setIds((current) => forgetTool(current, id)), [setIds]);

  return { ids, remember, forget };
}
