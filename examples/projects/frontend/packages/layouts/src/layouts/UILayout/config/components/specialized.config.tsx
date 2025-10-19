/**
 * Specialized Components Configuration
 */

import React from 'react';
import type { ComponentConfig } from './types';

export const SPECIALIZED_COMPONENTS: ComponentConfig[] = [
  {
    name: 'Sidebar',
    category: 'specialized',
    description: 'Full-featured sidebar navigation component (23KB) with collapsible groups and icons',
    importPath: `import { Sidebar } from '@djangocfg/ui';`,
    example: `// Note: Sidebar is a complex component used in layouts
// See DashboardLayout in the Layouts section for full implementation

<Sidebar
  menuGroups={[
    {
      label: "Main",
      items: [
        {
          icon: <HomeIcon />,
          label: "Dashboard",
          href: "/",
          isActive: true
        },
        {
          icon: <UsersIcon />,
          label: "Users",
          href: "/users"
        },
      ]
    },
    {
      label: "Settings",
      items: [
        {
          icon: <SettingsIcon />,
          label: "Preferences",
          href: "/settings"
        },
      ]
    }
  ]}
/>`,
    preview: (
      <div className="p-6 border rounded-md bg-muted/50">
        <p className="text-sm text-muted-foreground mb-4">
          The Sidebar component is a comprehensive navigation solution with:
        </p>
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li>• Collapsible menu groups</li>
          <li>• Icon support with lucide-react</li>
          <li>• Active state management</li>
          <li>• Responsive design (mobile drawer)</li>
          <li>• Keyboard navigation</li>
          <li>• 23KB bundle size</li>
        </ul>
        <p className="text-xs text-muted-foreground mt-4">
          See <strong>DashboardLayout</strong> in the UI Guide for full implementation example
        </p>
      </div>
    ),
  },
  {
    name: 'ImageWithFallback',
    category: 'specialized',
    description: 'Enhanced image component with loading states and fallback support',
    importPath: `import { ImageWithFallback } from '@djangocfg/ui';`,
    example: `<div className="space-y-4">
  {/* Successful load */}
  <ImageWithFallback
    src="/images/example.jpg"
    alt="Example image"
    width={300}
    height={200}
    className="rounded-md"
  />

  {/* With fallback */}
  <ImageWithFallback
    src="/invalid-image.jpg"
    alt="Image with fallback"
    fallbackSrc="/images/placeholder.jpg"
    width={300}
    height={200}
    className="rounded-md"
  />

  {/* Custom loading state */}
  <ImageWithFallback
    src="/large-image.jpg"
    alt="Loading example"
    width={300}
    height={200}
    className="rounded-md"
    loadingComponent={
      <div className="flex items-center justify-center h-full">
        <Spinner />
      </div>
    }
  />
</div>`,
    preview: (
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Features:
        </p>
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li>• Automatic fallback on load error</li>
          <li>• Custom loading states</li>
          <li>• Built on Next.js Image component</li>
          <li>• Preserves aspect ratio</li>
          <li>• Optimized performance</li>
        </ul>
        <div className="p-4 border rounded-md bg-muted/30">
          <p className="text-xs font-mono text-muted-foreground">
            Image loading states: loading → loaded | error → fallback
          </p>
        </div>
      </div>
    ),
  },
];
