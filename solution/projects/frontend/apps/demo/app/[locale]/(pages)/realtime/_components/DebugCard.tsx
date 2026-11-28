'use client';

import { RealtimePanel } from '@djangocfg/realtime/debug';

import { useAppTranslations } from '@i18n';

/** `RealtimePanel`: the socket, every topic with its offset, the last frames. */
export function DebugCard() {
  const { app } = useAppTranslations();
  return (
    <section className="space-y-2 lg:col-span-2">
      <h2 className="text-lg font-semibold">{app('realtime.debug')}</h2>
      <RealtimePanel />
    </section>
  );
}
