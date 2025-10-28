/**
 * Admin Routes
 *
 * Routes for administrative functions
 * Path prefix: /admin
 */

import { LayoutDashboard, Bitcoin, TrendingUp } from 'lucide-react';
import { defineRoute } from '../shared';

export const overview = defineRoute('/admin', {
  label: 'Overview',
  description: 'Dashboard overview',
  icon: LayoutDashboard,
  protected: true,
  group: 'main',
  order: 1,
});

export const crypto = defineRoute('/admin/crypto', {
  label: 'Cryptocurrency',
  description: 'Manage cryptocurrency data and wallets',
  icon: Bitcoin,
  protected: true,
  group: 'main',
  order: 2,
});

export const trading = defineRoute('/admin/trading', {
  label: 'Trading',
  description: 'Manage trading portfolio and orders',
  icon: TrendingUp,
  protected: true,
  group: 'main',
  order: 3,
});

// All routes as array
export const allRoutes = [overview, crypto, trading];
