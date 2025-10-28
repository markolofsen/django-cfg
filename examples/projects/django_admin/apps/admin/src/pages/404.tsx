/**
 * 404 Page - Not Found
 *
 * Ultra-minimal - just error code!
 * Title, description, icon auto-configured
 */

import { settings } from '@/core';
import { ErrorLayout } from '@djangocfg/layouts';

export default function NotFoundPage() {
  return <ErrorLayout code={404} supportEmail={settings.contact.email} />;
}
