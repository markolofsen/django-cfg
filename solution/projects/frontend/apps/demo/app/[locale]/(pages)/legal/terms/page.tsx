import { PublicLayout } from '@layouts/PublicLayout';
import { getTranslations } from 'next-intl/server';

export default async function TermsPage() {
  const t = await getTranslations('app.legal');

  return (
    <PublicLayout>
      <article className="prose prose-neutral dark:prose-invert mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1>{t('terms')}</h1>
        <p>
          Placeholder terms of service for the djangocfg demo. Swap in
          your real terms when shipping a real product.
        </p>
      </article>
    </PublicLayout>
  );
}
