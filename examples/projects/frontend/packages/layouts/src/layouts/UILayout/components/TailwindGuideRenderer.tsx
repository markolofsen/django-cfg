/**
 * TailwindGuideRenderer
 * Renders Tailwind CSS v4 guide from config
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui';
import { PrettyCode } from '@djangocfg/ui/tools';
import { TAILWIND_GUIDE } from '../config';
import { CategorySection } from './AutoComponentDemo';

/**
 * TailwindGuideRenderer - Dynamically renders Tailwind guide from config
 */
export function TailwindGuideRenderer() {
  return (
    <CategorySection
      title="Tailwind CSS v4 Guide"
      description="Everything you need to know about migrating to and using Tailwind CSS v4"
    >
      {/* Key Changes */}
      <Card>
        <CardHeader>
          <CardTitle>Key Changes in Tailwind CSS v{TAILWIND_GUIDE.version}</CardTitle>
          <CardDescription>
            Major improvements and breaking changes you should know about
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="list-disc list-inside space-y-2 text-muted-foreground">
            {TAILWIND_GUIDE.keyChanges.map((change, index) => (
              <li key={index}>{change}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Best Practices */}
      <Card>
        <CardHeader>
          <CardTitle>Best Practices</CardTitle>
          <CardDescription>
            Follow these patterns for clean, maintainable code
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">✅ Recommended Patterns</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-4">
                {TAILWIND_GUIDE.bestPractices.map((practice, index) => (
                  <li key={index}>{practice}</li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Migration Steps */}
      <Card>
        <CardHeader>
          <CardTitle>Migration Steps (v3 → v4)</CardTitle>
          <CardDescription>
            Step-by-step guide to upgrade your project
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-2 text-muted-foreground">
            {TAILWIND_GUIDE.migrationSteps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ol>
        </CardContent>
      </Card>

      {/* Examples */}
      {TAILWIND_GUIDE.examples.map((example, index) => (
        <Card key={index}>
          <CardHeader>
            <CardTitle>{example.title}</CardTitle>
            <CardDescription>{example.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <PrettyCode
              data={example.code}
              language="css"
              className="text-sm"
            />
          </CardContent>
        </Card>
      ))}

      {/* Resources */}
      <Card>
        <CardHeader>
          <CardTitle>Official Resources</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            <li>
              <a
                href="https://tailwindcss.com/docs/upgrade-guide"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Official Upgrade Guide
              </a>
            </li>
            <li>
              <a
                href="https://tailwindcss.com/docs/guides/nextjs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Next.js Integration Guide
              </a>
            </li>
            <li>
              <a
                href="https://tailwindcss.com/blog/tailwindcss-v4"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Tailwind CSS v4.0 Release Notes
              </a>
            </li>
          </ul>
        </CardContent>
      </Card>
    </CategorySection>
  );
}
