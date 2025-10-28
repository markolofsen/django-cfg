/**
 * _error.tsx - Universal Error Handler
 *
 * Ultra-minimal setup using ErrorLayout utilities
 * Everything is configured automatically!
 */

import { settings } from '@/core';
import { ErrorLayout, errorPageGetInitialProps } from '@djangocfg/layouts';

interface ErrorProps {
  statusCode?: number;
}

function ErrorPage({ statusCode }: ErrorProps) {
  return <ErrorLayout code={statusCode} supportEmail={settings.contact.email} />;
}

// Use ready-made getInitialProps from ErrorLayout
ErrorPage.getInitialProps = errorPageGetInitialProps;

export default ErrorPage;
