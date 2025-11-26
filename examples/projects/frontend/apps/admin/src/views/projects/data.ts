import {
  Car,
  TrendingUp,
  ShoppingCart,
  Building2,
  Settings,
  Bot,
  Globe,
  Video,
  Search,
  type LucideIcon,
} from 'lucide-react';

// =============================================================================
// TYPES
// =============================================================================

export type ProjectStatus = 'production' | 'development' | 'beta';
export type ProjectCategory = 'api' | 'platform' | 'framework' | 'service';

export interface ProjectInfo {
  name: string;
  url: string;
  description: string;
  icon: LucideIcon;
  features: string[];
  status: ProjectStatus;
  category: ProjectCategory;
}

// =============================================================================
// PROJECTS DATA
// =============================================================================

export const projects: ProjectInfo[] = [
  {
    name: 'DjangoCFG',
    url: 'https://djangocfg.com/',
    description:
      'Django framework with type-safe Pydantic v2 configuration. Includes Next.js admin, WebSockets, AI agents, and background tasks.',
    icon: Settings,
    features: ['Pydantic v2', 'Type-Safe', 'Next.js Admin', 'WebSockets', 'AI Agents'],
    status: 'production',
    category: 'framework',
  },
  {
    name: 'CarAPIs',
    url: 'https://carapis.com/',
    description:
      'Automotive data API platform. Provides structured vehicle data, pricing analytics, and market insights from multiple sources.',
    icon: Car,
    features: ['Vehicle Data', 'Pricing API', 'Market Analytics', 'Multi-Source'],
    status: 'production',
    category: 'api',
  },
  {
    name: 'StockAPIs',
    url: 'https://stockapis.com/',
    description:
      'Crypto trading infrastructure with real-time market data, order flow analysis, and algorithmic trading strategies.',
    icon: TrendingUp,
    features: ['Real-Time Data', 'Order Flow', 'Trading Signals', 'Multi-Exchange'],
    status: 'production',
    category: 'api',
  },
  {
    name: 'ShopAPIs',
    url: 'https://shopapis.com/',
    description:
      'E-commerce integration APIs. Unified interface for product catalogs, inventory management, and order processing.',
    icon: ShoppingCart,
    features: ['Product Catalog', 'Inventory', 'Order Processing', 'Multi-Platform'],
    status: 'development',
    category: 'api',
  },
  {
    name: 'PropAPIs',
    url: 'https://propapis.com/',
    description:
      'Real estate data API platform. Property listings, market valuations, and geographic analytics for developers.',
    icon: Building2,
    features: ['Property Data', 'Valuations', 'Geo Analytics', 'Market Trends'],
    status: 'development',
    category: 'api',
  },
  {
    name: 'Reforms.ai',
    url: 'https://reforms.ai/',
    description:
      'AI-powered automation platform. Intelligent workflows, document processing, and business process optimization.',
    icon: Bot,
    features: ['AI Workflows', 'Document Processing', 'Automation', 'Integration'],
    status: 'beta',
    category: 'platform',
  },
  {
    name: 'GPTFake',
    url: 'https://gptfake.com/',
    description:
      'AI content detection and verification service. Identifies AI-generated text, images, and deepfakes.',
    icon: Search,
    features: ['AI Detection', 'Text Analysis', 'Image Verification', 'Deepfake Check'],
    status: 'development',
    category: 'service',
  },
  {
    name: 'Uneralon',
    url: 'https://uneralon.com/',
    description:
      'Data aggregation and analytics platform. Collects, processes, and delivers structured data feeds.',
    icon: Globe,
    features: ['Data Feeds', 'Aggregation', 'Processing', 'API Delivery'],
    status: 'production',
    category: 'platform',
  },
  {
    name: 'WebRTC2',
    url: 'https://webrtc2.com/',
    description:
      'Real-time communication infrastructure. Video conferencing, streaming, and peer-to-peer connectivity solutions.',
    icon: Video,
    features: ['Video Calls', 'Streaming', 'P2P', 'Low Latency'],
    status: 'development',
    category: 'service',
  },
  {
    name: 'UnrealSEO',
    url: 'https://unrealseo.com/',
    description:
      'SEO automation and analytics toolkit. Keyword research, rank tracking, and content optimization tools.',
    icon: Search,
    features: ['Keyword Research', 'Rank Tracking', 'Content Tools', 'Analytics'],
    status: 'development',
    category: 'service',
  },
];

// =============================================================================
// CATEGORIES
// =============================================================================

export const PROJECT_CATEGORIES: ProjectCategory[] = ['api', 'platform', 'framework', 'service'];

export const categories = [
  { value: 'all' as const, label: 'All Projects', count: projects.length },
  ...PROJECT_CATEGORIES.map((cat) => ({
    value: cat,
    label: cat === 'api' ? 'API Platforms' : cat.charAt(0).toUpperCase() + cat.slice(1) + 's',
    count: projects.filter((p) => p.category === cat).length,
  })),
];

/** Categories without 'all' for filtering */
export const filterableCategories = categories.filter((c) => c.value !== 'all');

// =============================================================================
// STYLE MAPS
// =============================================================================

export const statusColors: Record<ProjectStatus, string> = {
  production: 'bg-green-500/10 text-green-600 border-green-500/20',
  beta: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
  development: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
};

export const categoryColors: Record<ProjectCategory, string> = {
  api: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
  platform: 'bg-cyan-500/10 text-cyan-600 border-cyan-500/20',
  framework: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
  service: 'bg-pink-500/10 text-pink-600 border-pink-500/20',
};

// =============================================================================
// HELPERS
// =============================================================================

export function getProjectsByCategory(category: ProjectCategory | 'all'): ProjectInfo[] {
  if (category === 'all') return projects;
  return projects.filter((p) => p.category === category);
}

export function getProjectByName(name: string): ProjectInfo | undefined {
  return projects.find((p) => p.name === name);
}

// =============================================================================
// STATS
// =============================================================================

export const projectStats = {
  total: projects.length,
  production: projects.filter((p) => p.status === 'production').length,
  apiPlatforms: projects.filter((p) => p.category === 'api').length,
  categories: PROJECT_CATEGORIES.length,
};
