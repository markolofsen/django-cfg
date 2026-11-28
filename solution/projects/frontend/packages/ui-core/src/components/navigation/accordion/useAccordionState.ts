'use client';

import * as React from 'react';

import { useUIPersistedState } from '../../../lib/persist';

const SCOPE_SINGLE = 'accordion:single';
const SCOPE_MULTIPLE = 'accordion:multiple';

export interface UseAccordionSingleResult {
  /** Currently open item id, or empty string if all closed. */
  value: string;
  setValue: (next: string) => void;
  reset: () => void;
}

export interface UseAccordionMultipleResult {
  /** List of open item ids. */
  value: string[];
  setValue: (next: string[]) => void;
  reset: () => void;
}

/**
 * Persist a single-mode Accordion's open item.
 *
 * @example
 * const { value, setValue } = useAccordionSingleState('sidebar-groups');
 * <Accordion type="single" value={value} onValueChange={setValue}>...</Accordion>
 */
export function useAccordionSingleState(
  key: string,
  defaultValue = '',
): UseAccordionSingleResult {
  const sanitize = React.useCallback(
    (raw: string) => (typeof raw === 'string' ? raw : undefined),
    [],
  );
  const persisted = useUIPersistedState<string>(SCOPE_SINGLE, key, defaultValue, { sanitize });
  return {
    value: persisted.value,
    setValue: persisted.setValue,
    reset: persisted.reset,
  };
}

/**
 * Persist a multiple-mode Accordion's open items.
 *
 * @example
 * const { value, setValue } = useAccordionMultipleState('sidebar-groups', ['general']);
 * <Accordion type="multiple" value={value} onValueChange={setValue}>...</Accordion>
 */
export function useAccordionMultipleState(
  key: string,
  defaultValue: string[] = [],
): UseAccordionMultipleResult {
  const sanitize = React.useCallback(
    (raw: string[]) =>
      Array.isArray(raw) && raw.every((v) => typeof v === 'string') ? raw : undefined,
    [],
  );
  const persisted = useUIPersistedState<string[]>(SCOPE_MULTIPLE, key, defaultValue, { sanitize });
  return {
    value: persisted.value,
    setValue: persisted.setValue,
    reset: persisted.reset,
  };
}
