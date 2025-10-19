import Head from 'next/head';
import { generateOgImageUrl } from '@djangocfg/og-image/utils';

import { PageConfig } from '../../../types/pageConfig';

interface SeoProps {
  pageConfig: PageConfig;
  icons?: {
    logo192?: string;
    logo384?: string;
    logo512?: string;
    logoVector?: string;
  };
  siteUrl?: string;
}

export default function Seo({ pageConfig, icons, siteUrl }: SeoProps) {
  const {
    title,
    description,
    keywords,
    jsonLd,
    ogImage,
  } = pageConfig;

  const ogTitle = ogImage?.title || title;
  const ogSubtitle = ogImage?.subtitle || description;

  // Generate OG image URL using @djangocfg/og-image utilities
  const ogImageUrl = ogImage
    ? generateOgImageUrl('/api/og', {
        title: ogTitle || 'Untitled',
        subtitle: ogSubtitle || '',
        description: ogSubtitle || '',
      })
    : null;

  // Make absolute URL if siteUrl provided
  const absoluteOgImageUrl = ogImageUrl && siteUrl ? `${siteUrl}${ogImageUrl}` : ogImageUrl;

  return (
    <Head>
      <title>{title}</title>
      <meta name="description" content={description} />
      {keywords && <meta name="keywords" content={keywords} />}
      
      {/* Favicon */}
      <link rel="icon" type="image/png" href={icons?.logo192 || '/favicon.png'} />
      
      {/* Open Graph */}
      <meta property="og:title" content={ogTitle} />
      <meta property="og:description" content={ogSubtitle} />
      <meta property="og:type" content="website" />

      {/* Site Name */}
      {pageConfig.projectName && (
        <meta property="og:site_name" content={pageConfig.projectName} />
      )}
      
      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={ogTitle} />
      <meta name="twitter:description" content={ogSubtitle} />
      
      {/* OG Image */}
      {absoluteOgImageUrl && (
        <>
          <meta property="og:image" content={absoluteOgImageUrl} />
          <meta property="og:image:width" content="1200" />
          <meta property="og:image:height" content="630" />
          <meta property="og:image:type" content="image/png" />
          <meta name="twitter:image" content={absoluteOgImageUrl} />
        </>
      )}
      
      {/* JSON-LD */}
      {jsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(jsonLd),
          }}
        />
      )}
    </Head>
  );
} 