import {
  Layers,
  Zap,
  Image,
  FileCode,
  Radio,
  FileText,
  Palette,
  Settings,
  Sparkles,
  type LucideIcon,
} from 'lucide-react';

// =============================================================================
// TYPES
// =============================================================================

export type PackageStatus = 'stable' | 'beta' | 'experimental';
export type PackageCategory = 'ui' | 'utility' | 'config' | 'realtime';

export interface PackageInfo {
  name: string;
  description: string;
  icon: LucideIcon;
  features: string[];
  status: PackageStatus;
  category: PackageCategory;
  npmUrl?: string;
}

// =============================================================================
// PACKAGES DATA
// =============================================================================

export const packages: PackageInfo[] = [
  // UI/Component Packages
  {
    name: '@djangocfg/ui',
    description:
      'Comprehensive React UI library with 56+ components, 7 blocks, and 11 hooks. Built with Radix UI, Tailwind CSS v4, and TypeScript.',
    icon: Palette,
    features: ['56+ Components', 'Radix UI', 'Tailwind v4', 'TypeScript', 'Dark Mode'],
    status: 'stable',
    category: 'ui',
    npmUrl: 'https://www.npmjs.com/package/@djangocfg/ui',
  },
  {
    name: '@djangocfg/layouts',
    description:
      'Layout system with authentication, dashboard layouts, snippets, and utility functions for building admin applications.',
    icon: Layers,
    features: ['Auth System', 'Dashboard', 'Layouts', 'Video Player', 'Utilities'],
    status: 'stable',
    category: 'ui',
    npmUrl: 'https://www.npmjs.com/package/@djangocfg/layouts',
  },
  {
    name: '@djangocfg/markdown',
    description:
      'Markdown rendering components with GFM support, syntax highlighting, and React integration.',
    icon: FileText,
    features: ['GFM Support', 'Syntax Highlighting', 'Tables', 'React'],
    status: 'stable',
    category: 'ui',
    npmUrl: 'https://www.npmjs.com/package/@djangocfg/markdown',
  },

  // Utility Packages
  {
    name: '@djangocfg/api',
    description:
      'Auto-generated TypeScript API clients with React hooks, SWR integration, Zod validation, and context providers.',
    icon: Zap,
    features: ['Auto-Generated', 'SWR', 'Zod', 'TypeScript', 'React Hooks'],
    status: 'stable',
    category: 'utility',
    npmUrl: 'https://www.npmjs.com/package/@djangocfg/api',
  },
  {
    name: '@djangocfg/og-image',
    description:
      'Universal OG Image generation for Next.js apps using Vercel OG with customizable templates.',
    icon: Image,
    features: ['Edge Runtime', 'Templates', 'Next.js', 'Vercel OG'],
    status: 'stable',
    category: 'utility',
    npmUrl: 'https://www.npmjs.com/package/@djangocfg/og-image',
  },
  {
    name: '@djangocfg/imgai',
    description:
      'AI-powered image generation & management with OpenAI DALL-E 3, Claude integration, and automatic catalog generation.',
    icon: Sparkles,
    features: ['DALL-E 3', 'Claude', 'CLI', 'Auto Catalog', 'Sharp'],
    status: 'beta',
    category: 'utility',
    npmUrl: 'https://www.npmjs.com/package/@djangocfg/imgai',
  },

  // Realtime Packages
  {
    name: '@djangocfg/centrifugo',
    description:
      'Production-ready Centrifugo WebSocket client with React integration, RPC pattern, and monitoring tools.',
    icon: Radio,
    features: ['WebSocket', 'React Hooks', 'RPC', 'Monitoring', 'Auto Reconnect'],
    status: 'stable',
    category: 'realtime',
    npmUrl: 'https://www.npmjs.com/package/@djangocfg/centrifugo',
  },

  // Config Packages
  {
    name: '@djangocfg/typescript-config',
    description: 'Shared TypeScript configurations for Next.js, React, and Node.js projects.',
    icon: FileCode,
    features: ['Base Config', 'Next.js', 'React', 'Node.js'],
    status: 'stable',
    category: 'config',
    npmUrl: 'https://www.npmjs.com/package/@djangocfg/typescript-config',
  },
  {
    name: '@djangocfg/eslint-config',
    description: 'Shared ESLint configurations with TypeScript and React best practices.',
    icon: Settings,
    features: ['TypeScript', 'React', 'Best Practices', 'Flat Config'],
    status: 'stable',
    category: 'config',
    npmUrl: 'https://www.npmjs.com/package/@djangocfg/eslint-config',
  },
];

// =============================================================================
// CATEGORIES
// =============================================================================

export const categories = [
  { value: 'all', label: 'All Packages', count: packages.length },
  { value: 'ui', label: 'UI/Components', count: packages.filter((p) => p.category === 'ui').length },
  { value: 'utility', label: 'Utilities', count: packages.filter((p) => p.category === 'utility').length },
  { value: 'realtime', label: 'Realtime', count: packages.filter((p) => p.category === 'realtime').length },
  { value: 'config', label: 'Config', count: packages.filter((p) => p.category === 'config').length },
] as const;

// =============================================================================
// STYLE MAPS
// =============================================================================

export const statusColors: Record<PackageStatus, string> = {
  stable: 'bg-green-500/10 text-green-600 border-green-500/20',
  beta: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
  experimental: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
};

export const categoryColors: Record<PackageCategory, string> = {
  ui: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
  utility: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
  config: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
  realtime: 'bg-cyan-500/10 text-cyan-600 border-cyan-500/20',
};

// =============================================================================
// HELPERS
// =============================================================================

export function getPackagesByCategory(category: PackageCategory | 'all'): PackageInfo[] {
  if (category === 'all') return packages;
  return packages.filter((p) => p.category === category);
}

export function getPackageByName(name: string): PackageInfo | undefined {
  return packages.find((p) => p.name === name);
}
