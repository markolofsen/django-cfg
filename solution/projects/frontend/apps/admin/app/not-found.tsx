import { ErrorLayout } from '@djangocfg/layouts/components';

import { settings } from './_core';

export default function NotFound() {
  return <ErrorLayout code={404} supportEmail={settings.contact.email} />;
}

