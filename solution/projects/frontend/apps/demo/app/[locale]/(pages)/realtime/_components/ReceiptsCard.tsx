'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui-core';
import { useAuth } from '@djangocfg/api/auth';

import { demoUserTopic } from '@/api/generated/realtime';
import { useAppTranslations } from '@i18n';

import { PingList } from './PingList';
import { useTopicLog } from './useTopicLog';

/** `demo.user:{id}`: only that user may subscribe; signed out, nothing is subscribed. */
export function ReceiptsCard() {
  const { app } = useAppTranslations();
  const { user } = useAuth();
  const userId = typeof user?.id === 'number' ? user.id : null;
  const { entries } = useTopicLog(userId === null ? null : demoUserTopic({ userId }));
  const body = userId === null
    ? <p className="text-sm text-muted-foreground">{app('realtime.receiptsSignedOut')}</p>
    : <PingList entries={entries} empty={app('realtime.receiptsEmpty')} />;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{app('realtime.receipts')}</CardTitle>
        <CardDescription>{app('realtime.receiptsHint')}</CardDescription>
      </CardHeader>
      <CardContent>{body}</CardContent>
    </Card>
  );
}
