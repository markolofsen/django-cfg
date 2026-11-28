/**
 * LegalPage Component
 *
 * Reusable component for legal pages (Privacy, Terms, Cookies, Security)
 * Accepts configuration for flexible content rendering
 *
 * Usage:
 * ```tsx
 * import { LegalPage } from '@djangocfg/layouts/components/legal';
 * import { privacyConfig } from './config';
 *
 * export default function PrivacyPage() {
 *   return <LegalPage config={privacyConfig} />;
 * }
 * ```
 */

'use client';

import React from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@djangocfg/ui-core/components';

import type { LegalPageConfig } from './types';

export interface LegalPageProps {
  config: LegalPageConfig;
  className?: string;
}

/**
 * Format date for display
 */
function formatDate(date: string | Date | undefined): string {
  if (!date) return '';
  if (typeof date === 'string') return date;
  return date.toISOString().split('T')[0] ?? '';
}

/**
 * LegalPage Component
 */
export function LegalPage({ config, className }: LegalPageProps) {
  const { title, lastUpdated, sections } = config;

  return (
    <div className={`container mx-auto max-w-4xl py-16 px-4 ${className || ''}`}>
      <div className="flex flex-col gap-8">
        {/* Header */}
        <div className="flex flex-col gap-4">
          <h1 className="text-4xl font-bold">{title}</h1>
          {lastUpdated && (
            <p className="text-lg text-muted-foreground">
              Last updated: {formatDate(lastUpdated)}
            </p>
          )}
        </div>

        {/* Sections */}
        {sections.map((section, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle>{section.title}</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              {Array.isArray(section.content) ? (
                <div className="flex flex-col gap-2">
                  {section.content.map((paragraph, pIndex) => (
                    <p key={pIndex}>{paragraph}</p>
                  ))}
                </div>
              ) : (
                <p>{section.content}</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

