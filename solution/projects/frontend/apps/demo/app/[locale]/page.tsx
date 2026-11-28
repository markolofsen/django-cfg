import Link from 'next/link';

import { PublicLayout } from '@layouts/PublicLayout';
import { privateRoutes } from '@routes/private';
import { routes } from '@routes/public';
import { getTranslations } from 'next-intl/server';

export default async function HomePage() {
  const t = await getTranslations('app.home');

  return (
    <PublicLayout>
      <section className="mx-auto flex max-w-3xl flex-col items-center gap-6 px-4 py-24 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">{t('title')}</h1>
        <p className="text-base text-muted-foreground sm:text-lg">{t('subtitle')}</p>
        <div className="flex items-center gap-3">
          <Link
            href={privateRoutes.dashboard}
            className="rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:opacity-90"
          >
            {t('cta')}
          </Link>
          <Link
            href={routes.auth}
            className="rounded-full border border-border px-5 py-2.5 text-sm font-medium text-foreground hover:bg-secondary/50"
          >
            Sign in
          </Link>
        </div>
      </section>
    </PublicLayout>
  );
}
