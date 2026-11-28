import React from 'react';

interface JsonLdProps {
  data: Record<string, unknown> | Record<string, unknown>[];
}

/**
 * JsonLd Component
 * 
 * Renders JSON-LD structured data for SEO.
 * Use this for schema.org markup (Organization, WebSite, FAQPage, etc.)
 * 
 * @example
 * ```tsx
 * <JsonLd data={{
 *   "@context": "https://schema.org",
 *   "@type": "Organization",
 *   "name": "My Company"
 * }} />
 * ```
 */
export function JsonLd({ data }: JsonLdProps) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data, null, 0),
      }}
    />
  );
}
