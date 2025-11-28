/**
 * Public Routes
 *
 * Routes accessible without authentication
 */

import { LayoutDashboard, LogIn, Shield, FileText, Cookie, Mail } from 'lucide-react';
import { defineRoute } from '../shared';

export const home = defineRoute('/', {
  label: 'Home',
  description: 'Dashboard home',
  icon: LayoutDashboard,
  protected: false,
  group: 'main',
  order: 1,
});

export const demo = defineRoute('/demo', {
  label: 'Admin Demo',
  description: 'Admin interface demo',
  icon: LayoutDashboard,
  protected: false,
  group: 'demo',
  order: 2,
});

export const auth = defineRoute('/auth', {
  label: 'Sign In',
  description: 'User authentication',
  icon: LogIn,
  protected: false,
});

export const privacy = defineRoute('/legal/privacy', {
  label: 'Privacy Policy',
  description: 'Privacy policy and data protection',
  icon: Shield,
  protected: false,
  group: 'legal',
  order: 1,
});

export const terms = defineRoute('/legal/terms', {
  label: 'Terms of Service',
  description: 'Terms and conditions',
  icon: FileText,
  protected: false,
  group: 'legal',
  order: 2,
});

export const cookies = defineRoute('/legal/cookies', {
  label: 'Cookie Policy',
  description: 'Cookie usage and preferences',
  icon: Cookie,
  protected: false,
  group: 'legal',
  order: 3,
});

export const security = defineRoute('/legal/security', {
  label: 'Security Policy',
  description: 'Security practices and policies',
  icon: Shield,
  protected: false,
  group: 'legal',
  order: 4,
});

// Contact
export const contact = defineRoute('/contact', {
  label: 'Contact',
  description: 'Get in touch with us',
  icon: Mail,
  protected: false,
  group: 'contact',
  order: 1,
});

// All routes as array
export const allRoutes = [home, ui, demo, auth, privacy, terms, cookies, security, contact];
