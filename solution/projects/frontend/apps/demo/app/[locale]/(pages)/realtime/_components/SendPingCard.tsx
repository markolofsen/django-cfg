'use client';

import { useState } from 'react';

import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle, Input } from '@djangocfg/ui-core';

import { useRealtimeDemoPingsSendCreate } from '@/api/generated/endpoints/realtime-demo/realtime-demo';
import { useAppTranslations } from '@i18n';

import type { FormEvent } from 'react';

/**
 * The generated POST mutation. The client adds `X-Realtime-Cid`, so neither
 * `demo.ping` nor the `demo.pings` hint comes back to this tab: `onSent`
 * refreshes the sender's own list.
 */
export function SendPingCard({ onSent }: { onSent: () => void }) {
  const { app } = useAppTranslations();
  const [note, setNote] = useState('');
  const mutation = useRealtimeDemoPingsSendCreate();
  const label = mutation.isPending ? app('realtime.sending') : app('realtime.sendButton');
  const failure = mutation.error ? <p className="mt-2 text-sm text-destructive">{app('realtime.sendFailed')}</p> : null;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await mutation.mutateAsync({ data: { note } });
    } catch {
      return; // shown from `error` (a 429 when throttled)
    }
    setNote('');
    onSent();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{app('realtime.send')}</CardTitle>
        <CardDescription>{app('realtime.sendHint')}</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="flex gap-2" onSubmit={submit}>
          <Input
            value={note}
            maxLength={200}
            placeholder={app('realtime.notePlaceholder')}
            onChange={(e) => setNote(e.target.value)}
          />
          <Button type="submit" disabled={mutation.isPending}>
            {label}
          </Button>
        </form>
        {failure}
      </CardContent>
    </Card>
  );
}
