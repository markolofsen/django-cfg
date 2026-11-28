'use client';

import { useRealtimeDemoPingsList } from '@/api/generated/endpoints/realtime-demo/realtime-demo';
import { PublicLayout } from '@layouts/PublicLayout';
import { useAppTranslations } from '@i18n';

import { ConnectionCard } from './_components/ConnectionCard';
import { DebugCard } from './_components/DebugCard';
import { PingEventsCard } from './_components/PingEventsCard';
import { ReceiptsCard } from './_components/ReceiptsCard';
import { SendPingCard } from './_components/SendPingCard';
import { StoredPingsCard } from './_components/StoredPingsCard';

/**
 * Live delivery from django-cfg's realtime module against the reference
 * Django (`apps/realtime_demo`): an explicit topic (`demo.ping`), a per-user
 * topic (`demo.user:{id}`), and a REST list backed by the generated React
 * Query client.
 */
export default function RealtimePage() {
  const { app } = useAppTranslations();
  const pings = useRealtimeDemoPingsList({ page_size: 10 });
  const refreshPings = () => void pings.refetch();

  return (
    <PublicLayout>
      <section className="mx-auto flex max-w-5xl flex-col gap-6 px-4 py-12 sm:px-6">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">{app('realtime.title')}</h1>
          <p className="text-sm text-muted-foreground">{app('realtime.subtitle')}</p>
        </header>
        <div className="grid gap-6 lg:grid-cols-2">
          <ConnectionCard />
          <SendPingCard onSent={refreshPings} />
          <PingEventsCard />
          <ReceiptsCard />
          <StoredPingsCard data={pings.data} error={pings.error} />
          <DebugCard />
        </div>
      </section>
    </PublicLayout>
  );
}
