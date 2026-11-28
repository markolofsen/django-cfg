import { settings } from '@core/settings';

/**
 * SoftwareApplication JSON-LD for the Django-CFG framework, emitted once
 * site-wide from the root layout. Lets Google/Bing and AI answer engines model
 * Django-CFG as a developer tool with a discoverable offer.
 *
 * Django-CFG is MIT-licensed open source, so the offer points at the main
 * product site and price is intentionally omitted (no paid tier) — the offer
 * stays a discoverable URL rather than a hardcoded amount.
 */
export function SoftwareApplicationJsonLd() {
  const { name, siteUrl, description } = settings.app;

  const software = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name,
    applicationCategory: 'DeveloperApplication',
    operatingSystem: 'Web',
    url: siteUrl,
    description,
    provider: {
      '@type': 'Organization',
      name,
      url: siteUrl,
    },
    offers: {
      '@type': 'Offer',
      url: settings.site.home,
      category: 'Open Source',
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(software) }}
    />
  );
}
