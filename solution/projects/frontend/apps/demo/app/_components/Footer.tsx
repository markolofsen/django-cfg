'use client';

import Link from 'next/link';

import { settings } from '@core/settings';
import { routes } from '@routes/public';
import { useAppTranslations } from '@i18n';

export function Footer() {
  const { app } = useAppTranslations();

  return (
    <footer className="border-t border-border mt-auto">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-4 py-6 text-xs text-muted-foreground sm:flex-row sm:px-6">
        <span>© {new Date().getFullYear()} {settings.app.name}</span>
        <div className="flex items-center gap-4">
          <Link href={routes.legal.privacy} className="hover:text-foreground">
            {app('legal.privacy')}
          </Link>
          <Link href={routes.legal.terms} className="hover:text-foreground">
            {app('legal.terms')}
          </Link>
        </div>
      </div>
    </footer>
  );
}
