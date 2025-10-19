/**
 * Layout Components Configuration
 */

import React from 'react';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Separator,
  Skeleton,
  AspectRatio,
  Sticky,
} from '@djangocfg/ui';
import type { ComponentConfig } from './types';

export const LAYOUT_COMPONENTS: ComponentConfig[] = [
  {
    name: 'Card',
    category: 'layout',
    description: 'Container with header, content, and footer sections',
    importPath: "import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@djangocfg/ui';",
    example: `<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>This is the main content of the card.</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>`,
    preview: (
      <Card className="max-w-sm">
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Card description goes here</CardDescription>
        </CardHeader>
        <CardContent>
          <p>This is the main content of the card.</p>
        </CardContent>
        <CardFooter>
          <Button>Action</Button>
        </CardFooter>
      </Card>
    ),
  },
  {
    name: 'Separator',
    category: 'layout',
    description: 'Visual divider between sections',
    importPath: "import { Separator } from '@djangocfg/ui';",
    example: `<div>
  <p>Section 1</p>
  <Separator className="my-4" />
  <p>Section 2</p>
</div>`,
    preview: (
      <div>
        <p>Section 1</p>
        <Separator className="my-4" />
        <p>Section 2</p>
      </div>
    ),
  },
  {
    name: 'Skeleton',
    category: 'layout',
    description: 'Loading placeholder animation',
    importPath: "import { Skeleton } from '@djangocfg/ui';",
    example: `<div className="space-y-3">
  <Skeleton className="w-full h-12" />
  <Skeleton className="w-3/4 h-8" />
  <Skeleton className="w-1/2 h-8" />
</div>`,
    preview: (
      <div className="space-y-3 max-w-sm">
        <Skeleton className="w-full h-12" />
        <Skeleton className="w-3/4 h-8" />
        <Skeleton className="w-1/2 h-8" />
      </div>
    ),
  },
  {
    name: 'AspectRatio',
    category: 'layout',
    description: 'Maintain aspect ratio for content',
    importPath: "import { AspectRatio } from '@djangocfg/ui';",
    example: `<AspectRatio ratio={16/9} className="bg-muted">
  <img src="/demo.jpg" alt="Demo" className="object-cover rounded-md" />
</AspectRatio>`,
    preview: (
      <AspectRatio ratio={16/9} className="bg-muted rounded-md max-w-sm">
        <div className="flex items-center justify-center h-full text-muted-foreground">
          16:9 Aspect Ratio
        </div>
      </AspectRatio>
    ),
  },
  {
    name: 'Sticky',
    category: 'layout',
    description: 'Make content sticky on scroll',
    importPath: "import { Sticky } from '@djangocfg/ui';",
    example: `<Sticky offsetTop={0} disableOnMobile={false}>
  <nav className="bg-background border p-4">
    Sticky Navigation
  </nav>
</Sticky>`,
    preview: (
      <div className="h-[300px] overflow-auto border rounded-md relative">
        <Sticky offsetTop={0} disableOnMobile={false}>
          <div className="bg-primary text-primary-foreground p-3 text-center font-semibold shadow-md">
            Sticky Header (scroll to see effect)
          </div>
        </Sticky>
        <div className="p-4 space-y-3">
          {[...Array(20)].map((_, i) => (
            <p key={i} className="text-sm">
              Content line {i + 1} - Scroll down to see the sticky header in action
            </p>
          ))}
        </div>
      </div>
    ),
  },
];
