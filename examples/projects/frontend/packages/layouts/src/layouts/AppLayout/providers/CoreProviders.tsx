/**
 * Core Providers
 *
 * Wraps application with all necessary providers
 */

'use client';

import React, { ReactNode } from 'react';
import { ThemeProvider, Toaster } from '@djangocfg/ui';
import { AuthProvider } from '../../../auth';
import type { AppLayoutConfig } from '../types';

export interface CoreProvidersProps {
  children: ReactNode;
  config: AppLayoutConfig;
}

/**
 * Core Providers Wrapper
 *
 * Provides:
 * - ThemeProvider (dark/light mode)
 * - AuthProvider (authentication)
 * - Toaster (notifications)
 */
export function CoreProviders({ children, config }: CoreProvidersProps) {
  return (
    <ThemeProvider>
      <AuthProvider
        config={{
          apiUrl: config.api.baseUrl,
          routes: {
            auth: config.routes.auth,
            defaultCallback: config.routes.defaultCallback,
            defaultAuthCallback: config.routes.defaultAuthCallback || config.routes.defaultCallback,
          },
        }}
      >
        {children}
      </AuthProvider>

      {/* Global toast notifications */}
      <Toaster />
    </ThemeProvider>
  );
}
