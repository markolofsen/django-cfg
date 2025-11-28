/**
 * 500 Page - Server Error
 *
 * Minimal setup - just pass the error code!
 * ErrorLayout handles everything automatically
 */

import { settings } from '@/core';
import { ErrorLayout } from '@djangocfg/layouts';

export default function ServerErrorPage() {
  return <ErrorLayout code={500} supportEmail={settings.contact.email} />;
}
