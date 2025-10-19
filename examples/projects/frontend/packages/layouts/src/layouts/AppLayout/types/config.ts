/**
 * Configuration Types
 */

import type { ReactNode } from 'react';
import type { PublicLayoutConfig, PrivateLayoutConfig } from './layout';
import type { RouteConfig } from './routes';

/**
 * Main AppLayout configuration
 */
export interface AppLayoutConfig {
  /** Application metadata */
  app: {
    name: string;
    description?: string;
    logoPath: string;
    siteUrl?: string;
    icons?: {
      logo192?: string;
      logo384?: string;
      logo512?: string;
      logoVector?: string;
    };
  };

  /** API configuration */
  api: {
    baseUrl: string;
  };

  /** Route configuration */
  routes: RouteConfig;

  /** Public layout configuration */
  publicLayout: PublicLayoutConfig;

  /** Private layout configuration */
  privateLayout: PrivateLayoutConfig;

  /** Error handling configuration */
  errors?: {
    /** Enable automatic error boundary (default: true) */
    enableErrorBoundary?: boolean;
    /** Support email for error pages */
    supportEmail?: string;
    /** Custom error handler callback */
    onError?: (error: Error, errorInfo?: React.ErrorInfo) => void;
  };

  /** Auth configuration */
  auth?: {
    /** Terms of Service URL */
    termsUrl?: string;
    /** Privacy Policy URL */
    privacyUrl?: string;
    /** Support URL for auth help */
    supportUrl?: string;
    /** Enable phone authentication (default: false) */
    enablePhoneAuth?: boolean;
  };
}
