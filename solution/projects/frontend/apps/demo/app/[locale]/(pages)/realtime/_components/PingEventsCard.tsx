'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@djangocfg/ui-core';

import { demoPingTopic } from '@/api/generated/realtime';
import { useAppTranslations } from '@i18n';

import { PingList } from './PingList';
import { useTopicLog } from './useTopicLog';

/** `demo.ping`: anonymous, published by the send endpoint and by `manage.py realtime publish`. */
export function PingEventsCard() {
  const { app } = useAppTranslations();
  const { entries } = useTopicLog(demoPingTopic());

  return (
    <Card>
      <CardHeader>
        <CardTitle>{app('realtime.events')}</CardTitle>
      </CardHeader>
      <CardContent>
        <PingList entries={entries} empty={app('realtime.eventsEmpty')} />
      </CardContent>
    </Card>
  );
}
