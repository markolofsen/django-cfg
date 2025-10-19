/**
 * Categories Configuration
 * Defines all component categories with metadata
 */

import React from 'react';
import {
  Home,
  FormInput,
  LayoutGrid,
  Navigation as NavigationIcon,
  Square,
  MessageSquare,
  Table2,
  Puzzle,
  Boxes,
  Code2,
  Palette,
} from 'lucide-react';
import { getComponentCount } from './components';

export interface ComponentCategory {
  id: string;
  label: string;
  icon: React.ReactNode;
  count?: number;
  description?: string;
}

export const CATEGORIES: ComponentCategory[] = [
  {
    id: 'overview',
    label: 'Overview',
    icon: <Home className="h-4 w-4" />,
    description: 'Welcome to Django CFG UI Library - explore 56+ components, 7 blocks, and 11 hooks',
  },
  {
    id: 'forms',
    label: 'Form Components',
    icon: <FormInput className="h-4 w-4" />,
    count: getComponentCount('forms'),
    description: 'Input fields, buttons, checkboxes, selects, and form validation components',
  },
  {
    id: 'layout',
    label: 'Layout Components',
    icon: <LayoutGrid className="h-4 w-4" />,
    count: getComponentCount('layout'),
    description: 'Cards, separators, skeletons, and structural layout components',
  },
  {
    id: 'navigation',
    label: 'Navigation',
    icon: <NavigationIcon className="h-4 w-4" />,
    count: getComponentCount('navigation'),
    description: 'Menus, breadcrumbs, tabs, and pagination components',
  },
  {
    id: 'overlay',
    label: 'Overlay Components',
    icon: <Square className="h-4 w-4" />,
    count: getComponentCount('overlay'),
    description: 'Dialogs, sheets, popovers, tooltips, and dropdown menus',
  },
  {
    id: 'feedback',
    label: 'Feedback',
    icon: <MessageSquare className="h-4 w-4" />,
    count: getComponentCount('feedback'),
    description: 'Toasts, alerts, progress bars, badges, and status indicators',
  },
  {
    id: 'data',
    label: 'Data Display',
    icon: <Table2 className="h-4 w-4" />,
    count: getComponentCount('data'),
    description: 'Tables, accordions, collapsibles, and data visualization',
  },
  {
    id: 'specialized',
    label: 'Specialized',
    icon: <Puzzle className="h-4 w-4" />,
    count: getComponentCount('specialized'),
    description: 'Advanced components like sidebar navigation and image handling',
  },
  {
    id: 'blocks',
    label: 'Blocks',
    icon: <Boxes className="h-4 w-4" />,
    count: getComponentCount('blocks'),
    description: 'Pre-built landing page sections: Hero, SuperHero, Features, CTA, Newsletter, Stats, Testimonials',
  },
  {
    id: 'hooks',
    label: 'Hooks',
    icon: <Code2 className="h-4 w-4" />,
    count: getComponentCount('hooks'),
    description: 'Custom React hooks for common functionality and state management',
  },
  {
    id: 'tailwind4',
    label: 'Tailwind CSS v4',
    icon: <Palette className="h-4 w-4" />,
    description: 'Migration guide and best practices for Tailwind CSS v4',
  },
];

export function getCategoryById(id: string): ComponentCategory | undefined {
  return CATEGORIES.find(cat => cat.id === id);
}

export function getTotalComponentCount(): number {
  return CATEGORIES.reduce((sum, cat) => sum + (cat.count || 0), 0);
}
