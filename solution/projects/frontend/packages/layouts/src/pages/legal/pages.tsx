/**
 * Pre-built legal page components
 *
 * Ready-to-use page components with default configurations
 * Can be customized by passing custom config
 *
 * Usage:
 * ```tsx
 * // app/legal/privacy/page.tsx
 * import { PrivacyPage } from '@djangocfg/layouts/components/legal';
 *
 * export default PrivacyPage;
 * ```
 */

'use client';

import { cookiesConfig, privacyConfig, securityConfig, termsConfig } from './configs';
import { LegalPage } from './LegalPage';

import type { LegalPageConfig } from './types';

export interface LegalPageComponentProps {
  config?: LegalPageConfig;
}

/**
 * Privacy Policy Page
 */
export function PrivacyPage({ config }: LegalPageComponentProps = {}) {
  return <LegalPage config={config || privacyConfig} />;
}

/**
 * Terms of Service Page
 */
export function TermsPage({ config }: LegalPageComponentProps = {}) {
  return <LegalPage config={config || termsConfig} />;
}

/**
 * Cookie Policy Page
 */
export function CookiesPage({ config }: LegalPageComponentProps = {}) {
  return <LegalPage config={config || cookiesConfig} />;
}

/**
 * Security Policy Page
 */
export function SecurityPage({ config }: LegalPageComponentProps = {}) {
  return <LegalPage config={config || securityConfig} />;
}

