/**
 * Route Definitions
 *
 * All route definitions in one place - simple and clear
 */

import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard, MessageSquare, BriefcaseIcon, Code,
  LogIn, User, CreditCard, LifeBuoy, Bug,
  Book, Shield, FileText, Cookie, Wallet, TrendingUp, Bitcoin, Building2,
  FileQuestion, ServerCrash, Wrench, Lock
} from 'lucide-react';
import { isDevelopment } from '../settings';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface RouteMetadata {
  label: string;
  description?: string;
  icon?: LucideIcon;
  protected: boolean;
  group?: string;  // For menu grouping
  order?: number;  // Order within group
  show?: boolean;
}

export interface RouteDefinition {
  path: string;
  metadata: RouteMetadata;
}

// ─────────────────────────────────────────────────────────────────────────
// Base Route Group Class
// ─────────────────────────────────────────────────────────────────────────

abstract class BaseRouteGroup {
  protected routes: Map<string, RouteDefinition> = new Map();

  protected route(path: string, metadata: RouteMetadata): string {
    this.routes.set(path, { path, metadata });
    return path;
  }

  getRoute(path: string): RouteDefinition | undefined {
    return this.routes.get(path);
  }

  getAllRoutes(): RouteDefinition[] {
    return Array.from(this.routes.values());
  }
}

// ─────────────────────────────────────────────────────────────────────────
// Public Routes (No authentication required)
// ─────────────────────────────────────────────────────────────────────────

export class PublicRoutes extends BaseRouteGroup {
  readonly home = this.route('/', {
    label: 'Home',
    description: 'Dashboard home page',
    icon: LayoutDashboard,
    protected: false,
    group: 'main',
    order: 1,
  });

  readonly ui = this.route('/ui', {
    label: 'UI Components',
    description: 'UI component library and showcase',
    icon: LayoutDashboard,
    protected: false,
    group: 'components',
    order: 1,
  });

  readonly admin = this.route('/admin', {
    label: 'Django Admin',
    description: 'Django CFG admin interface demo',
    icon: Lock,
    protected: false,
    group: 'admin',
    order: 1,
  });

  readonly auth = this.route('/auth', {
    label: 'Sign In',
    description: 'User authentication',
    icon: LogIn,
    protected: false,
  });

  readonly support = this.route('/support', {
    label: 'Support',
    description: 'User support',
    icon: LifeBuoy,
    protected: false,
  });

  // External documentation link (not a route, but kept for reference)
  readonly docsExternal = 'https://djangocfg.com';

  // Debug routes (development only)
  readonly debug = this.route('/debug', {
    label: 'Debug Tools',
    description: 'Development and testing utilities',
    icon: Wrench,
    protected: false,
    group: 'debug',
    order: 1,
  });

  readonly debugError = this.route('/debug/error', {
    label: 'Runtime Error',
    description: 'Test ErrorBoundary with intentional error',
    icon: Bug,
    protected: false,
    group: 'debug',
    order: 2,
  });

  readonly error404 = this.route('/404', {
    label: '404 Page',
    description: 'Not Found error page',
    icon: FileQuestion,
    protected: false,
    group: 'debug',
    order: 3,
  });

  readonly error500 = this.route('/500', {
    label: '500 Page',
    description: 'Server Error page',
    icon: ServerCrash,
    protected: false,
    group: 'debug',
    order: 4,
  });
}

// ─────────────────────────────────────────────────────────────────────────
// Legal Routes (No authentication required)
// ─────────────────────────────────────────────────────────────────────────

export class LegalRoutes extends BaseRouteGroup {
  
  readonly privacy = this.route('/legal/privacy', {
    label: 'Privacy Policy',
    description: 'Privacy policy and data protection',
    icon: Shield,
    protected: false,
    group: 'legal',
    order: 1,
  });

  readonly terms = this.route('/legal/terms', {
    label: 'Terms of Service',
    description: 'Terms and conditions',
    icon: FileText,
    protected: false,
    group: 'legal',
    order: 2,
  });

  readonly cookies = this.route('/legal/cookies', {
    label: 'Cookie Policy',
    description: 'Cookie usage and preferences',
    icon: Cookie,
    protected: false,
    group: 'legal',
    order: 3,
  });

  readonly security = this.route('/legal/security', {
    label: 'Security Policy',
    description: 'Security practices and policies',
    icon: Shield,
    protected: false,
    group: 'legal',
    order: 4,
  });
}

// ─────────────────────────────────────────────────────────────────────────
// Private Routes (Authentication required)
// ─────────────────────────────────────────────────────────────────────────

export class PrivateRoutes extends BaseRouteGroup {
  readonly overview = this.route('/private', {
    label: 'Dashboard',
    description: 'Main dashboard overview',
    icon: LayoutDashboard,
    protected: true,
    group: 'main',
    order: 1,
  });

  readonly trading = this.route('/private/trading', {
    label: 'Trading',
    description: 'Manage trading portfolio and orders',
    icon: TrendingUp,
    protected: true,
    group: 'main',
    order: 2,
  });

  readonly crypto = this.route('/private/crypto', {
    label: 'Cryptocurrency',
    description: 'Manage cryptocurrency data and wallets',
    icon: Bitcoin,
    protected: true,
    group: 'main',
    order: 3,
  });

  readonly profile = this.route('/private/profile', {
    label: 'Profile',
    description: 'User profile and settings',
    icon: User,
    protected: true,
    group: 'account',
    order: 1,
  });

  readonly support = this.route('/private/support', {
    label: 'Support',
    description: 'Manage support, tickets, and issues',
    icon: LifeBuoy,
    protected: true,
    group: 'account',
    order: 2,
  });

  readonly payments = this.route('/private/payments', {
    label: 'Payments',
    description: 'Manage payments, balance, and billing',
    icon: CreditCard,
    protected: true,
    group: 'account',
    order: 3,
  });

  readonly ui = this.route('/private/ui', {
    label: 'UI Components',
    description: 'UI component library and showcase',
    icon: LayoutDashboard,
    protected: true,
    group: 'developer',
    order: 2,
    // show: isDevelopment,
  });

  readonly admin = this.route('/private/admin', {
    label: 'Django Admin',
    description: 'Django CFG admin interface demo',
    icon: Lock,
    protected: true,
    group: 'developer',
    order: 3,
  });

  // Dynamic order routes
  orderDetail(id: string): string {
    return `/private/trading/orders/${id}`;
  }

  // Dynamic coin routes
  coinDetail(id: string): string {
    return `/private/crypto/coins/${id}`;
  }

  exchangeDetail(id: string): string {
    return `/private/crypto/exchanges/${id}`;
  }
}

// ─────────────────────────────────────────────────────────────────────────
// Routes Container
// ─────────────────────────────────────────────────────────────────────────

export class UnrealonRoutes {
  readonly public = new PublicRoutes();
  readonly private = new PrivateRoutes();
  readonly legal = new LegalRoutes();
  
  getAllRoutes(): RouteDefinition[] {
    return [
      ...this.public.getAllRoutes(),
      ...this.private.getAllRoutes(),
      ...this.legal.getAllRoutes(),
    ];
  }

  getRouteByPath(path: string): RouteDefinition | undefined {
    return this.getAllRoutes().find(r => r.path === path);
  }

  getRouteLabel(path: string): string {
    const route = this.getRouteByPath(path);
    return route?.metadata.label || 'No label';
  }

  getRouteDescription(path: string): string | undefined {
    return this.getRouteByPath(path)?.metadata.description;
  }

  isRouteProtected(path: string): boolean {
    const route = this.getRouteByPath(path);
    return route?.metadata.protected ?? true;
  }
}
