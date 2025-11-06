/**
 * Admin Routes
 *
 * Routes for administrative functions
 * Path prefix: /admin
 */

import { LayoutDashboard, Bitcoin, TrendingUp, Terminal, Zap, Radio, ListChecks } from 'lucide-react';
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

// Placeholder routes for compatibility (not implemented in solution project)
export const commands = defineRoute('/admin/commands', {
  label: 'Commands',
  description: 'Management commands',
  icon: Terminal,
  protected: true,
  group: 'admin',
  order: 4,
});

export const grpc = defineRoute('/admin/grpc', {
  label: 'gRPC',
  description: 'gRPC status',
  icon: Zap,
  protected: true,
  group: 'admin',
  order: 5,
});

export const centrifugo = defineRoute('/admin/centrifugo', {
  label: 'Centrifugo',
  description: 'WebSocket status',
  icon: Radio,
  protected: true,
  group: 'admin',
  order: 6,
});

export const rq = defineRoute('/admin/rq', {
  label: 'RQ',
  description: 'Task queue status',
  icon: ListChecks,
  protected: true,
  group: 'admin',
  order: 7,
});

// All routes as array
export const allRoutes = [overview, crypto, trading, commands, grpc, centrifugo, rq];
