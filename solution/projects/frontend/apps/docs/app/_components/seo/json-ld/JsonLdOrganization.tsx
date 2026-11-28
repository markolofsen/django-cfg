import { settings } from '@core/settings';

/**
 * Organization JSON-LD, emitted once site-wide from the root layout. Gives
 * Google/Bing and AI answer engines a machine-readable identity for Django-CFG
 * (the named entity behind the framework).
 *
 * SoftwareApplication is emitted separately by <SoftwareApplicationJsonLd />.
 * `sameAs` lists product-confirmed public profiles (the GitHub org and the
 * main product site); extend as more become available.
 */
export function OrganizationJsonLd() {
  const { name, siteUrl, description } = settings.app;

  const organization = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name,
    url: siteUrl,
    logo: `${settings.app.docsUrl}/favicon.png`,
    description,
    sameAs: [settings.github.org, settings.site.home],
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(organization) }}
    />
  );
}
