import type { ReactNode } from 'react';

import { PANEL_TITLE_CLASS } from '../../../chat/ui';

import { AssistantHelp } from './assistant-help';

/** What a host may put in the header's title slot: the title is the default; a segment control, a count beside the title or any node replaces it. */
export function headingNode(heading: ReactNode | undefined, title: string): ReactNode {
  return heading ?? <h2 className={PANEL_TITLE_CLASS}>{title}</h2>;
}

/**
 * The header controls before Close: the round Help `?` (default), then the host's actions. `help={false}` or `null` leaves Help out (a call has no dictation and no toggle key, so the list would be wrong);
 * a node replaces it. With Help out and no actions the header draws no divider.
 */
export function headerActions(help: ReactNode | false | undefined, actions: ReactNode): ReactNode {
  const helpNode = help === undefined ? <AssistantHelp /> : help || null;
  if (!helpNode && !actions) return undefined;
  return (
    <>
      {helpNode}
      {actions}
    </>
  );
}
