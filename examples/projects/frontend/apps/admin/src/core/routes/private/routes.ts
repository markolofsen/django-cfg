/**
 * User Routes
 *
 * Routes for authenticated users
 * Path prefix: /private
 */

import { LayoutDashboard, Palette, User, CreditCard, LifeBuoy } from 'lucide-react';
import { defineRoute } from '../shared';
import { isDevelopment } from '@/core/settings';

export const home = defineRoute('/private', {
  label: 'Home',
  description: 'Dashboard home',
  icon: LayoutDashboard,
  protected: true,
  group: 'main',
  order: 1,
});

export const payments = defineRoute('/private/payments', {
  label: 'Payments',
  description: 'Payment methods and billing',
  icon: CreditCard,
  protected: true,
  group: 'main',
  order: 2,
});

export const support = defineRoute('/private/support', {
  label: 'Support',
  description: 'Help and support center',
  icon: LifeBuoy,
  protected: true,
  group: 'main',
  order: 3,
});

export const profile = defineRoute('/private/profile', {
  label: 'Profile',
  description: 'User profile and settings',
  icon: User,
  protected: true,
  group: 'account',
  order: 1,
});

export const ui = defineRoute('/private/ui', {
  label: 'UI Components',
  description: 'Component showcase and documentation',
  icon: Palette,
  protected: true,
  group: 'development',
  order: 1,
  show: isDevelopment,  // Only in development
});

// All routes as array
export const allRoutes = [home, payments, support, profile, ui];
