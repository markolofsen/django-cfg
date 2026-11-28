'use client';

import { CircleHelp } from 'lucide-react';

import { Kbd, Popover, PopoverContent, PopoverTrigger } from '@djangocfg/ui-core/components';
import { formatHotkey, useIsTouch } from '@djangocfg/ui-core/hooks';
import { PanelIconButton } from '../../../chat/ui';

import { useAssistantCopy } from '../../../i18n/assistant';
import { ASSISTANT_TOGGLE, DICTATION_TOGGLE } from '../composer/keys';

/** One line of the list: `combo` is a hotkey string, drawn for the viewer's system (⌘ on Apple, Ctrl elsewhere). */
export interface HelpRow {
  combo: string;
  text: string;
}

/** The keys the composer answers to, in the order a person needs them. A host without dictation or the toggle key filters or replaces them (`AssistantHelp rows`). */
export function useHelpRows(): HelpRow[] {
  const copy = useAssistantCopy();
  return [
    { combo: ASSISTANT_TOGGLE, text: copy.helpToggle },
    { combo: DICTATION_TOGGLE, text: copy.helpDictate },
    { combo: 'enter', text: copy.helpSend },
    { combo: 'escape', text: copy.helpStop },
    { combo: 'arrowup', text: copy.helpRecall },
    { combo: 'shift+enter', text: copy.helpNewline },
  ];
}

/** A round "?" in the assistant's header, before its other actions; pressing it opens the short list of keys the composer answers to (`rows`: the host's own list). */
export function AssistantHelp({ rows: given }: { rows?: readonly HelpRow[] }) {
  const copy = useAssistantCopy();
  const own = useHelpRows();
  const rows = given ?? own;
  const touch = useIsTouch();
  // The keys are a desktop keyboard's: a phone has none of them.
  if (touch) return null;
  return (
    <Popover>
      <PopoverTrigger asChild>
        <PanelIconButton label={copy.helpLabel}>
          <CircleHelp className="size-4" aria-hidden />
        </PanelIconButton>
      </PopoverTrigger>
      <PopoverContent side="bottom" align="end" className="w-72 p-3">
        <ul className="space-y-2">
          {rows.map(({ combo, text }) => (
            <li key={combo} className="flex items-start justify-between gap-3 text-sm">
              <span className="text-muted-foreground">{text}</span>
              <Kbd className="shrink-0">{formatHotkey(combo)}</Kbd>
            </li>
          ))}
        </ul>
      </PopoverContent>
    </Popover>
  );
}
