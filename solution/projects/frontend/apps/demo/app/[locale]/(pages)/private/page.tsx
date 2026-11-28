'use client';

import { useAuth } from '@djangocfg/api/auth';

import { useAppTranslations } from '@i18n';

export default function DashboardPage() {
  const { user } = useAuth();
  const { app } = useAppTranslations();

  const name = user?.first_name?.trim() || user?.full_name?.trim() || user?.email || '';

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">{app('dashboard.title')}</h1>
        <p className="text-sm text-muted-foreground">
          {app('dashboard.welcome')}{name ? `, ${name}` : ''}.
        </p>
      </header>

      <div className="rounded-2xl border border-border bg-card p-6">
        <p className="text-sm text-muted-foreground">{app('dashboard.description')}</p>
      </div>
    </section>
  );
}
