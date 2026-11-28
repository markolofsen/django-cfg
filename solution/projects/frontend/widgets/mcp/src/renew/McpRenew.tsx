'use client';

import { useMemo, useState } from 'react';

import { useMcpCopy, useMcpLocale } from '../i18n';
import { ConfirmAction } from './ConfirmAction';
import { fillText } from './model';

export interface Renewal {
  /** When the key was last reissued (ISO), `null` when never. */
  reissuedAt: string | null;
  /** Rotates the user's key; the panel's commands switch to the new one. Throws on failure. */
  run: () => Promise<void>;
}

/**
 * What the panel does not show: one control, "Renew access" (disconnects every assistant, rotates the user's django-cfg API key).
 * Mount only for a signed-in user whose key is django-cfg's own.
 */
export function McpRenew({ renewal, className }: { renewal: Renewal; className?: string }) {
  const { renew: copy } = useMcpCopy();
  const locale = useMcpLocale();
  const date = useMemo(() => new Intl.DateTimeFormat(locale, { dateStyle: 'medium' }), [locale]);
  const [announcement, setAnnouncement] = useState('');

  const renew = async () => {
    try {
      await renewal.run();
      setAnnouncement(copy.renewedAnnounce);
      return true;
    } catch {
      return false;
    }
  };

  return (
    <div className={['flex flex-col gap-2 border-t border-border pt-3 text-start', className].filter(Boolean).join(' ')}>
      <span className="text-sm leading-5 text-muted-foreground">{copy.renewHint}</span>
      {renewal.reissuedAt ? (
        <span className="text-sm leading-5 text-muted-foreground">{fillText(copy.lastRenewed, { when: date.format(new Date(renewal.reissuedAt)) })}</span>
      ) : null}
      <ConfirmAction label={copy.renew} question={copy.renewConfirm} confirmLabel={copy.confirm} keepLabel={copy.keep} failed={copy.error} onConfirm={renew} />
      <span role="status" aria-live="polite" className="sr-only">
        {announcement}
      </span>
    </div>
  );
}
