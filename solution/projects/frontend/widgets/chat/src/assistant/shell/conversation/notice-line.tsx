'use client';

import { Button } from '@djangocfg/ui-core/components';

import { useAssistantCopy, type SessionNotice } from '../../../i18n/assistant';

interface Props {
  notice: SessionNotice;
  onRetry?: () => void;
}

/** The plain line above the composer when the connection dropped (`reconnecting`) or an answer is still running past its budget (`stalled`, with Retry). */
export function NoticeLine({ notice, onRetry }: Props) {
  const copy = useAssistantCopy();
  return (
    <div role="status" className="px-4 pb-2 text-xs text-muted-foreground">
      {notice === 'reconnecting' ? (
        copy.reconnecting
      ) : (
        <span className="inline-flex items-center gap-2">
          {copy.stalled}
          {onRetry ? (
            <Button size="sm" variant="outline" onClick={onRetry}>
              {copy.retry}
            </Button>
          ) : null}
        </span>
      )}
    </div>
  );
}
