/**
 * Route Definitions for BitAPI
 *
 * All route definitions with metadata for menu generation
 */

import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard, Radio, User, LogIn,
  Book, Shield, FileText, Cookie, Palette
} from 'lucide-react';

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
    description: 'BitAPI Dashboard home',
    icon: LayoutDashboard,
    protected: false,
    group: 'main',
    order: 1,
  });

  readonly auth = this.route('/auth', {
    label: 'Sign In',
    description: 'User authentication',
    icon: LogIn,
    protected: false,
  });

  readonly docs = this.route('/docs', {
    label: 'Documentation',
    description: 'API documentation and guides',
    icon: Book,
    protected: false,
    group: 'resources',
    order: 1,
  });

  readonly privacy = this.route('/privacy', {
    label: 'Privacy Policy',
    description: 'Privacy policy and data protection',
    icon: Shield,
    protected: false,
    group: 'resources',
    order: 2,
  });

  readonly terms = this.route('/terms', {
    label: 'Terms of Service',
    description: 'Terms and conditions',
    icon: FileText,
    protected: false,
    group: 'resources',
    order: 3,
  });

  readonly cookies = this.route('/cookies', {
    label: 'Cookie Policy',
    description: 'Cookie usage and preferences',
    icon: Cookie,
    protected: false,
    group: 'security',
    order: 2,
  });

  readonly security = this.route('/security', {
    label: 'Security Policy',
    description: 'Security practices and policies',
    icon: Shield,
    protected: false,
    group: 'security',
    order: 1,
  });
}

// ─────────────────────────────────────────────────────────────────────────
// Private Routes (Authentication required)
// ─────────────────────────────────────────────────────────────────────────

export class PrivateRoutes extends BaseRouteGroup {
  readonly overview = this.route('/private', {
    label: 'Overview',
    description: 'Dashboard overview',
    icon: LayoutDashboard,
    protected: true,
    group: 'main',
    order: 1,
  });


  readonly centrifugo = this.route('/private/centrifugo', {
    label: 'Centrifugo',
    description: 'Real-time messaging and monitoring',
    icon: Radio,
    protected: true,
    group: 'system',
    order: 2,
  });

  readonly profile = this.route('/private/profile', {
    label: 'Profile',
    description: 'User profile and settings',
    icon: User,
    protected: true,
    group: 'account',
    order: 1,
  });

  readonly ui = this.route('/private/ui', {
    label: 'UI Components',
    description: 'Component showcase and documentation',
    icon: Palette,
    protected: true,
    group: 'development',
    order: 1,
  });

}

// ─────────────────────────────────────────────────────────────────────────
// Routes Container
// ─────────────────────────────────────────────────────────────────────────

export class BitAPIRoutes {
  readonly public = new PublicRoutes();
  readonly private = new PrivateRoutes();

  getAllRoutes(): RouteDefinition[] {
    return [
      ...this.public.getAllRoutes(),
      ...this.private.getAllRoutes(),
    ];
  }

  getRouteByPath(path: string): RouteDefinition | undefined {
    return this.getAllRoutes().find(r => r.path === path);
  }

  getRouteLabel(path: string): string {
    const route = this.getRouteByPath(path);
    return route?.metadata.label || 'BitAPI';
  }

  getRouteDescription(path: string): string | undefined {
    return this.getRouteByPath(path)?.metadata.description;
  }

  isRouteProtected(path: string): boolean {
    const route = this.getRouteByPath(path);
    return route?.metadata.protected ?? true;
  }
}
