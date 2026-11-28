'use client';

import Link from 'next/link';

import { PublicLayout } from '@layouts/PublicLayout';
import { routes } from '@routes/public';

export default function LocaleNotFound() {
  return (
    <PublicLayout>
      <section className="mx-auto flex max-w-xl flex-col items-center gap-4 px-4 py-24 text-center">
        <p className="text-xs uppercase tracking-widest text-muted-foreground">404</p>
        <h1 className="text-3xl font-bold">Page not found</h1>
        <Link
          href={routes.home}
          className="rounded-full bg-primary px-5 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          Back to home
        </Link>
      </section>
    </PublicLayout>
  );
}
