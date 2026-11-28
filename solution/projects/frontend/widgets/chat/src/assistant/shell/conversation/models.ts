import { useMemo } from 'react';

import type { ModelOption } from '../../../chat/core';

import { useAssistantCopy } from '../../../i18n/assistant';
import type { Locale } from '@djangocfg/i18n/copy';

/**
 * Starter aliases for the composer's model switch (`AssistantChat models`), in the reader's language. They are names of intent, not of models: what `fast` or `smart` runs is the host's backend to decide,
 * so the same list works on any server that reads the `model` field of the request body. The ids are fixed (`auto`, `fast`, `smart`); only the labels follow the language. Pass your own list instead for other aliases.
 */
export function useModelAliases(locale?: Locale): readonly ModelOption[] {
  const copy = useAssistantCopy(locale);
  return useMemo(
    () => [
      { id: 'auto', label: copy.modelAuto, hint: copy.modelAutoHint },
      { id: 'fast', label: copy.modelFast, hint: copy.modelFastHint },
      { id: 'smart', label: copy.modelSmart, hint: copy.modelSmartHint },
    ],
    [copy],
  );
}

/** The alias a switch starts on. */
export const DEFAULT_MODEL = 'auto';
