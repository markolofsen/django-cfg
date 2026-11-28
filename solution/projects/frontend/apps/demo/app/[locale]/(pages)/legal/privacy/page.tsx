import { PublicLayout } from '@layouts/PublicLayout';
import { getTranslations } from 'next-intl/server';

export default async function PrivacyPage() {
  const t = await getTranslations('app.legal');

  return (
    <PublicLayout>
      <article className="prose prose-neutral dark:prose-invert mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1>{t('privacy')}</h1>
        <p>
          This is a placeholder privacy notice for the djangocfg demo
          app. Replace it with your real policy before going to
          production.
        </p>
      </article>
    </PublicLayout>
  );
}
